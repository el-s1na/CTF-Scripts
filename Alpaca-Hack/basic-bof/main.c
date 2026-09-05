// gcc -o chal main.c -fno-stack-protector -O0

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// You don't have to care about this function
__attribute__((constructor)) void setup() {
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
}

/*
** How to get the address of `win` **

  $ nm chal | grep win
  XXXXXXXXX

This address is **NOT fixed** across executions, because the challenge binary
`chal` is compiled WITHOUT -fno-pie (i.e., without position-independent code).
*/
void win() {
    execve("/bin/sh", NULL, NULL);
}

int main(void) {
    printf("address of main function: %p\n", main);
    char buffer[64];
    printf("input > ");
    gets(buffer);
    return 0;
}
