cc=gcc
cflags= -Wall -std=c99
ftmarco= -fno-stack-protector
debug = -g
buggy:
	$(cc) -o buggy_program $(cflags) buggy_program.c $(debug)

.PHONY: clean
clean:
	rm -f buggy_program

