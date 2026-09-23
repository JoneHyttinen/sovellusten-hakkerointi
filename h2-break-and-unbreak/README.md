# h2 Break & Unbreak (Tero)

## x) Read/watch/listen and summarize

### OWASP Top 10:

- OWASP Top 10 on dokumentti, jossa tuodaan esille laaja yhteenveto kaikista kriittisimmistä turvallisuusriskeistä web sovelluksille.
- Top 1 turvallisuusriski on "Broken Access Control", joka löytyi jossain muodossa kaikista testatuista sovelluksista.
- BAC on turvallisuusriski, jossa systeemi epäonnistuu kunnollisesti rajaamaan, mitä autentikoitu käyttäjä saa tehdä tai nähdä sovelluksessa.

### Karvinen 2023:

- Fuff on web "fuzzaaja", jonka on tehnyt Joona "joohoi" Hoikkala. Käytännössä se automatisoi HTTP pyyntöjen lähettämisprosessin, ettei hakkerin tarvitse manuaalisesti lähettää eri pyyntöjä toistensa jälkeen.
- Teron artikkeli sisältää ohjeita miten ffuf-työkalua voi hyödyntää lokaalisti löytääkseen haavoittuvuuksia web sovelluksesta. Se sisältää myös lukijan suoritettavan haasteen.

### PortSwigger:

- PortSwiggerin artikkelissa selitetään esimerkeillä ja teorialla mitä access control tarkoittaa, ja minkälaisia haavoittuvuuksia siitä voi syntyä.
- Artikkelissa myös selitetään miten access control haavoittuvuuksia voidaan estää.

### Karvinen 2006

- Tässä Teron artikkelissa Tero selittää minkälainen raportin kuuluu olla, kun jotain testataan tietokoneella, kuten tämän kurssin harjoitustehtävien raportit.
- Raportin tulee olla toistettava, lukijan täytyy pystyä toistamaan testit samoilla lopputuloksilla, kuin raportin tekijällä
- Täsmällinen, pitää olla selkeää mitä työkaluja on käytetty, missä järjestyksessä ja onko testeissä tai työkaluissa ollut ongelmia
- Helppolukuinen, käytä väliotsikoita, kirjoita selkeää ja huolellista kieltä. 
- Raportissa täytyy viitata lähteisiin, koska hyvä tapa ja akateeminen käytäntö vaatii viittauksia.
- Artikkelissa on myös paljon esimerkkejä raporteista ja yleisiä mokia raportin kirjoittamisessa.

---

## a) Break into 010-staff-only

Aloitin tehtävän lataamalla zip tiedoston, jossa on haasteet `wget` komennolla.

Purin myös zip tiedostosta haasteet `unzip` komennolla.

![kuva1](./kuvia/kuva1.png)
(Latasin tiedostot Macilla, sen takia UI näyttää erilaiselta.)

---

Zip-tiedosto sisälsi challenges tiedoston, jonka sisällä on seuraavat kaksi haastetta:

![kuva2](./kuvia/kuva2.png)


Ensimmäinen haaste on 010-staff-only, jonka kansion sisältö on seuraavanlainen:

![kuva3](./kuvia/kuva3.png)

---

Yritin suorittaa kansion sisältä löytyneen Python-tiedoston ohjeiden mukaan, mutta järjestelmälläni ei ollut `python-flask-sqlalchemy` pakettia, joten latasin sen `pacman` packet managerilla, koska olen Arch-pohjaisella järjestelmällä (BTW).

![kuva4](./kuvia/kuva4.png)


Suoritin tiedoston uudestaan ja dev serveri meni päälle kuvan alla olevaan osoitteeseen.

![kuva5](./kuvia/kuva5.png)

---

Seuraavaksi aloitin hakkeroinnin annetussa osoitteessa, joka näytti aluksi tältä:

![kuva6](./kuvia/kuva6.png)

Pelin ohjeissa lukee, että PIN koodisi on 123, joka näyttää meidän salasanan, joka on **Somedude**.

Painamalla F12, avasin selaimen Inspector näkymän, josta näin sivun html-koodin. Sieltä huomataan, että sivusto ottaa syötteen vastaan seuraavalla tavalla:

![kuva7](./kuvia/kuva7.png)


Vaihtamalla html input tyypin `text` muotoon, voimme syöttää salasanan teksti muodossa, joka auttaa meitä SQL-injektiota tehtäessä.

Kokeilin perus SQL-injektio arvoa, jonka opin tunnilla `' OR 1=1--`. Tämä näytti salasanan olevan **foo**, joka antaa meille selkeän vihjeen siitä, että sovellus on murrettavissa, mutta meidän pitää näyttää oikealta riviltä salasana.

![kuva8](./kuvia/kuva8.png)


Tutkin hieman erilaisia SQL komentoja(?) ja löysin **LIMIT** komennon, jolla voidaan rajata kuinka monta riviä kyselymme saa näyttää, tämä ei kuitenkaan meitä auta tässä tehtävässä.

LIMIT komennolla on myös yksityiskohtaisempi käyttötarkoitus `LIMIT X OFFSET Y` tai `LIMIT Y, X`, jolla voimme spesifioida **X** luvulla, kuinka monta riviä palautamme, ja **Y** luvulla, kuinka monta riviä haluamme ohittaa kokonaan kyselyn palautuksessa.

Kokeilin ensin lisätä aikaisemman loppuun `LIMIT 1`, joka palautti saman **foo**, sen jälkeen `LIMIT 1, 1`, joka palautti **Somedude**.

Viimeisenä kokeilin `LIMIT 2, 1`, joka palautti oikean admin salasanan.

`SUPERADMIN%%rootALL-FLAG{Tero-e45f8764675e4463db969473b6d0fcdd}`

![kuva9](./kuvia/kuva9.png)

---

## b) Fix the 010-staff-only vulnerability from source code.

SQL-kysely käsitellään koodissa yhdistämällä pin merkkijono suoraan kyselyn muuttujaan.

![kuva10](./kuvia/kuva10.png)
(Python indentation ei toiminut neovimissä sen takia niin paljon erroreita.)

Poistin pin-merkkijonon yhdistämisen suoraan kyselyyn ja annoin sen erillisenä parametrina myöhemmin.

![kuva11](./kuvia/kuva11.png)

---

Uudella koodilla, jos yrität tehdä SQL-injektiota vastaukseksi tulee {not found}.

![kuva12](./kuvia/kuva12.png)

---

## c) Solve dirfuzt-1 from the article Karvinen 2023

Ensin latasin `ffuf` työkalun AUR-paketin yay:n avulla.

`yay -S ffuf`

Sitten latasin yleisiä web-polkuja sisältävän sanalistan.

`wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt`

---

## Lähteet

[OWASP Top 10 sivu]("https://owasp.org/projects/top-ten") (Teron sivuilla oleva linkki ei toiminut)

[Karvinen 2023]("https://terokarvinen.com/2023/fuzz-urls-find-hidden-directories/")

[PortSwigger]("https://portswigger.net/web-security/access-control")

[Karvinen 2006]("https://terokarvinen.com/2006/raportin-kirjoittaminen-4/")
