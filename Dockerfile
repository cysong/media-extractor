FROM public.ecr.aws/lambda/python:3.13

# Install ffmpeg via static binary (Amazon Linux 2023 default repos do not include ffmpeg)
RUN dnf install -y tar xz && \
    curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
    | tar -xJ --strip-components=1 -C /usr/local/bin --wildcards '*/ffmpeg' && \
    chmod +x /usr/local/bin/ffmpeg && \
    dnf clean all

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["handler.lambda_handler"]
