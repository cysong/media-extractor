#!/usr/bin/env bash
# setup-aws.sh — provision all AWS resources for media-extractor
# Prerequisites: aws CLI configured, docker running
# Usage: bash scripts/setup-aws.sh

set -euo pipefail

# ── Config (edit these before running) ───────────────────────────────────────
APP_NAME="media-extractor"
AWS_REGION="${AWS_REGION:-ap-southeast-2}"
DYNAMODB_TABLE="media-extractor-records"
LAMBDA_TIMEOUT=60
LAMBDA_MEMORY=512
# ─────────────────────────────────────────────────────────────────────────────

log() { echo "[$(date +%H:%M:%S)] $*"; }

# Resolve account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
ECR_REPOSITORY="$APP_NAME"
LAMBDA_FUNCTION_NAME="$APP_NAME"
IAM_ROLE_NAME="${APP_NAME}-lambda-role"
IMAGE_URI="$ECR_REGISTRY/$ECR_REPOSITORY:latest"

log "Account : $AWS_ACCOUNT_ID"
log "Region  : $AWS_REGION"
log "Image   : $IMAGE_URI"
echo ""

# ── 1. ECR ───────────────────────────────────────────────────────────────────
log "1/6  Creating ECR repository..."
aws ecr describe-repositories --repository-names "$ECR_REPOSITORY" \
    --region "$AWS_REGION" &>/dev/null \
  || aws ecr create-repository \
        --repository-name "$ECR_REPOSITORY" \
        --region "$AWS_REGION" \
        --output table

# ── 2. Build & push image ────────────────────────────────────────────────────
log "2/6  Building and pushing Docker image..."
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$ECR_REGISTRY"

docker build -t "$APP_NAME" .
docker tag "$APP_NAME:latest" "$IMAGE_URI"
docker push "$IMAGE_URI"

# ── 3. DynamoDB ──────────────────────────────────────────────────────────────
log "3/6  Creating DynamoDB table..."
aws dynamodb describe-table --table-name "$DYNAMODB_TABLE" \
    --region "$AWS_REGION" &>/dev/null \
  || aws dynamodb create-table \
        --table-name "$DYNAMODB_TABLE" \
        --attribute-definitions AttributeName=id,AttributeType=S \
        --key-schema AttributeName=id,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region "$AWS_REGION" \
        --output table

# ── 4. IAM Role ──────────────────────────────────────────────────────────────
log "4/6  Creating IAM role..."

TRUST_POLICY='{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "lambda.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}'

ROLE_ARN=$(aws iam get-role --role-name "$IAM_ROLE_NAME" \
    --query 'Role.Arn' --output text 2>/dev/null) \
  || ROLE_ARN=$(aws iam create-role \
        --role-name "$IAM_ROLE_NAME" \
        --assume-role-policy-document "$TRUST_POLICY" \
        --query 'Role.Arn' --output text)

# Basic Lambda execution (CloudWatch logs)
aws iam attach-role-policy \
  --role-name "$IAM_ROLE_NAME" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# DynamoDB write access
DYNAMODB_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:Scan"
    ],
    "Resource": "arn:aws:dynamodb:$AWS_REGION:$AWS_ACCOUNT_ID:table/$DYNAMODB_TABLE"
  }]
}
EOF
)

aws iam put-role-policy \
  --role-name "$IAM_ROLE_NAME" \
  --policy-name "${APP_NAME}-dynamodb" \
  --policy-document "$DYNAMODB_POLICY"

log "    Role ARN: $ROLE_ARN"

# Wait for role to propagate
log "    Waiting 10s for IAM role to propagate..."
sleep 10

# ── 5. Lambda ─────────────────────────────────────────────────────────────────
log "5/6  Creating Lambda function..."

if aws lambda get-function --function-name "$LAMBDA_FUNCTION_NAME" \
    --region "$AWS_REGION" &>/dev/null; then
  aws lambda update-function-code \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --image-uri "$IMAGE_URI" \
    --region "$AWS_REGION" \
    --output table
else
  aws lambda create-function \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --package-type Image \
    --code ImageUri="$IMAGE_URI" \
    --role "$ROLE_ARN" \
    --timeout "$LAMBDA_TIMEOUT" \
    --memory-size "$LAMBDA_MEMORY" \
    --environment "Variables={DYNAMODB_TABLE=$DYNAMODB_TABLE}" \
    --region "$AWS_REGION" \
    --output table

  log "    Waiting for function to become active..."
  aws lambda wait function-active \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --region "$AWS_REGION"
fi

LAMBDA_ARN=$(aws lambda get-function \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --region "$AWS_REGION" \
  --query 'Configuration.FunctionArn' --output text)

# ── 6. API Gateway ────────────────────────────────────────────────────────────
log "6/6  Creating API Gateway HTTP API..."

API_ID=$(aws apigatewayv2 get-apis --region "$AWS_REGION" \
  --query "Items[?Name=='$APP_NAME'].ApiId" --output text)

if [ -z "$API_ID" ]; then
  API_ID=$(aws apigatewayv2 create-api \
    --name "$APP_NAME" \
    --protocol-type HTTP \
    --region "$AWS_REGION" \
    --query 'ApiId' --output text)
fi

# Lambda integration
INTEGRATION_ID=$(aws apigatewayv2 create-integration \
  --api-id "$API_ID" \
  --integration-type AWS_PROXY \
  --integration-uri "$LAMBDA_ARN" \
  --payload-format-version "2.0" \
  --region "$AWS_REGION" \
  --query 'IntegrationId' --output text)

# POST /get-media route
aws apigatewayv2 create-route \
  --api-id "$API_ID" \
  --route-key "POST /get-media" \
  --target "integrations/$INTEGRATION_ID" \
  --region "$AWS_REGION" \
  --output table

# Auto deploy stage
aws apigatewayv2 create-stage \
  --api-id "$API_ID" \
  --stage-name '$default' \
  --auto-deploy \
  --region "$AWS_REGION" \
  --output table 2>/dev/null || true

# Allow API Gateway to invoke Lambda
aws lambda add-permission \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --statement-id "apigateway-invoke" \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:$AWS_REGION:$AWS_ACCOUNT_ID:$API_ID/*/*/get-media" \
  --region "$AWS_REGION" \
  --output table 2>/dev/null || true

API_ENDPOINT="https://$API_ID.execute-api.$AWS_REGION.amazonaws.com/get-media"

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo "  Setup complete"
echo "========================================"
echo ""
echo "API endpoint:"
echo "  POST $API_ENDPOINT"
echo ""
echo "Add these to GitHub Secrets:"
echo "  AWS_ACCESS_KEY_ID     = <your key>"
echo "  AWS_SECRET_ACCESS_KEY = <your secret>"
echo "  AWS_REGION            = $AWS_REGION"
echo "  ECR_REPOSITORY        = $ECR_REPOSITORY"
echo "  LAMBDA_FUNCTION_NAME  = $LAMBDA_FUNCTION_NAME"
echo ""
echo "Test:"
echo "  curl -X POST $API_ENDPOINT \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"url\": \"https://x.com/NASA/status/1\"}'"
