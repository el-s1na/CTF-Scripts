# NOTE: This hash is pinned to avoid version and environment differences.
FROM ubuntu:24.04@sha256:e21f810fa78c09944446ec02048605eb3ab1e4e2e261c387ecc7456b38400d79
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && \
    apt-get -y install xinetd && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r pwn && \
    useradd -r -g pwn -d /home/pwn pwn


RUN cat > /etc/xinetd.d/pwn << 'EOF'
service pwn
{
  type           = UNLISTED
  disable        = no
  socket_type    = stream
  protocol       = tcp
  wait           = no
  user           = pwn
  bind           = 0.0.0.0
  port           = 1337
  server         = /usr/bin/timeout
  server_args    = 180 /home/pwn/chal
}
EOF

RUN chmod 444 /etc/xinetd.d/pwn
WORKDIR /home/pwn
COPY --chmod=550 chal .
COPY --chmod=444 flag.txt /flag.txt
RUN chown -R root:pwn /home/pwn

EXPOSE 1337
CMD ["xinetd", "-dontfork"]
