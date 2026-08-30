## lab0

Alkuperäinen koodi on virheellinen, koska funktiota kutsuessa koko on 5, kun oikeasti taulukon viimeisen arvon indeksi on 4, koska taulukko alkaa 0:sta.

![alkuperäinen koodi](./kuvakoodista1.png)

Korjasin koodin vaihtamalla buggy_functionissa olevan loopin lopetusehdon <=:stä pelkkään <.

![korjattu funktio](./korjattukoodi.png)

## lab1

## lab2

## lab3

Ratkaisin tähän osioon `crackme05` ohjelman.

Ensimmäisenä voimme tarkastella main funktion ohjeita 'disassemble main' komennolla.

Me näämme main funktion ohjeista, että salasanan pituuden täytyy olla 16 merkkiä.

```
call strnlen
cmp $0x10, %eax // vertaa string pituutta kuuteentoista
jne fail
```

Toinen salasanan vaatimus on, että 2 indeksin arvon täytyy olla 'B' kirjain.

```
cmpb $0x42, 0x2(%rbx) ; 0x42 = 'B' ASCII:ssa.
```

Kolmas vaatimus salasanalle on, että  13 indeksin arvon täytyy olla 'Q' kirjain.

```
cmpb $0x51, 0xd(%rbx) ; 0x51 = 'Q' ASCII:ssa.
```

Salasanan oletettu layout on nyt:

0 1 2 3 4 5 6 7 8 9 A B C D E F
? ? B ? ? ? ? ? ? ? ? ? ? Q ? ?

Voimme ymmärtää miten check_with_mod funktiota hyödynnetään ohjelmassa tarkastelemalla sen kutsuja main funktiossa.

![main](./mainfunktiossacheck_with_modlab3.png)

```
mov %rbx,%rdi      ; pointer into password
mov $0x4,%esi      ; length
mov $0x3,%edx      ; modulus?
call check_with_mod
```

```
lea 0x4(%rbx),%rdi
mov $4,%esi
mov $4,%edx
call check_with_mod
```

```
lea 0x8(%rbx),%rdi
mov $4,%esi
mov $5,%edx
call check_with_mod
```

```
lea 0xc(%rbx),%rdi
mov $4,%esi
mov $4,%edx
call check_with_mod
```

Tämä jakaa salasanan neljään osioon:

| Block | Characters | Arguments |
| --------------- | --------------- | --------------- |
| 1 | password[0..3] | check_with_mod(ptr, 4, 3) |
| 2 | password[4..7] | check_with_mod(ptr, 4, 4) |
| 3 | password[8..11] | check_with_mod(ptr, 4, 5) |
| 4 | password[12..15] | check_with_mod(ptr, 4, 4) |

Seuraavaksi voimme tarkastella itse check_with_mod funktiota 'disassemble check_with_mod' komennolla.

![check_with_mod](./check_with_modfunktiolab3.png)
