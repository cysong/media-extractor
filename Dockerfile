FROM public.ecr.aws/lambda/python:3.12

# Install ffmpeg via static binary (Amazon Linux 2023 default repos do not include ffmpeg)
RUN curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
    | tar -xJ --strip-components=1 -C /usr/local/bin --wildcards '*/ffmpeg' \
    && chmod +x /usr/local/bin/ffmpeg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["handler.lambda_handler"]
