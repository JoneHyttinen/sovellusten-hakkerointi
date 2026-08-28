#include "stdio.h"

void print_scrambled(const char *message)
{
  int i = 0;
  do {
    printf("%c", (*message)+i);
  } while (*++message);
  printf("\n");
}

int main()
{
  const char * good_message = "Hello, world.";

  print_scrambled(good_message);
}

