FROM ubuntu:22.04@sha256:3ba65aa20f86a0fad9df2b2c259c613df006b2e6d0bfcc8a146afb8c525a9751

RUN apt-get update && \
    apt-get install -y socat

WORKDIR /app
COPY flag.txt ./
COPY --chmod=555 chall ./

RUN useradd -m ctf
USER ctf

CMD ["socat", "-T30", "tcp-listen:9999,fork,reuseaddr", "exec:/app/chall"]
