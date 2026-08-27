#include <stdio.h>

void buggy_function(int *arr, int size) {
    for (int i = 0; i <= size; i++) { // Huomaa: <= aiheuttaa puskuriylivuodon
        printf("Element %d: %d\n", i, arr[i]);
    }
}

int main() {
    int numbers[] = {1, 2, 3, 4, 5};
    buggy_function(numbers, 4); // Virheellinen koko
    return 0;
}
