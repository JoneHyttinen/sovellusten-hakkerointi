#include <stddef.h>
#include <stdio.h>
#include <string.h>

int main() {
  char pw[20];
  char key[10];

  printf("Give the password to obfuscate (Max 20 characters): ");
  scanf("%s", pw);

  printf("Give a key to obfuscate with (Max 10 characters): ");
  scanf("%s", key);

  size_t keylen = strlen(key);

  printf("Your obfuscated password: ");
  for (size_t i = 0; i < strlen(pw); i++) {
    printf("0x%02X, ", (unsigned char)pw[i] ^ key[i % keylen]);
  }
}
