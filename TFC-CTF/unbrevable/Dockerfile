FROM ubuntu:22.04

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libseccomp2 \
        socat \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY vuln_patched ld-2.35.so libc-2.35.so libc.so.6 flag ./

RUN chmod 0555 vuln_patched ld-2.35.so libc-2.35.so \
    && chmod 0444 flag

USER 65534:65534

EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:./vuln_patched,stderr"]
