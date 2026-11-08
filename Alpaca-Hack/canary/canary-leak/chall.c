// gcc chall.c -o chall -fstack-protector -O0
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

void vuln(){
    unsigned long *canary;
    unsigned long canary_saved;
    unsigned long input;
    char buf[64];

    canary = (unsigned long *)(buf + 0xc8);
    canary_saved = *canary;

    puts("Input:");
    read(0, buf, 0xcf);
    
    puts("Output:");
    puts(buf);

    puts("Canary?");
    read(0, &input, 8);

    if(canary_saved == input){
        FILE *fp = fopen("flag.txt","r");
            char flag[128];
            fgets(flag, sizeof(flag), fp);
            puts(flag);
    }else{
        puts("Nope");
    }
}

int main(){
    setvbuf(stdout,NULL,_IONBF,0);
    setvbuf(stdin,NULL,_IONBF,0);

    vuln();
}