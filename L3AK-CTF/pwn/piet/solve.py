#!/usr/bin/python3
from pwn import *
from sys import argv

elf = context.binary = ELF("./chall_patched")
libc = ELF("./libc.so.6", checksec=False)
ld = ELF("./ld-linux-x86-64.so.2", checksec=False)
io = process()
#  -> 0x5555555569c5 e8f6f9ffff            <load_png+0xeb>   call   0x5555555563c0

#    -> 0x5555555563c0 f30f1efa              <NO_SYMBOL>   endbr64
#       0x5555555563c4 ff25ce4b0000          <NO_SYMBOL>   jmp    QWORD PTR [rip + 0x4bce] # 0x55555555af98 <png_init_io@got[plt]>
#       0x5555555563ca 660f1f440000          <NO_SYMBOL>   nop    WORD PTR [rax + rax * 1 + 0x0]
#       0x5555555563d0 f30f1efa              <NO_SYMBOL>   endbr64
#       0x5555555563d4 ff25c64b0000          <NO_SYMBOL>   jmp    QWORD PTR [rip + 0x4bc6] # 0x55555555afa0 <calloc@got[plt]>
#       0x5555555563da 660f1f440000          <NO_SYMBOL>   nop    WORD PTR [rax + rax * 1 + 0x0]


io.interactive()
