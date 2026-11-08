#include <stdio.h>
#include <stdlib.h>

int main(void) {
    char buf[0x80] = {0};
    printf("printf @ %p\n", (void *)printf);
    void (*f_ptr)(void *);
    printf("Enter the address> ");
    scanf("%p%*c", (void **)&f_ptr);
    f_ptr(NULL);
}

__attribute__((constructor))
void setup() {
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
}