#include <stdio.h>
#include <stdlib.h>

void alpaca_function0() { puts("Alpaca Function 0."); }

void alpaca_function1() { puts("Alpaca Function 1. 🦙"); }

void alpaca_function2() { puts("Alpaca Function 2. 🦙🦙"); }

void win() {
  asm volatile("mov $0,%spl");
  puts("You Win! 🦙🦙🦙🦙🦙");
  system("/bin/sh");
  exit(0);
}

void vuln() {
  void (*alpaca_functions[3])() = {
      alpaca_function0, alpaca_function1,
      alpaca_function2}; // array of function pointers

  unsigned int choice;
  printf("Select an alpaca function index: ");
  scanf("%u", &choice); // no bounds check

  alpaca_functions[choice]();

  exit(0); // this does not get called->just point to rbp
}

int main() {
  setvbuf(stdin, NULL, _IONBF, 0);
  setvbuf(stdout, NULL, _IONBF, 0);

  vuln();

  win();

  return 0;
}
