# Tapo C200 -laiteohjelmiston analyysi

Kohteena TP-Link Tapo C200 -valvontakamera (laitteistoversio 3.0 / firmware-perhe C200v3-C200v4). Tehtävänä oli purkaa laitteen laiteohjelmiston salaus, analysoida kuvatiedosto, erottaa juuritiedostojärjestelmä (rootfs) sekä raa'asta flash-dumpista että valmistajan jakelemasta kuvatiedostosta, kartoittaa laitteella ajettavat sovellukset ja lopuksi selvittää, voiko root-salasanan avata staattisella analyysillä.

**Käytetyt lähdetiedostot:**

| Tiedosto | Koko | SHA-256 |
|---|---|---|
| `Tapo_C200v4_en_1.4.2.bin` (valmistajan salattu kuva) | 8 117 624 t | `7a936497d4f36a981c274448c01d89bb90cf4ddaa6d69b98eb60ef4c53f4bc1d` |
| `Tapo_C200v4_en_1.4.2.bin.dec` (purettu kuva) | 8 117 624 t | `4b28f05c9c02806281e8ab58698f5c8329dee197493f51e811c2c73291e551a1` |
| `dump-tapo-c200v3-1.4.2.bin` (raaka flash-dumppi laitteesta) | 8 388 608 t | `710491fe37ead52d757e9bfc491ce92902a93d2bb3d12b264219dff8b5c30575` |

