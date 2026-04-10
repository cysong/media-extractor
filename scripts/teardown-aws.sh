#!/usr/bin/env bash
# teardown-aws.sh — remove all AWS resources created by setup-aws.sh
# Usage: bash scripts/teardown-aws.sh

set -euo pipefail

APP_NAME="media-extractor"
AWS_REGION="${AWS_REGION:-ap-southeast-2}"
DYNAMODB_TABLE="media-extractor-records"
IAM_ROLE_NAME="${APP_NAME}-lambda-role"

log() { echo "[$(date +%H:%M:%S)] $*"; }

echo "This will delete: Lambda, API Gateway, ECR, DynamoDB table, IAM role."
read -r -p "Continue? (yes/no): " confirm
[ "$confirm" = "yes" ] || { echo "Aborted."; exit 0; }

# Lambda
log "Deleting Lambda function..."
aws lambda delete-function --function-name "$APP_NAME" \
  --region "$AWS_REGION" 2>/dev/null && log "  Done." || log "  Not found, skipping."

# API Gateway
log "Deleting API Gateway..."
API_ID=$(aws apigatewayv2 get-apis --region "$AWS_REGION" \
  --query "Items[?Name=='$APP_NAME'].ApiId" --output text)
if [ -n "$API_ID" ]; then
  aws apigatewayv2 delete-api --api-id "$API_ID" --region "$AWS_REGION"
  log "  Done."
else
  log "  Not found, skipping."
fi

# DynamoDB
log "Deleting DynamoDB table..."
aws dynamodb delete-table --table-name "$DYNAMODB_TABLE" \
  --region "$AWS_REGION" 2>/dev/null && log "  Done." || log "  Not found, skipping."

# ECR
log "Deleting ECR repository..."
aws ecr delete-repository --repository-name "$APP_NAME" \
  --region "$AWS_REGION" --force 2>/dev/null && log "  Done." || log "  Not found, skipping."

# IAM
log "Deleting IAM role..."
aws iam detach-role-policy \
  --role-name "$IAM_ROLE_NAME" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole 2>/dev/null || true
aws iam delete-role-policy \
  --role-name "$IAM_ROLE_NAME" \
  --policy-name "${APP_NAME}-dynamodb" 2>/dev/null || true
aws iam delete-role --role-name "$IAM_ROLE_NAME" \
  2>/dev/null && log "  Done." || log "  Not found, skipping."

echo ""
echo "Teardown complete."
