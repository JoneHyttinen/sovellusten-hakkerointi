#include <stddef.h>
#include <stdio.h>
#include <string.h>

int main() {
  char guess[50];
  unsigned char stored[] = {0x07, 0x03, 0x0D, 0x1E, 0x16, 0x1D, 0x0B, 0x39,
                            0x00, 0x18, 0x04, 0x0D, 0x39, 0x40, 0x47, 0x5C};
  const unsigned char key[] = {0x6F, 0x62, 0x66, 0x75, 0x73};

  printf("What's the password?\n");
  scanf("%19s", guess);

  int match = 1;
  for (size_t i = 0; i < sizeof(stored); i++) {
    if (((unsigned char)guess[i] ^ key[i % sizeof(key)]) != stored[i]) {
      match = 0;
      break;
    }
  }
  if (match) {
    printf("Yes! That's the password. "
           "FLAG{Tero-d75ee66af0a68663f15539ec0f46e3b1}\n");
  } else {
    printf("Sorry, no bonus.\n");
  }
  return 0;
}