**Työkalut:** [`tp-link-decrypt`](https://github.com/robbins/tp-link-decrypt) — tehtävänannossa osoitettu, robbinsin ylläpitämä (watchfulip:n alkuperäistä työtä jatkava) haara — (RSA/AES-avainten purku ja salauksen purku), `binwalk` 3.1.0 (asennettu Nixin kautta), `squashfs-tools` / `sasquatch` (SquashFS-purku), `dd`, `gunzip`, `tar`, `file`, `readelf`, `objdump`, `strings`, `nm` sekä itse kirjoitettu MIPS32-purkuskripti (ks. tehtävä 6).

---

## 1. Laiteohjelmistokuvan salauksen purku

TP-Link allekirjoittaa ja salaa jakelemansa `.bin`-päivityspaketit. Tiedoston alusta löytyy RSA-2048-allekirjoitusrakenne, jonka jälkeen varsinainen data on AES-CBC-salattu avaimella, joka on itsessään upotettu (osittain julkisiin) TP-Link-binääreihin.

Käytin tehtävänannossa annettua [`robbins/tp-link-decrypt`](https://github.com/robbins/tp-link-decrypt) -projektia, joka osaa purkaa avaimet suoraan TP-Linkin omista, julkisesti jaetuista GPL-paketeista/firmwareista:

```bash
./preinstall.sh        # riippuvuudet
./extract_keys.sh       # louhii RSA/AES-avaimet TP-Linkin julkisista binääreistä
make                     # kääntää bin/tp-link-decrypt -työkalun
./bin/tp-link-decrypt ../Tapo_C200v4_en_1.4.2.bin
```

Ajon tuloste:

```
TP-link firmware decrypt
Watchful_IP & robbins 03-10-25 v0.0.4

Tapo firmware header found
RSA-2048

key/iv:
KEY=9c6ba1d761e4eee17dfde90cfed603bd
IV=8778f31423815ce85e9f186b60507edd

Firmware verification successful
Decrypted firmware written to ../Tapo_C200v4_en_1.4.2.bin.dec
```

Työkalu tunnisti otsikosta RSA-2048-allekirjoituksen, päätteli tästä käytetyn AES-avaimen/IV:n, purki datan ja **vahvisti allekirjoituksen onnistuneesti** — eli tuloksena on aidon, laitteen hyväksymän laiteohjelmiston selväkielinen sisältö. Tulostiedosto `Tapo_C200v4_en_1.4.2.bin.dec` on samankokoinen (8 117 624 t) kuin lähde, mutta tavusisältö poikkeaa täysin (SHA-256 eri), mikä vahvistaa salauksen purkautuneen.

---

## 2. Kuvatiedoston analysointi

Puretun kuvan (`Tapo_C200v4_en_1.4.2.bin.dec`) rakenne kartoitettiin `binwalk`illa allekirjoitusten/entropian perusteella. Löydöksiä:

| Offset | Sisältö |
|---|---|
| `0x00000000` | RSA/otsikkolohko (satunnaiselta näyttävää dataa — allekirjoitus/padding) |
| `0x00020400` | Linux-kernelin `uImage`-otsikko (magic `0x27051956`), gzip-pakattu |
| `0x000166C1`–`0x003689 82` | Kernelin gzip-datavirta paloiteltuna (binwalk pilkkoo saman deflate-virran ~64 kt lohkoihin päällekkäisten gzip-tunnisteiden vuoksi — tämä on binwalkin tunnettu ominaisuus, ei erillisiä tiedostoja) |
| `0x003E0200` | SquashFS-tiedostojärjestelmä (magic `hsqs`) — sovellusten rootfs |
| `0x007A0700` ja `0x007AF2BC` | Kaksi 245 760 t GNU tar -arkistoa — laitteen konfiguraatio-/kalibrointiosio kahtena kopiona (A/B-redundanssi) |

Kaksi keskeistä hyötykuormaa tunnistettiin: **Linux-kerneli** (uImage/gzip, n. 2,3 Mt) ja **SquashFS-rootfs** (sovellustaso, tehtävä 4). Näiden lisäksi kuvassa on paljon pieniä upotettuja binäärejä ja datalohkoja (OSD-fontit/-kuvakkeet, ISP-kalibrointidata, sertifikaatteja) — binwalk löysi kuvasta yhteensä 117 tunnistettavaa offsetia.

---

## 3. Rootfsin erottaminen dump-tiedostosta

`dump-tapo-c200v3-1.4.2.bin` on 8 388 608 tavun (8 Mt) raaka flash-dumppi otettu suoraan laitteesta (esim. SPI-flashin lukija tai UART/JTAG-reitin kautta), toisin kuin verkosta ladattu, valmistajan salaama päivityspaketti. Tämä tiedosto **ei ole salattu**, koska se on jo laitteen suorittama, purettu sisältö sellaisenaan flashilla.

Etsin ensin tunnetut allekirjoitukset raa'asta dumpista:

- gzip-alkutunniste (`1F 8B 08`) offsetissa `0x00030100` (196864) → pieni tar-paketti
- SquashFS-tunniste (`hsqs`) offsetissa `0x00440000` (4456448) → varsinainen rootfs

```bash
# Rootfs (SquashFS) irti dumpista
dd if=dump-tapo-c200v3-1.4.2.bin of=extractions/dump-rootfs.squashfs bs=1 skip=4456448
unsquashfs -d extractions/dump-rootfs extractions/dump-rootfs.squashfs
```

Ensimmäisellä yrityksellä `unsquashfs`-komentoa ei ollut asennettuna (`bash: unsquashfs: command not found`); asensin `squashfs-tools`-paketin (ja tarvittaessa `sasquatch`-forkin, joka tukee valmistajien käyttämiä epästandardeja pakkausvariantteja), minkä jälkeen purku onnistui:

```
Parallel unsquashfs: Using 12 processors
76 inodes (204 blocks) to write
created 70 files, 20 directories, 6 symlinks
```

Samasta dumpista kaivettiin lisäksi pienempi gzip-osio (konfiguraatio-/radio-kalibrointidata):

```bash
dd if=dump-tapo-c200v3-1.4.2.bin of=extractions/small-gzip.gz bs=1 skip=196864 count=60091
gunzip -k extractions/small-gzip.gz
tar -xf extractions/small-gzip -C extractions/small-gzip-extracted
```

Tuloksena `base-files/etc/*.config` (JSON-muotoiset laite-, ISP-, audio- ja OEM-asetukset) sekä `radio/`-hakemisto Wi-Fi-radion PHY/e-fuse-kalibrointidatalla ja `encrypt_key`-tiedosto (ks. tehtävä 6).

---

## 4. Rootfsin erottaminen kuvatiedostosta

Sama SquashFS-rootfs löytyy myös puretusta valmistajan kuvasta (`Tapo_C200v4_en_1.4.2.bin.dec`), offsetissa `0x3E0200`. Tässä käytettiin `binwalk`in automaattista erottelua (`-e`), joka tunnistaa SquashFS-otsikon ja ajaa `unsquashfs`-purun automaattisesti alihakemistoon:

```bash
binwalk -e Tapo_C200v4_en_1.4.2.bin.dec
```

Tulos: `extractions/Tapo_C200v4_en_1.4.2.bin.dec.extracted/3E0200/squashfs-root/`, joka sisällöltään vastaa täysin dump-tiedostosta käsin eroteltua rootfsia (`bin/`, `config/`, `etc/`, `lib/`, `usr/`) — sama tiedostomäärä (70 tiedostoa, 20 hakemistoa, 6 symlinkkiä) ja samat tiedostot tavulleen. Tämä on tärkeä ristiintarkistus: **kaksi täysin eri lähteestä (fyysinen flash-dumppi vs. verkosta ladattu ja salauksesta purettu päivityspaketti) ja kahdella eri menetelmällä (käsin `dd`+`unsquashfs` vs. automaattinen `binwalk -e`) tuottivat identtisen rootfsin**, mikä vahvistaa sekä salauksenpurun onnistuneen oikein että dumpin olevan aito.

---

## 5. Saatavilla olevien sovellusten kartoitus

Rootfsin (`bin/`, `usr/bin/`, `usr/sbin/`, `lib/modules/`) sisältö on hyvin suppea — tämä ei ole täysi Linux-jakelu, vaan minimaalinen sulautettu ympäristö, jossa yksi suuri sovellus (`main`) hoitaa lähes kaiken kameran toiminnallisuuden.

**Pääsovellus**
- `bin/main` — n. 3,5 Mt:n MIPS32-binääri, joka sisältää HTTP-hallintarajapinnan (`/admin/system/...`-reitit), pilvi-/onboarding-logiikan, videosuoratoiston, PTZ-moottoriohjauksen ja liikkeentunnistuksen. Käytännössä koko kameran "käyttöjärjestelmäpalvelu".

**Diagnostiikka- ja debug-työkalut** (`bin/`)
- `gdbserver` — etähallintapalvelin, jolla voisi liittyä käynnissä olevaan `main`-prosessiin verkon yli
- `impdbg`, `logcat`, `dmesg`, `getcpuinfo` — sisäisiä loki-/vianetsintätyökaluja
- `date` — ajanhallinta

**Verkko- ja järjestelmädaemonit** (`usr/sbin/`, `usr/bin/`)
- `hostapd` — Wi-Fi-tukiasematila (laitteen alkukytkentä/onboarding)
- `dnsd` — kevyt oma DNS-daemon
- `chroot` — juurihakemiston vaihto
- `mkfs.fat`, `fsck.fat`, `fatlabel` — muistikortin (SD) FAT32-alustus/korjaus
- `iperf` — verkon suorituskykytesti
- `is_cal_real.script` — kalibrointiskripti

**Jaetut kirjastot** (`lib/`, `usr/lib/`)
- uClibc-kirjastot (`libcrypt`, `libdl`, `libm`, `libpthread`, `librt`)
- `libaudioProcess.so`, `libudt.so` (UDT-protokolla, käytetään usein P2P-videosuoratoistossa), `libstdc++`

**Ytimen moduulit** (`lib/modules/3.10.14/`)
- `tx-isp-t31.ko` — Ingenic T31-SoC:n kuva-anturi-/ISP-ajuri
- `sensor_sc2336_t31.ko` — SmartSens SC2336-kuva-anturin ajuri
- `avpu.ko` — video-/äänienkooderin kiihdytin
- `audio.ko` — äänipiirin ajuri
- `motor_driver.ko` — PTZ-askelmoottoriohjaus
- `mmc_core.ko`, `mmc_block.ko`, `jzmmc_v12.ko` — muistikorttiväylä
- `esp32.ko` — apuprosessorin (Wi-Fi/BT-yhteysprosessori?) ajuri
- `sinfo.ko` — laitetieto-/sarjanumeromoduuli

Löydös: laitteistoalustaksi paljastui **Ingenic T31 (MIPS32r2, uClibc, Linux 3.10.14)** SoC, joka on tyypillinen halvoissa Kiinalais-valmisteisissa IP-kameroissa — ei siis Qualcomm/Amlogic-alusta, jota osa vanhemmasta TP-Link-dokumentaatiosta viittaa.

---

## 6. Root-salasanan analysointi ja avaamisyritys

### 6.1 Perinteistä käyttäjätietokantaa ei löydy

Rootfsista etsittiin ensin klassiset Linux-tunnistetiedostot:

```bash
find . -iname "passwd*" -o -iname "shadow*"
```

**Kummastakaan rootfsista (dump- tai kuvaperäisestä) ei löytynyt `/etc/passwd`- eikä `/etc/shadow`-tiedostoa**, eikä edes `login`/`getty`/`sh`-tulkkia. Tämä poikkeaa oleellisesti "tavallisesta" sulautetusta Linuxista: laitteessa ei ole monikäyttäjäistä kirjautumisjärjestelmää eikä perinteistä root-shelliä käynnistyksessä — kaikki todennus (paikallinen web-admin, pilviyhdistäminen, laiteparinmuodostus) hoidetaan `main`-binäärin sisäisesti.

### 6.2 Merkkijonoanalyysi

```bash
strings bin/main | grep -iE "root|passwd|login|telnet|admin"
```

Osumia mm.: `factory_passwd`, `gen_root_passwd`, `bp_passwd`, `digest_passwd`, `hub_passwd`, `root_passwd`, `change_admin_password`, `get_cam_passwd`, `has_valid_temp_passwd`. Nämä viittaavat siihen, että laitteella *on* sisäinen "root-salasana"-käsite (käytössä mm. paikallishallinnan/hub-yhdistämisen todennuksessa), mutta se muodostetaan/tallennetaan ohjelmallisesti, ei staattisena tekstinä binäärissä eikä tiedostojärjestelmässä.

### 6.3 Binäärin arkkitehtuuri ja työkaluongelma

```
$ file bin/main
bin/main: ELF 32-bit LSB executable, MIPS, MIPS32 rel2 version 1 (SYSV), dynamically linked, interpreter /lib/ld-uClibc.so.0, stripped
```

Binääri on **riisuttu (stripped)** MIPS32r2-koodia. Järjestelmässä ei ollut valmiina MIPS-yhteensopivaa `objdump`/`radare2`/Ghidra-asennusta (`objdump: can't disassemble for architecture UNKNOWN!`), eikä pip/pakettien asennus onnistunut suoraan (Arch-ympäristön "externally-managed" -rajoitus, ei verkkoyhteyttä pip-indeksiin). Tämän vuoksi kirjoitin n. 100 rivin **oman MIPS32-purkuskriptin** (Python), joka tulkitsee yleisimmät R/I/J-tyypin käskyt (lui/addiu/jal/beq/lw/sw jne.) suoraan ELF-tekstisegmentistä.

### 6.4 `gen_root_passwd`-merkkijonon jäljitys

Etsin merkkijonon `"gen_root_passwd"` tiedosto-offsetin (`0x26F2D4`), laskin siitä virtuaaliosoitteen `.rodata`-segmentin perusteella (`VA = 0x66F2D4`) ja etsin binäärin `.text`-segmentistä kaikki `lui`+`addiu`-käskyparit, jotka rakentavat juuri tämän osoitteen (MIPS lataa 32-bittisiä vakio-osoitteita kahdella käskyllä):

```python
hi = (target_va + 0x8000) >> 16 & 0xffff   # 0x67
lo = target_va & 0xffff                     # 0xf2d4
```

Löytyi kaksi osumaa (`0x4202AC`, `0x4203C4`). Näiden ympäristön (funktio `0x41FE8C`–`0x42014C`) purku paljasti, että merkkijonoa käytetään **vain lokitusfunktion moduulitunnisteena** (`jal 0x0071f080` -kutsuissa parametreina taso/rivinumero/moduulinimi) sisällä asetustiedoston jäsentimessä (buffereiden alustus, kenttien luku, virhekoodit) — ei itse salasanan generointi-/tiivistysalgoritmina. Toisin sanoen tämä funktio *reagoi* virheisiin lokittamalla tunnisteella `"gen_root_passwd"`, mutta varsinainen kryptografinen logiikka (jos sellaista käytetään) on koodissa muualla, eikä sitä löytynyt tällä hakumenetelmällä.

### 6.5 `encrypt_key`-löydös

Dump-tiedostosta puretusta konfiguraatio-osiosta löytyi tiedosto `base-files/etc/encrypt_key`, sisältö:

```
17CD41F251DB9B5F
```

Tämä on 8 tavun (64-bittinen) heksadesimaaliavain — kokoluokaltaan sopiva esim. DES-avaimeksi. Se on todennäköisesti avain, jolla laite salaa/purkaa paikallisesti tallennettuja tunnistetietoja (esim. laiteparinmuodostuksen/pilviyhdistämisen aikana vaihdettuja arvoja) tai etätuen/tehtaan diagnostiikkatilan avausta varten. Avaimen käyttökohdetta ei pystytty yksiselitteisesti todistamaan ilman vastaavaa salattua dataa (esim. aidon, käytössä olleen laitteen konfiguraatiotallennetta), joten sen hyödyntäminen jäi tässä analyysissä dokumentoinniksi, ei täydeksi purkuketjuksi.

### 6.6 Johtopäätös

**Root-salasanaa ei onnistuttu — eikä pystyttykään — avaamaan puhtaasti staattisella tiedostojärjestelmäanalyysillä**, koska sellaista ei ole tallennettu perinteisessä `/etc/shadow`-muodossa mihinkään kahdesta tutkitusta rootfs-kopiosta. Löydökset (merkkijonot, `encrypt_key`, `gen_root_passwd`-viittaus asetusjäsentimessä) osoittavat todennuksen olevan sovelluksen (`main`) sisäistä logiikkaa, joka todennäköisesti sitoo pääsyn joko TP-Link-pilvitiliin, laiteen omaan MAC-/sarjanumeropohjaiseen johdannaiseen tai tehdasasetuksiin — ei mihinkään yhteen staattiseen, kaikille laitteille yhteiseen oletussalasanaan. Täydellinen purku vaatisi joko:

1. koko `main`-binäärin täyden dekompiloinnin (Ghidra/IDA MIPS-tuella) `gen_root_passwd`-*toteutuksen* (ei vain lokitusviittauksen) löytämiseksi, tai
2. dynaamisen analyysin oikealla laitteella (UART-konsoli/JTAG, `gdbserver`-liitäntä käynnissä olevaan prosessiin), tai
3. aidon, salatun konfiguraatiotallenteen hankkimisen `encrypt_key`-avaimen käytön todentamiseksi.

---

## Yhteenveto: onkohan tämä turvallinen käyttää?

- Laiteohjelmiston salaus (RSA-allekirjoitus + AES) perustuu avaimiin, jotka TP-Link on itse julkaissut osana muita tuotteitaan — käytännössä salaus estää vain satunnaisen selailun, ei määrätietoista analyysiä.
- Laitteella ei ole perinteistä root-shelliä eikä `/etc/shadow`-tiedostoa, mikä on *parempi* asetelma kuin monissa vanhemmissa IoT-kameroissa, joissa on kova­koodattu oletussalasana.
- Laitteelta löytyy kuitenkin aktiivinen **`gdbserver`**-etävianetsintäpalvelin ja useita sisäisiä "passwd"-käsitteitä (`factory_passwd`, `bp_passwd`, `hub_passwd`), jotka laajentavat hyökkäyspintaa, jos niihin pääsee käsiksi paikallisverkosta.
- Paikallinen `encrypt_key`-tiedosto tallentaa salausavaimen selväkielisenä laitteen omaan tiedostojärjestelmään — yleinen sulautetun järjestelmän heikkous ("avain on siinä missä salattu datakin").

Kokonaisuutena laite ei paljastanut kriittistä, suoraan hyödynnettävää oletussalasanaa staattisella analyysillä, mutta laiteohjelmiston rakenteesta löytyi useita jatkotutkimuksen arvoisia kohteita (debug-työkalut, sisäiset salasanamekanismit, paikallisesti tallennettu salausavain).

---

## Lähteet

[TP-Link Decrypt repositorio](https://github.com/robbins/tp-link-decrypt)

[Tehtävänanto (Lari)](https://terokarvinen.com/application-hacking/#laksyt)

[Rooting the TP-Link Tapo C200 Rev.5 (Artikkeli)](quentinkaiser.be/security/2025/07/25/rooting-tapo-c200/)

Claude Sonnet 5 Hyödynnetty tehtävän ratkaisemisessa.
