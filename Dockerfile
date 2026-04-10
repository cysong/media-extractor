FROM public.ecr.aws/lambda/python:3.12

# Install ffmpeg for audio/video merging
RUN dnf install -y ffmpeg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["handler.lambda_handler"]
