FROM public.ecr.aws/lambda/python:3.13

# Install ffmpeg static binary for audio/video format merging
# Download to /tmp first to avoid pipe exit code masking
RUN dnf install -y tar xz && \
    curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
        -o /tmp/ffmpeg.tar.xz && \
    tar -xJf /tmp/ffmpeg.tar.xz \
        --strip-components=1 \
        --wildcards \
        -C /var/task \
        '*/ffmpeg' && \
    rm /tmp/ffmpeg.tar.xz && \
    dnf clean all

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["handler.lambda_handler"]
