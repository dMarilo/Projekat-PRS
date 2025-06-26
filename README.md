# Projekat Šahovskog Engine-a

Ovaj repozitorij sadrži implementaciju šahovskog engine-a u Pythonu sa AI sposobnostima korištenjem klasičnih algoritama poput Minimax i NegaMax sa Alpha-Beta orezivanjem. Engine takođe uključuje punu implementaciju šahovske igre sa pravilima poput en passant, rošade (djelimično), promocije piona i validacije poteza.

---

## Sadržaj

- [Pregled Projekta](#pregled-projekta)  
- [Struktura Koda](#struktura-koda)  
- [Ključne Komponente](#ključne-komponente)  
  - [Stanje igre i reprezentacija table](#stanje-igre-i-reprezentacija-table)  
  - [Generisanje i validacija poteza](#generisanje-i-validacija-poteza)  
  - [Logika rošade](#logika-rošade)  
  - [Klasa Potez](#klasa-potez)  
  - [AI Algoritmi](#ai-algoritmi)  
  - [Funkcija evaluacije](#funkcija-evaluacije)  
  - [Pomoćne funkcije za korisnički interfejs](#pomoćne-funkcije-za-korisnički-interfejs)  
- [Kako kod funkcioniše](#kako-kod-funkcioniše)  
- [Dalji koraci razvoja](#dalji-koraci-razvoja)  

---

## Pregled Projekta

Ovaj šahovski engine simulira igru između čovjeka i AI ili AI protiv AI koristeći klasične pretražne algoritme za izbor poteza. Engine održava stanje igre, validira poteze, pokriva posebna pravila poput rošade i en passant, i evaluira pozicije kako bi AI mogao donositi odluke.

---

## Struktura Koda

- **GameState (Stanje igre)**: Čuva trenutno stanje table, čiji je na potezu, prava za rošadu, stanje en passant, pozicije kraljeva, te provjerava šah, mat i pat.
  
- **Klasa Move (Potez)**: Predstavlja jedan potez sa početnim i krajnjim poljem, pomjerenom i pojedinom figurom, posebnim zastavicama (en passant, rošada, promocija) i pruža šahovsku notaciju.

- **Klasa CastlingRights (Prava rošade)**: Prati prava rošade za oba igrača.

- **AI Algoritmi**: Implementacije Minimax i NegaMax algoritama sa Alpha-Beta orezivanjem i funkciju za evaluaciju pozicija.

- **Evaluacija pozicije**: Kombinuje materijalnu vrijednost i pozicijske tablice za procjenu vrijednosti pozicije za igrača na potezu.

- **Funkcije za UI**: Pomažu u vizualnom označavanju odabranih polja i pozicije kralja, posebno kad je u šahu ili matu.

---

## Ključne Komponente

### Stanje igre i reprezentacija table

- Tabla je predstavljena kao lista 8x8, gdje svaki element opisuje figuru kao string npr. `"white pawn"`, `"black queen"` ili `"--"` ako je polje prazno.
- Varijable prate koji igrač je na potezu (`whiteToMove`), prava za rošadu, stanje en passant, te lokacije kraljeva.
- Stanje se ažurira svakim potezom, uključujući mogućnost vraćanja poteza.

### Generisanje i validacija poteza

- Generišu se svi legalni potezi za figure u skladu sa pravilima šaha i trenutnim stanjem igre.
- Posebni potezi (en passant, rošada, promocija piona) imaju posebne metode.
- Provjerava se da li su polja pod napadom radi validacije poteza.

### Logika rošade

- Prava rošade se prate i ažuriraju kako igra napreduje.
- Funkcije `getCastleMoves()`, `getKingsideCastleMoves()` i `getQueensideCastleMoves()` generišu dozvoljene rošade.
- Trenutno je potrebno popraviti implementaciju rošade da pravilno provjeri sigurnost polja kroz koja kralj prolazi i da pravilno pomjeri topa.

### Klasa Potez

- Sadrži sve informacije o potezu, uključujući početno i krajnje polje, figuru koja se pomjera, eventualno pojedenu figuru, i oznake posebnih poteza.
- Podržava poređenje poteza i konverziju u šahovsku notaciju.

### AI Algoritmi

- **Minimax**: Rekurzivni algoritam za pronalazak najboljeg poteza do određene dubine.
- **NegaMax sa Alpha-Beta orezivanjem**: Efikasnija verzija Minimax algoritma koja smanjuje broj istraženih čvorova.
- Oba algoritma koriste funkciju evaluacije za ocjenu pozicija.

### Funkcija evaluacije

- Kombinuje:
  - **Materijalnu vrijednost** figura na tabli.
  - **Pozicijske tablice** koje daju bonuse ili penale u zavisnosti od pozicije figure.
- Također uzima u obzir mat i pat situacije dajući im visoke pozitivne ili negativne ocjene.

### Pomoćne funkcije za korisnički interfejs

- `highlightSquare()`: Vizualno označava odabrano polje ako na njemu stoji figura igrača na potezu.
- `highlightKing()`: Boji polje kralja žutom ako je u šahu, ili tamnocrvenom ako je u šah-matu.

---

## Kako kod funkcioniše

1. **Inicijalizacija igre**: Tabla se postavlja u početni položaj.
2. **Naizmjenični potezi**: Generišu se legalni potezi za igrača na potezu.
3. **Odabir poteza**: Igrač bira potez ili AI računa najbolji potez koristeći Minimax ili NegaMax.
4. **Izvršavanje poteza**: Izabrani potez se primjenjuje na stanje igre.
5. **Provjera stanja igre**: Nakon svakog poteza provjerava se da li je igrač u šahu, matu, patu ili nekom drugom završnom stanju.
6. **Vizuelna podrška**: UI označava selektovane figure i status kralja.
7. **Undo/redo**: Omogućeno vraćanje poteza radi istraživanja različitih varijanti.

---

## Dalji koraci razvoja

Za završetak i unapređenje ovog projekta, potrebno je:

### 1. Potpuna implementacija Monte Carlo Tree Search (MCTS)

- Završiti sve faze MCTS algoritma: selekciju, ekspanziju, simulaciju i propagaciju.
- Integrisati MCTS sa trenutnim modelom igre i funkcijama za generisanje poteza.
- Implementirati eventualnu neuralnu mrežu ili heuristiku za simulacije.
- Osigurati da MCTS AI može korektno da bira poteze.

### 2. Popraviti implementaciju rošade

- Osigurati da su ispunjeni svi uslovi za rošadu:
  - Kralj i top nisu ranije pomjerani.
  - Polja između kralja i topa su prazna.
  - Kralj nije u šahu, niti prolazi ili završava na poljima pod napadom.
- Implementirati pravilno pomjeranje topa uz rošadu.
- Ažurirati prava rošade prilikom pomjeranja kralja ili topa.

### 3. Implementirati višedretvenost (multithreading)

- Poboljšati performanse AI algoritama pokretanjem izračunavanja u zasebnim dretvama.
- Omogućiti paralelnu evaluaciju poteza ili simulacija, posebno za MCTS.
- Voditi računa o sinhronizaciji da se izbjegnu problemi sa istovremenim pristupom i zamrzavanjem UI.

---

## Kontakt i saradnja

Ako želite doprinijeti ili imate pitanja, slobodno otvorite issue ili me kontaktirajte direktno.

---

Hvala što ste pogledali ovaj projekat!  
— Dušan Mariović  
