# passtr - a simple static analysis warm up exercise

Copyright 2024 Tero Karvinen https://TeroKarvinen.com

Prerequisites

	$ sudo apt-get update
	$ sudo apt-get install make gcc micro

Run

	$ ./passtr

To edit and compile the source code

	$ micro passtr.c
	$ make
	$ ./passtr

The binary is already compiled for regular PC's aka amd64. If you've got an arm64 (Raspberry Pi or Mac M1, M2, M3 or M4), try recompiling it ('make clean; make'). 

