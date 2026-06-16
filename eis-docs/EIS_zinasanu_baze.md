# EIS (Elektroniskā iepirkumu sistēma) — Zināšanu bāze

> Šī zināšanu bāze ir veidota, balstoties uz oficiālo EIS dokumentāciju (rokasgrāmatām, MK noteikumiem Nr. 816, lietošanas noteikumiem, privātuma politiku un nozares eksperta analīzi). Tā kalpo kā pamats EIS atvērto datu lauku interpretācijai un sistēmas darbības izpratnei.

---

## 1. SISTĒMAS PĀRSKATS

### 1.1. Kas ir EIS

**Elektroniskā iepirkumu sistēma (EIS)** ir Latvijas valsts centralizētā e-iepirkumu platforma, ko uztur **Valsts reģionālās attīstības aģentūra (VRAA)** — MK noteikumos Nr. 816 saukta arī par "aģentūru". Sistēma pieejama: **www.eis.gov.lv**

> **Piezīme par nosaukumu:** Atvērto datu organizāciju klasifikatorā (reģ.nr. **90001733697**) šī iestāde tagad parādās kā **"Valsts digitālās attīstības aģentūra"** (pārdēvēta). MK noteikumi Nr. 816 vēl izmanto vēsturisko nosaukumu "Valsts reģionālās attīstības aģentūra" — abi attiecas uz vienu un to pašu institūciju.

EIS nodrošina:
- Centralizētu elektronisku preču un pakalpojumu iegādi valsts un pašvaldību iestādēm
- Publisko iepirkumu procedūru norisi elektroniskā formā
- E-izziņu (piegādātāju pārbaudes ziņu) automātisku iegūšanu
- Elektronisko izsoļu norisi

**Juridiskais ietvars:** EIS īsteno **divus institūtus**, kas izriet no Publisko iepirkumu likuma (PIL):
- **PIL 56. p. Vispārīgā vienošanās (VV)** — daudz-piegādātāju rāmja vienošanās uz laiku līdz 4 gadiem
- **PIL 57. p. Dinamiskā iepirkumu sistēma (DIS)** — bieži lietojamām, tirgū plaši pieejamām precēm

Skat. detalizētu analītisko izpratni: [`KATALOGI_UN_VV_IZPRATNE.md`](../KATALOGI_UN_VV_IZPRATNE.md)

### 1.2. EIS apakšsistēmas

| Nr. | Apakšsistēma | Apraksts | Atspoguļojums atvērtajos datos |
|-----|-------------|----------|-------------------------------|
| 1 | **E-pasūtījumu apakšsistēma** (e-katalogs) | Centralizēto iepirkumu VV ietvaros veikto darījumu noslēgšana starp pasūtītāju un piegādātāju | `EIS_E_PASUT_APST_*.csv` (pasūtījumi), `EIS_E_PASUT_*.csv` (piegādes) |
| 2 | **E-izziņu apakšsistēma** | Piegādātāju izslēgšanas gadījumu pārbaude no 4 reģistriem (IeM Sodu reģistrs, Uzņēmumu reģistrs, VID, Pašvaldību nekustamā īpašuma nodokļa sistēma) — skat. sadaļu 12 | Nav tieši atvērtajos datos |
| 3 | **E-konkursu apakšsistēma** | Publisko iepirkumu plānu publicēšana un iepirkumu procedūru norise, t.sk. dinamiskās iepirkumu sistēmas | `EIS_E_IEPIRKUMI_IZSLUDINATIE_*.csv`, `ATVERSANA_*.csv`, `REZULTATI_*.csv`, `GROZIJUMI_*.csv` |
| 4 | **E-izsoļu apakšsistēma** | Izsoļu norises process | Nav atsevišķi atvērtajos datos |

### 1.3. Juridiskais pamats

- **MK noteikumi Nr. 816** "Publisko elektronisko iepirkumu noteikumi" (20.12.2022) — galvenais regulējums
- **Publisko iepirkumu likums** — regulē e-konkursu procedūras
- **VRAA iekšējie noteikumi Nr. 1-2/23/10** (03.05.2023) — EIS lietošanas noteikumi
- **Valsts informācijas sistēmu likums** — VRAA kā EIS pārzinis

---

## 2. LIETOTĀJU LOMAS UN TIESĪBAS

### 2.1. Sistēmas lomas

| Nr. | Loma | Latviskais nosaukums | Organizācijas tips | Apraksts |
|-----|------|---------------------|-------------------|----------|
| 1 | **Viesis** | Viesis | — | Neautorizēts lietotājs. Publiskā informācija, kataloga apskate |
| 2 | **Iepircējs** | Iepircējs | Pircējs | Veido grozus, nosūta pirkuma pieprasījumus, apskata pasūtījumus |
| 3 | **Apstiprinātājs** | Apstiprinātājs | Pircējs | Apstiprina/noraida pirkuma pieprasījumus un pasūtījumus |
| 4 | **Saņēmējs** | Saņēmējs | Pircējs | Apstiprina preču saņemšanu un kvalitāti piegādēm |
| 5 | **Pircēja administrators** | Pircēja administrators | Pircējs | Pārvalda organizācijas lietotājus un datus |
| 6 | **Piegādātājs** | Piegādātājs | Piegādātājs | Apstiprina/noraida pasūtījumus, veido piegādes, uztur preču datus katalogā |
| 7 | **Piegādātāja administrators** | Piegādātāja administrators | Piegādātājs | Pārvalda piegādātāja organizācijas lietotājus un datus |
| 8 | **Nozares eksperts** | Nozares eksperts | Iekšējais | Uzrauga un kontrolē katalogu saturu, pasūtījumus, piegādes |
| 9 | **Kataloga vadītājs** | Kataloga vadītājs | Iekšējais | Pārvalda katalogu saturu un VV pozīcijas |
| 10 | **Kataloga administrators** | Kataloga administrators | Iekšējais | Administrē katalogu konfigurāciju, audita datus |
| 11 | **Publikāciju redaktors** | Publikāciju redaktors | Iekšējais | Veido un publicē informatīvas publikācijas |
| 12 | **Sistēmas administrators** | Sistēmas administrators | Iekšējais | Pilnas sistēmas administrēšana |

### 2.2. Lietotāju tipi (saskaņā ar EIS lietošanas noteikumiem)

| Tips | Apraksts |
|------|----------|
| **Iekšējais lietotājs** | VRAA darbinieks vai ierēdnis — EIS darbības nodrošināšana |
| **Ārējais lietotājs** | EIS dalībnieka lietotājs — darbs ar apakšsistēmām |
| **Autentificētais lietotājs** | Pieslēdzies ar identifikācijas rīkiem |
| **Viesis** | Neautentificēts lietotājs — tikai publiskā piekļuve |

### 2.3. Autentifikācijas metodes

| Metode | Apraksts |
|--------|----------|
| Lietotājvārds + Parole | Standarta autentifikācija |
| Lietotājvārds + Parole + Kodu karte | Divfaktoru autentifikācija |
| VISS (Valsts Informācijas Sistēmu Savietotājs) | Ārējā autentifikācija |
| Elektroniskais paraksts (e-paraksts) | Autentifikācija ar e-parakstu |

**Paroles prasības:** min. 12 zīmes, lielais+mazais burts, cipars, speciālais simbols. Nomaiņa ik 90 dienas. Pēc 5 neveiksmīgiem mēģinājumiem — bloķēšana.

---

## 3. SISTĒMAS MODUĻI

### 3.1. Galvenie navigācijas moduļi (šķirkļi)

| Nr. | Modulis | Apraksts |
|-----|---------|----------|
| 1 | **Katalogs** | Katalogu, kategoriju, preču un VV pozīciju pārvaldība |
| 2 | **Grozs** | Iepirkumu grozu izveide un pārvaldība |
| 3 | **Pasūtījumi** | Pasūtījumu apstrāde, statusa maiņas, vēsture |
| 4 | **Piegādes** | Piegāžu pārvaldība, nodošanas-pieņemšanas akti |
| 5 | **Organizācijas** | Organizāciju datu pārvaldība, adreses, kontaktpersonas |
| 6 | **Atskaites** | Pircēja un piegādātāja atskaišu veidošana |
| 7 | **Audits** | Audita datu atskaišu izveide un apskate |
| 8 | **Pieteikumi** | Ieteikumu un sūdzību iesniegšana |
| 9 | **Informācija** | Ziņojumi, paziņojumi un publikācijas |
| 10 | **Lietotāji** | Lietotāja datu apskate, paroles maiņa |

---

## 4. KATALOGA STRUKTŪRA UN HIERARHIJA

### 4.1. Hierarhiskā struktūra

```
Katalogs (piem. "Datortehnika un programmatūra")
  └── Kategorija (ar CPV kodu, piem. "Datori")
       └── Apakškategorija (piem. "Portatīvie datori")
            └── VV pozīcija (ar preču veidu un CPV kodu)
                 ├── Prece 1 (piegādātāja A, ar cenu, reģionu info)
                 ├── Prece 2 (piegādātāja B)
                 └── Prece N (piegādātāja C)
```

### 4.2. Kataloga datu lauki

| Lauks | Tips | Apraksts |
|-------|------|----------|
| Kataloga nosaukums | Teksts | Kataloga pilnais nosaukums |
| Kataloga statuss | Statuss | Aktīvs/Bloķēts/Dzēsts |
| Spēkā esamības periods | Datums (no-līdz) | Kataloga darbības periods |

### 4.3. Kategorijas datu lauki

| Lauks | Tips | Apraksts |
|-------|------|----------|
| Kategorijas pozīcijas numurs | Teksts | Numurs hierarhijā |
| Kategorijas nosaukums | Teksts | Pilnais nosaukums |
| CPV kods | Teksts | Kopējā iepirkumu vārdnīcas kods (līdz 9 cipariem) |
| Apakškategoriju skaits | Skaitlis | Tiešo apakškategoriju skaits |
| Preču skaits | Skaitlis | Tiešo preču skaits |

### 4.4. VV (Vispārīgās vienošanās) pozīcijas datu lauki

| Lauks | Tips | Apraksts |
|-------|------|----------|
| Pozīcijas numurs | Teksts | VV pozīcijas pilnais numurs |
| Pozīcijas nosaukums | Teksts | VV pozīcijas nosaukums |
| Kategorija | Teksts | Piederības kategorija |
| CPV kods | Teksts | Kopējā iepirkumu vārdnīcas kods |
| Preču veids | Teksts | Nosaka specifisko un fiksēto īpašību kopu |
| Piegādātāju skaits | Skaitlis | Piesaistīto piegādātāju skaits |
| Aktīvo preču skaits | Skaitlis | Aktīvo preču skaits |
| Mērķgrupa | Teksts | VV pozīcijas mērķgrupa |
| Statuss | Statuss | Aktīva/Bloķēts/Dzēsts |

### 4.5. Preču datu lauki

| Lauks | Tips | Apraksts |
|-------|------|----------|
| Preces nosaukums | Teksts | Preces pilnais nosaukums |
| Piegādātāja piešķirtais kods | Teksts | Piegādātāja iekšējais preces kods |
| Ražotāja kods | Teksts | Ražotāja preces kods (unikāls sistēmā) |
| VV pozīcijas numurs | Teksts | Piederības VV pozīcija |
| Preču veids | Teksts | Preču veida nosaukums |
| Cena (bez PVN) | Skaitlis (EUR) | Preces vienības cena bez PVN |
| PVN likme | Procenti | Pievienotās vērtības nodokļa likme (5%, 21%) |
| Cena (ar PVN) | Skaitlis (EUR) | Preces vienības cena ar PVN |
| Minimālais iepirkuma limits | Skaitlis | Minimālais preces daudzums |
| Piegādes laiks | Teksts/skaitlis | Piegādes laika ilgums |
| Piegādātāja nosaukums | Teksts | Piegādātāja organizācija |
| Piegādes reģions | Teksts | Reģiona nosaukums |
| Apraksts | Teksts | Detalizēts preces apraksts |
| Ražotājs | Teksts | Ražotāja nosaukums |
| Ražotāja mājas lapa | URL | Ražotāja tīmekļa vietne |
| Garantija | Teksts/skaitlis | Garantijas periods (0 = nav garantijas) |
| Preces statuss | Statuss | Aktīva/Bloķēts/Dzēsts |
| Specifiskās īpašības | Mainīgs | Preču veidam specifiskās īpašības |
| Fiksētās īpašības | Mainīgs | Preču veidam fiksētās īpašības |
| Atlaide | % vai skaitlis | Atlaides procenti vai no noteikta skaita |
| Savstarpēji aizvietojamas preces | Saraksts | Saistīto preču saraksts |

### 4.6. Preču reģionālā informācija

Katrai precei var būt atšķirīgas cenas, piegādes laiki un minimālie limiti pa reģioniem:

| Reģions | Cena (bez PVN) | Cena (ar PVN) | Piegādes laiks | Min. limits | Atlaide |
|---------|---------------|---------------|---------------|-------------|--------|
| Rīga | ... | ... | ... | ... | ... |
| Kurzeme | ... | ... | ... | ... | ... |
| Latgale | ... | ... | ... | ... | ... |
| Vidzeme | ... | ... | ... | ... | ... |
| Zemgale | ... | ... | ... | ... | ... |

### 4.7. Preču imports/eksports (masveida apstrāde)

**Datnes formāts:** CSV, kodējums UTF-8 vai Baltic Windows-1257, atdalītājs — semikols (;), decimālzīme — punkts (.)

**Obligātie lauki importa datnē:**
| Lauks | Obligāts | Apraksts |
|-------|---------|----------|
| Preces nosaukums | Jā | Teksts kā pavadzīmē |
| Piegādātāja preces kods | Jā | Piegādātāja iekšējais kods |
| Ražotājs | Jā | Ražotāja nosaukums |
| Ražotāja preces kods | Jā | Unikāls sistēmas ietvaros |
| Garantija | Jā | Garantijas periods (0 = nav) |
| Apraksts | Jā | Papildu informācija par preci |
| Ir izmaiņas | Speciāls | "x" vai "X" = apstrādāt rindu, tukšs = ignorēt |

**Importa/eksporta datņu statusi:**

| Statuss | Apraksts |
|---------|----------|
| Gaida rindā | Datne gaida apstrādi |
| Tiek apstrādāta / Tiek ģenerēts | Sistēma apstrādā datni |
| Datne veiksmīgi importēta / Nosūtīts uz e-pastu | Veiksmīgs rezultāts |
| Importēta ar kļūdām | Importēta, bet ar kļūdām dažās rindās |
| Datnes apstrāde beidzās ar kļūdu / Ir notikusies kļūda | Neveiksmīgs rezultāts |

---

## 5. E-KATALOGA DARĪJUMU PROCESS

### 5.1. Pasūtījuma dzīves cikls (e-pasūtījumu apakšsistēma)

```
IEPIRCĒJS veido grozu
  ↓
Grozs → Pirkuma pieprasījums (nosūtīts piegādātājam)
  ↓
PIEGĀDĀTĀJS apstiprina/noraida
  ↓
Izskatīšanā pieņemts → Daļēji apstiprināts → Pieprasījuma apstiprinājums
  ↓
APSTIPRINĀTĀJS apstiprina
  ↓
Apstiprināts pasūtījums
  ↓
PIEGĀDĀTĀJS veido piegādi → Nosūtīta piegāde
  ↓
SAŅĒMĒJS apstiprina saņemšanu → Saņemtas preces
  ↓
SAŅĒMĒJS apstiprina kvalitāti → Kvalificēta piegāde
  ↓
Pilnībā izpildīts pasūtījums
```

### 5.2. Pasūtījuma statusi (pilns saraksts)

| Nr. | Statuss | Apraksts | Nākamie iespējamie statusi |
|-----|---------|----------|--------------------------|
| 1 | **Pirkuma pieprasījums** | Iepircējs nosūtījis grozu | Izskatīšanā pieņemts / Atteikts |
| 2 | **Izskatīšanā pieņemts pirkuma pieprasījums** | Piegādātājs pieņēmis izskatīšanai | Daļēji apstiprināts / Atteikts |
| 3 | **Daļēji apstiprināts pirkuma pieprasījums** | Piegādātājs daļēji apstiprinājis | Pieprasījuma apstiprinājums / Atteikts |
| 4 | **Pirkuma pieprasījuma apstiprinājums** | Piegādātājs pilnībā apstiprinājis | Apstiprināts pieprasījums / Atteikts |
| 5 | **Apstiprināts pirkuma pieprasījums** | Apstiprinātājs apstiprinājis pieprasījumu | Apstiprināts pasūtījums / Atteikts |
| 6 | **Apstiprināts pasūtījums** | Galīgi apstiprināts | Izmaiņu pieprasījumi / Pilnībā izpildīts / Izbeigts |
| 7 | **Daļēji apstiprināts pasūtījums** | Apstiprinātājs daļēji apstiprinājis | Apstiprināts pasūtījums / Atteikts |
| 8 | **Pircēja pieprasītas izmaiņas piegādes laikā** | Pircējs pieprasījis piegādes laika izmaiņas | Apstiprināts pasūtījums (automātiski) |
| 9 | **Pieprasītas izmaiņas piegādes laikā** | Piegādātājs pieprasījis izmaiņas | Apstiprināts pasūtījums (automātiski) |
| 10 | **Iepircēja apstiprinātas izmaiņas piegādes laikā** | Iepircējs apstiprinājis izmaiņas | Apstiprināts pasūtījums (automātiski) |
| 11 | **Pilnībā izpildīts pasūtījums** | ✅ Gala statuss — visas piegādes pabeigtas | — |
| 12 | **Izbeigts pasūtījums** | ✅ Gala statuss — pasūtījums izbeigts | — |
| 13 | **Atteikts pirkuma pieprasījums** | ❌ Gala statuss | — |
| 14 | **Atteikts daļējs pieprasījums** | ❌ Gala statuss | — |
| 15 | **Atteikts apstiprinātais pirkuma pieprasījums** | ❌ Gala statuss | — |
| 16 | **Atteikts daļējs pasūtījums** | ❌ Gala statuss | — |

### 5.3. Automātiskās statusa maiņas (katru dienu 00:30)

| No statusa | Uz statusu | Iemesls |
|-----------|-----------|---------|
| Pirkuma pieprasījums | Atteikts pirkuma pieprasījums | Termiņa beigas |
| Izskatīšanā pieņemts | Atteikts pirkuma pieprasījums | Termiņa beigas |
| Daļēji apstiprināts pieprasījums | Atteikts daļējs pieprasījums | Termiņa beigas |
| Pieprasījuma apstiprinājums | Atteikts daļējs pieprasījums | Termiņa beigas |
| Apstiprināts pirkuma pieprasījums | Atteikts apstiprinātais pieprasījums | Termiņa beigas |
| Daļēji apstiprināts pasūtījums | Atteikts daļējs pasūtījums | Termiņa beigas |
| Pircēja pieprasītas izmaiņas | Apstiprināts pasūtījums | Automātiski pēc termiņa |
| Pieprasītas izmaiņas | Apstiprināts pasūtījums | Automātiski pēc termiņa |
| Iepircēja apstiprinātas izmaiņas | Apstiprināts pasūtījums | Automātiski pēc termiņa |

### 5.4. Piegādes statusi

| Nr. | Statuss | Apraksts |
|-----|---------|----------|
| 1 | **Nosūtīta piegāde** | Piegādātājs izveidojis un nosūtījis piegādi |
| 2 | **Saņemtas preces** | Saņēmējs apstiprinājis preču saņemšanu (vai automātiski) |
| 3 | **Daļēji saņemtas preces** | Saņēmējs daļēji apstiprinājis |
| 4 | **Kvalificēta piegāde** | ✅ Gala statuss — kvalitāte apstiprināta |
| 5 | **Daļēji kvalificēta piegāde** | ✅ Gala statuss — daļēji apstiprināta kvalitāte |
| 6 | **Noraidīta piegāde** | ❌ Gala statuss — piegāde noraidīta |

**Automātiskās piegādes statusa maiņas:**
- Nosūtīta piegāde → Saņemtas preces (pēc termiņa)
- Daļēji saņemtas preces → Kvalificēta piegāde (pēc termiņa)

### 5.5. Atliktā groza process

"Atliktais grozs" ir lielo pasūtījumu apstrādes mehānisms, kur pircējs izveido grozu ar vairākām pozīcijām, un piegādātāji var izteikt īpašus piedāvājumus (ar specifiskām cenām) vai ļaut sistēmai automātiski piedāvāt kataloga aktīvās preces.

**Process:**
1. Pircējs izveido atlikto grozu ar pozīcijām
2. Piegādātāji saņem paziņojumu un var:
   - Izteikt īpašu piedāvājumu (norādot konkrētu preci un cenu)
   - Neko nedarīt (sistēma ņems kataloga aktīvo preci)
   - Atteikt dalību
3. Pēc noteikta termiņa grozs "nostrādā" — sistēma izvēlas vislētāko piedāvājumu
4. Rezultāti redzami ar ikonām (zaļa = vislētākais, sarkana = nav vislētākais)

**Galvenie lauki atliktajā grozā:**
- Piedāvātā rindas summa (bez PVN), EUR
- Darījumam paredzētais maksimālais finanšu līdzekļu apjoms (bez PVN), EUR
- Preces aktivitāte (izvēlne)

---

## 6. GROZA DATU LAUKI

### 6.1. Groza galvenie lauki

| Lauks | Tips | Apraksts |
|-------|------|----------|
| Groza numurs | Skaitlis | Sistēmas piešķirtais identifikators |
| Groza nosaukums | Teksts | Lietotāja piešķirtais nosaukums |
| Groza statuss | Statuss | Aktīvs / Neaktīvs |
| Izveides datums | Datums | Groza izveides datums |
| Organizācijas nosaukums | Teksts | Pircēja organizācija |
| Lietotājvārds | Teksts | Groza izveidotāja lietotājvārds |
| Vārds, Uzvārds | Teksts | Izveidotāja vārds un uzvārds |
| Vispārīgā vienošanās nosaukums | Teksts | VV nosaukums |
| Piegādātāja nosaukums | Teksts | Piegādātāja organizācija |
| Piegādes adrese | Teksts | Izvēlētā piegādes adrese |
| Piegādes reģions | Teksts | Reģiona nosaukums |
| Bankas konts | Teksts | Organizācijas bankas konts |
| Kopējā summa bez PVN | EUR | Groza kopsumma bez PVN |
| Kopējā summa ar PVN | EUR | Groza kopsumma ar PVN |
| Kopā PVN | EUR | PVN summa |
| Komentārs grozam | Teksts | Iepircēja komentārs |

### 6.2. Groza rindas lauki

| Lauks | Tips | Apraksts |
|-------|------|----------|
| Numurs pēc kārtas | Skaitlis | Preces kārtas numurs grozā |
| Pozīcijas numurs | Teksts | VV pozīcijas numurs |
| Nosaukums | Teksts | Preces nosaukums |
| Piegādātāja piešķirtais kods | Teksts | Preces kods |
| Skaits | Skaitlis | Daudzums |
| Vienības cena (bez PVN) | EUR | Preces cena |
| Summa (bez PVN) | EUR | Rindas kopsumma |
| PVN % | Procenti | PVN likme |
| Komentārs precei | Teksts | Komentārs par preci |

---

## 7. PASŪTĪJUMA DATU LAUKI

### 7.1. Pasūtījuma galvenie lauki

| Lauks | Tips | Apraksts | Atvērto datu relevance |
|-------|------|----------|----------------------|
| Pasūtījuma numurs | Skaitlis | Sistēmas unikālais ID | ✅ Primārā atslēga |
| Pasūtījuma statuss | Statuss | Pašreizējais statuss | ✅ |
| Groza nosūtīšanas datums | Datums | Pieprasījuma izveides datums | ✅ |
| Pasūtījuma aktuālais datums | Datums | Pēdējā statusa maiņas datums | ✅ |
| Piegādātāja piešķirtais numurs | Teksts | Piegādātāja iekšējais numurs | |
| Vispārīgā vienošanās numurs | Teksts | VV identifikators | ✅ |
| Piegādātāja nosaukums | Teksts | Piegādātāja organizācija | ✅ |
| Pasūtītāja nosaukums | Teksts | Pircēja organizācija | ✅ |
| Reģistrācijas numurs | Teksts | Nodokļu maksātāja reģ. nr. | ✅ Saite ar PASUTITAJI_KLAS |
| Juridiskā adrese | Teksts | Organizācijas adrese | |
| Pamata konts | Teksts | Bankas konts | |
| Kontaktpersona | Teksts | Kontaktpersonas vārds | |
| Telefons | Teksts | Tālruņa numurs | |
| E-pasts | Teksts | E-pasta adrese | |
| Piegādes adrese | Teksts | Piegādes vieta | |
| Pasūtījumu jāmaina līdz | Datums | Apstrādes termiņš | |
| Kopējā summa bez PVN | EUR | Pasūtījuma kopsumma | ✅ |
| Kopā PVN | EUR | PVN summa | |
| Kopējā summa ar PVN | EUR | Kopsumma ar PVN | ✅ |

### 7.2. Pasūtījuma rindas lauki

| Lauks | Tips | Apraksts |
|-------|------|----------|
| Numurs pēc kārtas | Skaitlis | Rindas numurs |
| Pozīcijas numurs | Teksts | VV pozīcijas numurs |
| Nosaukums | Teksts | Preces nosaukums |
| Piegādātāja piešķirtais kods | Teksts | Preces kods |
| Skaits | Skaitlis | Pēdējais saskaņotais daudzums |
| Vienības cena (bez PVN) | EUR | Preces cena |
| Summa (bez PVN) | EUR | Rindas summa |
| PVN % | Procenti | PVN likme |
| Atlaide % | Procenti | Piemērotā atlaide |

---

## 8. PIEGĀDES DATU LAUKI

### 8.1. Piegādes galvenie lauki

| Lauks | Tips | Apraksts |
|-------|------|----------|
| Piegādes statuss | Statuss | Pašreizējais statuss |
| Pavadzīmes numurs | Teksts | Piegādātāja pavadzīmes numurs |
| Pasūtījuma numurs | Skaitlis | Saistītā pasūtījuma ID |
| Piegādātāja piešķirtais numurs | Teksts | Piegādātāja iekšējais numurs |
| Vispārīgā vienošanās numurs | Teksts | VV identifikators |
| Apraksts | Teksts | Piegādes apraksts |
| Statusa piešķiršanas datums | Datums | Pēdējā statusa datums |
| Piegāde jāmaina līdz | Datums | Apstrādes termiņš |
| Piegāde līdz | Datums | Piegādes termiņa datums |

### 8.2. Piegādes rindas lauki

| Lauks | Tips | Apraksts |
|-------|------|----------|
| Pozīcijas numurs, Nosaukums, Kods | Teksts | Preces identifikācija |
| Kopējais skaits pasūtījumā | Skaitlis | Pasūtītais daudzums |
| Šajā piegādē iekļautais skaits | Skaitlis | Piegādātais daudzums šajā piegādē |
| Vienības cena (bez PVN) | EUR | Preces sākotnējā cena |
| Summa piegādē, bez PVN | EUR | Rindas summa piegādē |
| Saņemts | Skaitlis | Saņemtais daudzums |
| Kvalitatīvs skaits | Skaitlis | Kvalitatīvi pieņemtais daudzums |
| PVN % | Procenti | PVN likme |
| Saņēmēja komentārs precei | Teksts | Komentārs par preci |
| Iepircēja komentārs precei grozā | Teksts | Sākotnējais komentārs |
| Saņēmēja kopīgais komentārs | Teksts | Kopīgais komentārs |

---

## 9. ORGANIZĀCIJAS DATU LAUKI

### 9.1. Organizācijas galvenie lauki

| Lauks | Tips | Apraksts |
|-------|------|----------|
| Nosaukums | Teksts | Organizācijas pilnais nosaukums |
| Saīsinātais nosaukums | Teksts | Nosaukuma saīsinājums |
| Organizācijas veids | Klasifikators | Organizācijas tips |
| Organizācijas loma | Klasifikators | Pircējs / Piegādātājs |
| Statuss | Statuss | Aktīvs / Bloķēts / Dzēsts |
| Reģistrācijas numurs | Teksts | Nodokļu maksātāja reģ. nr. |
| PVN maksātāja reģ. numurs | Teksts | PVN reģistrācijas numurs |
| Juridiskā adrese | Teksts | Juridiskā adrese |
| Katalogs | Teksts | Piesaistītais katalogs |
| Dalības nosacījumu periods | Datums (no-līdz) | VV dalības periods |
| Bankas konts | Teksts | Bankas konta numurs |
| Pamata konts (pazīme) | Boolean | Vai konts ir pamata |

### 9.2. Adreses lauki

| Lauks | Tips | Apraksts |
|-------|------|----------|
| Adreses veids | Klasifikators | Juridiskā / Piegādes adrese |
| Nosaukums | Teksts | Adreses nosaukums |
| Novads | Teksts | Novads |
| Apdzīvota vieta | Teksts | Pilsēta, pagasts |
| Iela | Teksts | Ielas nosaukums |
| Māja | Teksts | Mājas numurs |
| Dzīvoklis | Teksts | Dzīvokļa numurs |
| Pasta indekss | Teksts | Pasta kods |
| Valsts | Teksts | Valsts |
| Piegādes reģions | Teksts | Reģions |
| Darba laiks | Teksts | Piegādes adreses darba laiks |

### 9.3. Kontaktpersonu lauki

| Lauks | Tips |
|-------|------|
| Vārds | Teksts |
| Uzvārds | Teksts |
| Amats | Teksts |
| Departaments | Teksts |
| Tālruņa numurs | Teksts |
| Faksa numurs | Teksts |
| E-pasts | Teksts |

---

## 10. PASŪTĪTĀJU KLASIFIKATORS (ATVĒRTIE DATI)

Atvērto datu portālā pieejams fails **PASUTITAJI_KLAS.CSV** — centrālais klasifikators ar visiem EIS reģistrētajiem pasūtītājiem.

| Lauka nosaukums | Datu tips | Apraksts |
|----------------|-----------|----------|
| Nr | numeric | Kārtas numurs |
| Organizacija | text | Pasūtītāja pilns juridiskais nosaukums |
| RegNr | numeric | Reģistrācijas numurs (Primary Key) |
| RegNrVeids | text | PVN numurs vai Personas kods/NMR kods |
| Augstak_stavosa_organizacija | text | Hierarhiskā padotība (augstākstāvošā org.) |
| RegDatums | text (DD.MM.GGGG) | Reģistrācijas datums EIS |
| Blokets | text | Vai konts ir bloķēts |
| Dzests | text | Vai konts ir dzēsts |
| _id | sistēmas | Iekšējais DB identifikators |

---

## 11. ATVĒRTO DATU KOPAS UN TO SAISTĪBA AR EIS MODUĻIEM

### 11.1. E-kataloga (e-pasūtījumu) datu kopas

| Datu kopa | Failu prefikss | Gadi | Modulis | Kas reģistrēts |
|-----------|---------------|------|---------|---------------|
| **Pirkuma pasūtījumi** | `EIS_E_PASUT_APST_` | 2010-2026 | E-pasūtījumi | Apstiprināti pasūtījumi e-katalogā |
| **Piegādes** | `EIS_E_PASUT_` | 2010-2026 | E-pasūtījumi | Faktiski veiktās piegādes |
| **Pasūtītāju klasifikators** | `PASUTITAJI_KLAS` | Viens fails | E-pasūtījumi | Visu pasūtītāju reģistrs |

### 11.2. E-konkursu datu kopas

| Datu kopa | Failu prefikss | Gadi | Modulis | Kas reģistrēts |
|-----------|---------------|------|---------|---------------|
| **Izsludinātie iepirkumi** | `EIS_E_IEPIRKUMI_IZSLUDINATIE_` | 2016-2026 | E-konkursi | Iepirkumu paziņojumi |
| **Piedāvājumu atvēršana** | `EIS_E_IEPIRKUMI_ATVERSANA_` | 2016-2026 | E-konkursi | Atvēršanas protokoli |
| **Iepirkumu rezultāti** | `EIS_E_IEPIRKUMI_REZULTATI_` | 2018-2026 | E-konkursi | Līgumu noslēgšana |
| **Iepirkumu grozījumi** | `EIS_E_IEPIRKUMI_GROZIJUMI_` | 2016-2026 | E-konkursi | Līguma izmaiņas |

### 11.3. Datu savstarpējās saistības

```
PASUTITAJI_KLAS.CSV (RegNr)
    ↕ saite caur reģistrācijas numuru
EIS_E_PASUT_APST_*.csv (pasūtījuma dati ar pasūtītāja info)
    ↕ saite caur pasūtījuma numuru
EIS_E_PASUT_*.csv (piegādes dati ar pasūtījuma numuru)
```

```
EIS_E_IEPIRKUMI_IZSLUDINATIE_*.csv (iepirkuma ID)
    ↕ saite caur iepirkuma identifikatoru
EIS_E_IEPIRKUMI_ATVERSANA_*.csv (piedāvājumu atvēršana)
    ↕
EIS_E_IEPIRKUMI_REZULTATI_*.csv (rezultāti un līgumi)
    ↕
EIS_E_IEPIRKUMI_GROZIJUMI_*.csv (līguma grozījumi)
```

---

## 12. E-IZZIŅU APAKŠSISTĒMA

E-izziņu apakšsistēma automātiski pārbauda piegādātāju atbilstību, iegūstot datus no **4 reģistriem** (saskaņā ar MK noteikumiem Nr. 816 16. punktu):

| Nr. | Reģistra pārzinis | Reģistrs / sistēma | Pārbaudāmā informācija |
|-----|---------|----------------------|---|
| 1 | **Iekšlietu ministrijas Informācijas centrs** | Sodu reģistrs | Sodāmības dati, administratīvie pārkāpumi |
| 2 | **Uzņēmumu reģistrs** | Uzņēmumu reģistra informācijas sistēma | Reģistrācijas un maksātnespējas dati |
| 3 | **Valsts ieņēmumu dienests (VID)** | VID informācijas sistēmas | Nodokļu parādi, deklarācijas, **darbinieku vidējās stundas tarifa likmes profesiju grupās** |
| 4 | **Latvijas Republikas pašvaldības** | Nekustamā īpašuma nodokļa administrēšanas sistēma | Nodevu parādi |

> **Piezīme par IUB:** Iepirkumu uzraudzības birojs (IUB) **nav** e-izziņu reģistra pārzinis. IUB uztur atsevišķu **publikāciju vadības sistēmu** (PIL 1.p. 25)) un **tiesību izmantošanas aizlieguma reģistru** (PIL 80. pants), no kura informāciju izsmeļ atsevišķi.

**Pārbaudāmie izslēgšanas pamati:**
- Publisko iepirkumu likuma 42. pants
- Aizsardzības un drošības jomas iepirkumu likuma 44. pants
- Sabiedrisko pakalpojumu sniedzēju iepirkumu likuma 48. pants
- PPP likuma 37. pants
- Darbinieku vidējās stundas darba algas likmes pa profesiju grupām (PIL 53. p. nepamatoti zemiem piedāvājumiem)

**E-izziņas ģenerēšanas laiks:** maksimums **24 stundas** (MK 816 21. punkts)

---

## 13. CENTRALIZĒTO IEPIRKUMU PREČU/PAKALPOJUMU GRUPAS

Saskaņā ar **MK noteikumu Nr. 816 1. pielikumu** (faktiskais saraksts pārvilkts uz 2024. gada redakciju):

| Nr. | Preču/pakalpojumu grupa | Rīkotājs | Apakšgrupas |
|-----|----------------------|----------|-------------|
| 1 | **Biroja papīrs un kancelejas preces** | VRAA | Dokumentu uzglabāšanas preces, papīrs un papīra preces, rakstāmgalda piederumi, datu nesēji, prezentāciju piederumi |
| 2 | **Datortehnika un tās uzstādīšana** | VRAA | Galda datori, planšetdatori, portatīvie datori, monitori, nepārtrauktās barošanas avoti |
| 3 | **Demonstrācijas iekārtas** | VRAA | Interaktīvie ekrāni, audio/video/foto iekārtas, papildierīces |
| 4 | **Drukas un kopēšanas iekārtas** | VRAA | Digitālās kopēšanas, daudzfunkc. lāzer/tintes, lāzer/tintes drukas, platformāta, specializētās |
| 5 | **Drukas iekārtu piederumi** | VRAA | Toneri, tintes kasetnes, citi piederumi |
| 6 | **Mēbeles** | VRAA | Biroja un apmeklētāju krēsli, biroja komplektējamās, izglītības iestāžu, metāla mēbeles |
| 7 | **Programmatūra un atbalsta pakalpojumi** | VRAA | Biroja, operētājsistēmas, lietojumu programmat., apmācības, serveru standarta programm. |
| 8 | **Saimniecības preces** | VRAA | Papīra higiēnas preces, sadzīves ķīmija, telpu uzturēšanas/uzkopšanas |
| 9 | **Servertehnika un datu glabātavas** | VRAA | Serveri/statnes, komutatori, asmensserveri, datu glabātavas, UPS, uzstādīšana |
| 10 | **Mākoņskaitļošanas pakalpojumi** | VRAA | — |
| 11 | **Pārtikas preces** | VRAA | — |
| 12 | **Medikamenti, medicīnas preces, medicīniskās ierīces, IAL** | **Veselības ministrija** (ievērojot VRAA tehniskās specifikāciju veidnes) | — |
| 13 | **Civilstāvokļa aktu reģistrācijas veidlapas** | **Tieslietu ministrija** (ievērojot VRAA tehniskās specifikāciju veidnes) | — |

**Datu pierādījumi (no `eis.db`):** EIS e-katalogā parādās tieši šīs grupas — CI sērijas katalogi (CI119 kanceleja, CI123V datortehnika, CI118 programmatūra, CI120 saimniecība, CI124 mēbeles, CI114M drukas izejmateriāli) plus NVD sērija medikamentiem (NVD3, NVD10R, NVD11R).

**Implikācija analīzei:** Šis ir **vienīgais saraksts**, kura iepirkumus VRAA centralizē. Visas pārējās jomas — medicīnas ierīces ar lielāku specifiku, ceļi, mežrūpniecība, aizsardzība, transports, energoresursi, telekomunikācijas — paliek **decentralizētās VV** ar pašu iestāžu rīkotām procedūrām (skat. KATALOGI_UN_VV_IZPRATNE.md sadaļu 2.3).

---

## 13a. VISPĀRĪGĀS VIENOŠANĀS JURIDISKAIS IETVARS (PIL 56. P.) UN DIVI TIPI

VV ir PIL 1. p. 33) definēts institūts: vienošanās starp pasūtītāju(-iem) un piegādātāju(-iem) noteikt **attiecīgā laikposmā slēdzamos iepirkuma līgumus**.

### 13a.1. PIL 56. panta galvenie noteikumi

| Pants | Noteikums |
|-------|-----------|
| 56.p. 4.d. | VV slēdz uz **ne vairāk kā 4 gadiem** (izņēmuma kārtā ilgāk objektīvu iemeslu dēļ) |
| 56.p. 5.d. | VV ar **vienu piegādātāju** — līgumus slēdz vienkāršā konsultācijā |
| 56.p. 6.d. | VV ar **vairākiem piegādātājiem** — līgumus slēdz 3 veidos: bez atkārtotas izvērtēšanas, ar mini-konkursu vai ar pilnu atkārtotu izvērtēšanu |
| 56.p. 4.d. | Pasūtītājs **neizmanto VV, lai ierobežotu konkurenci** |

### 13a.2. Divi VV tipi datu kontekstā (kritiskais sadalījums)

| Tips | Pasūtītājs | Kur realizē | Vai redzams atvērtajos datos? |
|------|------------|-------------|-----------------------------|
| **A. Centralizētā VV** | VRAA (`reg_nr=90001733697`) | EIS e-katalogā | **JĀ** (`e_pasutijumi`, `piegades`) |
| **B. Decentralizētā VV** | Slimnīcas, LVM, universitātes, VALIC u.c. | Tieši starp pasūtītāju un piegādātāju | **NĒ** — faktiskā realizācija nav publiska |

**Datu skaitļi (no `eis.db`, 2010–2026):**
- VV līgumi KOPĀ: **46,977** par **274 mljrd EUR** griestiem
- A. Centralizētās (VRAA): 2,191 (**4.7%**) — 67.7 mljrd EUR
- B. Decentralizētās: 44,786 (**95.3%**) — 206.4 mljrd EUR

**Sekas analīzei:** Uzņēmuma profila atskaitēs VV un tiešie līgumi (`ligums_ir_vv='Nē'`) **nedrīkst** parādīties vienā summā. Skat. UZNEMUMA_PROFILS.md sadaļu 9.

---

## 13b. KATALOGA DZĪVES CIKLS UN PĀRMAIŅAS

Atbilstoši PIL 56.p. 4.d. (VV ≤4 gadi) **katalogi nav mūžīgi**.

### 13b.1. Tipiskais cikls

| Funkcija | Kataloga paaudzes datos | Cikls |
|---|---|---|
| Kancelejas preces | CI67 → CI88 → CI95 → CI109 → CI119 | 5 paaudzes 12 gadu laikā |
| Datortehnika | CI106 → CI117V → CI123V | 3 paaudzes, ~3-4 g. katra |
| Programmatūra | CI110 → CI118 → ? | 2+ paaudzes |
| Medikamenti | CI107R → NVD11R → NVD10R | 3 paaudzes |

### 13b.2. Kā notiek nomaiņa

1. VRAA izsludina **jaunu centralizētu iepirkumu** (parādās `iepirkumi`)
2. Iepirkumā uzvar **vairāki piegādātāji** (parādās `iepirkumu_rezultati` ar `ligums_ir_vv='Jā'`, jauns `kataloga_numurs`)
3. Vecais katalogs **paralēli darbojas** līdz savas VV termiņa beigām
4. Pozīcijas vecajā katalogā **pakāpeniski slēdzas** (ne visas reizē)

### 13b.3. Suffix sistēma (viens VV cikls — vairāki katalogi)

| Sufikss | Nozīme | Piemērs |
|---|---|---|
| (bāze) | Preces | CI105 (asmeņserveri) |
| **P** | Pakalpojumi/uzturēšana | CI105P, CI110P, CI118P |
| **A** | Apmācības | CI110A, CI118A |
| **N** | Nereģistrētas (medikamenti) | CI107N |
| **V/C** | Variants/apakšsegments | CI117V, CI117P, CI117C |
| **M** | Izejmateriāli | CI114M |

**Praktiski:** Uzvara CI105 (preces) NEGARANTĒ vietu CI105P (pakalpojumi) — atsevišķi iepirkumi, atsevišķi uzvarētāju saraksti.

---

## 14. IEPIRKUMU VEIDI UN NOTEIKUMI (MK NOTEIKUMI NR. 816)

> **Terminoloģija:** MK noteikumiem ir **punkti**, ne panti. Atsauces zemāk uz "MK 816 39. p." nozīmē "Ministru kabineta noteikumu Nr. 816 39. punkts".

### 14.1. Pasūtījumu veidi e-pasūtījumu apakšsistēmā

| Veids | MK 816 punkts | Apraksts | Min. piedāvājuma termiņš |
|-------|--------------|----------|--------------------------|
| **Automātiska zemākās cenas izvēle** | 38. p. | Sistēma izvēlas zemāko kataloga cenu pozīcijā — nav atkārtotas konkurences | Tūlītējs (kataloga cena) |
| **Standarta pasūtījums ar specifikāciju** | 39. p. | Pasūtītājs precizē tehniskās prasības — lejupejošā solīšana visiem pozīcijas piegādātājiem | **1 darba diena** |
| **Lielas vērtības pasūtījums** | 40. p. | Pasūtījuma summa ≥ PIL 8.p. 4.d. slieksnim — paplašināta lejupejošā solīšana | **3 darba dienas** |
| **Nedalāms pasūtījums** | 44. p. | Preču/pakalpojumu savstarpējas saderības nodrošināšana — viens piegādātājs visam pasūtījumam | Nepieciešams pamatojums |
| **Viena piegādātāja pasūtījums** | 46. p. | Tikai viens piegādātājs vai specifikācija piesaistīta konkrētam ražotājam/preču zīmei | Nepieciešams detalizēts pamatojums |

**Datu identifikācija:** atvērto datu kopā nav eksplicīta `pasūtījuma veids` lauka. Atšķirību var rekonstruēt **heiristiski** no `e_pasutijumi` (skat. KATALOGI_UN_VV_IZPRATNE.md sadaļu 4).

### 14.2. Vērtību limiti

| Noteikums | Limits | Avots |
|-----------|--------|-------|
| Pakalpojumu iepirkuma limits (MK 816 39., 44., 46. p. minētajiem pasūtījumiem) | **≤ €1 000 000** (bez PVN) | MK 816 47. p. |
| Lielas vērtības pasūtījuma slieksnis | PIL 8.p. 4.d. noteiktā summa | MK 816 40. p. |
| Centralizācijas obligātais slieksnis — tiešās pārvaldes iestādēm | ≥ **€1 000** uz 12 mēn. | PIL 17.p. 7.d. |
| Centralizācijas obligātais slieksnis — pašvaldībām | ≥ **€10 000** uz 12 mēn. | PIL 17.p. 8.d. |
| VV maksimālais termiņš | **≤ 4 gadi** (izņēmuma kārtā ilgāks) | PIL 56.p. 4.d. |
| Iepirkuma līguma grozījumu maks. pieaugums | **≤ 50%** no sākotnējās summas | PIL 61.p. 4.d. |

### 14.3. AG (atsevišķā gadījuma) pamatojuma prasības

**Kad nepieciešams pamatojums:**
- Nedalāms pasūtījums (44. pants) — savstarpējas saderības nodrošināšana
- Viena piegādātāja pasūtījums (46. pants) — tikai viens piedāvātājs vai konkrēts ražotājs/preču zīme

**Pamatojuma dokumenta saturs:**

| Sadaļa | Obligātais saturs |
|--------|------------------|
| Pasūtītāja informācija | Pasūtītāja/pakalpojuma sniedzēja nosaukums |
| Groza informācija | Atliktā groza numurs, izveides datums |
| Katalogs/pozīcija | Kataloga numurs, VV pozīciju numuri |
| Situācijas apraksts | Brīvas formas apraksts ar pamatojumu, kāpēc alternatīvi risinājumi nav iespējami |
| Nepieciešamības pamatojums | Iepirkuma nepieciešamības vai savstarpējas saderības pamatojums |
| Izmaksu analīze | Aizvietošanas izmaksas un to proporcionalitāte, risinājuma uzturēšana un ekspluatācija |
| Finanšu dati | Groza kopējās paredzamās izmaksas (EUR bez PVN), esošajā risinājumā ieguldītie līdzekļi, iespējamās aizvietošanas izmaksas, uzturēšanas gada summa |

**Iesniegšana:** Pamatojums un apliecinājumi **jāpievieno** iepirkuma grozam EIS sistēmā groza izveides laikā.

**Publiskā pieejamība:** Viena piegādātāja/preču zīmes pasūtījumam pamatojums ir publiski pieejams **3 darba dienas** pēc paziņojuma.

### 14.4. VRAA (centralizēto iepirkumu institūcijas) kontroles mehānismi

| Darbība | MK 816 punkts | Apraksts |
|---------|-------|----------|
| **Pasūtījuma pārtraukšana** | 48. p. | VRAA pārtrauc e-pasūtījumu apakšsistēmā veidotu pasūtījumu, ja: (1) trūkst dokumentu nedalāmiem/viena piegādātāja pasūtījumiem; (2) pārkāpti VV obligātie nosacījumi |
| **Atbilstības pārbaude** | 49. p. | Obligāta pārbaude, ja: (1) summa > PIL 8.p. 4.d. sliekšņa; (2) iepriekš jau bijis pārtraukts pasūtījums par to pašu preci |
| **Kvalitātes pārbaudes** | 3.15. p. | Izlases kārtībā veic atbilstības un kvalitātes pārbaudes precēm un pakalpojumiem VV ietvaros |
| **Sankcijas** | 3.15. p. | Privāto tiesību jomā piemēro VV paredzētos ierobežojumus vai soda sankcijas par VV noteikumu pārkāpumiem |

---

## 15. ATSKAITES UN AUDITS

### 15.1. Pieejamie atskaišu veidi

| Atskaite | Pieejams lomām | Parametri |
|----------|--------------|-----------|
| **Pircēja atskaite par pasūtījumiem** (īsa/detalizēta) | Iepircējs, Apstiprinātājs, Saņēmējs, Pircēja admin., Nozares ekspts., Kataloga vadītājs/admin., Sistēmas admin. | Pircējs, Bankas konts, Datumu intervāls (max 1 gads), Katalogs, Kategorija, Piegādātājs, Reģions |
| **Piegādātāja atskaite par apstiprinātiem pasūtījumiem** (īsa/detalizēta) | Piegādātājs, Piegādātāja admin., Nozares ekspts., Kataloga vadītājs/admin., Sistēmas admin. | Datumu intervāls, Katalogs, Kategorija, Piegādātājs, Pircējs, Reģions |
| **Crystal Reports atskaites** | Atkarīgs no konfigurācijas | Sagatavju parametri |

### 15.2. Audita sistēma

**Audita atskaites parametri:**

| Parametrs | Apraksts |
|-----------|----------|
| Modulis | Sistēmas moduļa nosaukums |
| Notikums | Auditējamie notikumi |
| Iespējamais pārkāpums | Pārkāpuma tips (piem., "Saglabāts administrators ar biznesa lomu") |
| Datums un laiks (no/līdz) | Periods |
| Organizācija | Organizācijas nosaukums |
| Lietotājs | Konkrēts lietotājs |
| IP adrese | Lietotāja IP |
| Notikuma rezultāts | Veiksmīgs / Neveiksmīgs / Visi |

---

## 16. PRIVĀTUMA UN DATU AIZSARDZĪBA

### 16.1. Apstrādājamie personas dati

| Kategorija | Dati |
|-----------|------|
| Identifikācijas dati | Vārds, uzvārds, personas kods, e-pasts, tālrunis |
| Autentifikācijas dati | Lietotājvārds, parole (šifrēta), kodu karte, IP adrese |
| Darījumu dati | Pasūtījumu, piegāžu, grozu informācija |

### 16.2. Datu saņēmēji

| Nr. | Saņēmēja kategorija | Apraksts |
|-----|---------------------|----------|
| 1 | **Pats lietotājs** | Pēc identitātes pārbaudes |
| 2 | **Tā paša EIS dalībnieka lietotāji** | Ar atbilstošām piekļuves tiesībām |
| 3 | **Citi EIS dalībnieki** | Pamatojoties uz noslēgtiem līgumiem |
| 4 | **Citas valsts informācijas sistēmas un reģistri** | Kvalifikācijas datu ieguvei |
| 5 | **Apstiprinātie auditori** | Sistēmas auditu veikšanai |
| 6 | **Trešās personas** | Uz tiesiska pamata tehniskajiem darbiem |
| 7 | **Valsts/pašvaldību iestādes** | Normatīvajos aktos noteiktajos gadījumos |

### 16.3. Datu glabāšanas termiņi

| Datu kategorija | Termiņš |
|----------------|---------|
| Darījumu dati (pasūtījumi, piegādes) | 10 gadi |
| Iepirkumu procedūru dokumenti | 10 gadi |
| Audita ieraksti | 3 gadi |
| Sīkdatnes (cookies) | Līdz sesijas beigām |
| Lietotāja profila dati | Kamēr profils aktīvs vai saskaņā ar normatīvajiem aktiem (PIL, Grāmatvedības likums, Arhīvu likums) |

### 16.4. Drošības pasākumi

- SSL/TLS šifrēšana
- Identifikācija un autorizācija ar lomu sistēmu
- IP līmeņa bloķēšana
- Audita pieraksti par visām lietotāju darbībām

---

## 17. SISTĒMAS KONFIGURĀCIJAS PARAMETRI

| Parametrs | Noklusētā vērtība | Apraksts |
|-----------|-------------------|----------|
| Terminu kontroles laiks | 00:30 | Ikdienas automātiskā termiņu pārbaude |
| Nepareizu autentifikācijas mēģinājumu skaits | 5 | Pēc 5x → bloķēšana |
| Paroles derīguma termiņš | 90 dienas | Obligāta nomaiņa |
| Paroles minimālais garums | 12 zīmes | Min. prasība |
| Atskaišu datumu intervāls | Max 1 gads | Atskaišu periods |
| Audita atskaišu saraksta atjaunošana | Konfigurējams (sek.) | Auto-refresh |

---

## 18. DOKUMENTĀCIJAS AVOTI

### 18.1. EIS sistēmas rokasgrāmatas un noteikumi

| Nr. | Dokuments | Fails | Apraksts |
|-----|----------|-------|----------|
| 01 | Iepircēja rokasgrāmata | `markdown/01_Iepirceja_rokasgramata.md` | Pircēja/iepircēja darba process |
| 02 | Apstiprinātāja rokasgrāmata | `markdown/02_Apstiprinataja_rokasgramata.md` | Pasūtījumu apstiprināšana |
| 03 | Saņēmēja rokasgrāmata | `markdown/03_Sanemeja_rokasgramata.md` | Piegāžu saņemšana un kvalitāte |
| 04 | Pircēja administratora rokasgrāmata | `markdown/04_Pirceja_administratora_rokasgramata.md` | Organizācijas un lietotāju pārvaldība |
| 05 | Piegādātāja rokasgrāmata | `markdown/05_Piegadataja_rokasgramata.md` | Piegādātāja darba process |
| 06 | Piegādātāja administratora rokasgrāmata | `markdown/06_Piegadataja_admin_rokasgramata.md` | Piegādātāja organizācijas pārvaldība |
| 07 | Atlikto grozu apstrāde | `markdown/07_Atlikto_grozu_apstrade.md` | Lielo pasūtījumu process |
| 08 | Preču importa rokasgrāmata | `markdown/08_Precu_importa_rokasgramata.md` | CSV datnes formāts un imports |
| 09 | Nozares eksperta rokasgrāmata | `markdown/09_Nozares_eksperta_rokasgramata.md` | Kataloga uzraudzība un kontrole |
| 10 | EIS lietošanas noteikumi | `markdown/10_EIS_lietosanas_noteikumi.md` | VRAA iekšējie noteikumi |
| 11 | EIS privātuma politika | `markdown/11_EIS_privatuma_politika.md` | Personas datu apstrāde |
| 12 | AG pamatojums | `markdown/12_AG_pamatojums.md` | Atsevišķā gadījuma pamatojuma veidlapa |

### 18.2. Normatīvie akti

| Dokuments | Fails | Apraksts |
|---|---|---|
| **Publisko iepirkumu likums (PIL)** | `markdown/PUBLISKO_IEPIRKUMU_LIKUMS.md` | Pamatlikums (90 pantu) — VV (56.p.), DIS (57.p.), centralizācija (17.p.), grozījumi (61.p.), procedūru veidi (8.p.) |
| **MK noteikumi Nr. 816** | `markdown/13_MK_noteikumi_816.md` | "Publisko elektronisko iepirkumu noteikumi" — e-pasūtījumu apakšsistēmas darbība, e-izziņu sistēma, 1. pielikums ar centralizēto preču grupām |

### 18.3. Analītiskās izpratnes dokumenti (projekta specifiskie)

| Dokuments | Fails | Apraksts |
|---|---|---|
| **DB shēma** | `../eis-db-schema.md` | SQLite datubāzes struktūra, 10 tabulas, normalizācijas lēmumi |
| **Uzņēmuma profila skill** | `../UZNEMUMA_PROFILS.md` | Tiešo līgumu vs VV nodalīšana, A/B VV grupas, kataloga dzīves cikls, sarkanie karogi |
| **Katalogu un VV izpratne** | `../KATALOGI_UN_VV_IZPRATNE.md` | PIL pantu validācija ar `eis.db`, konkurences modeļi, sistēmas nepilnību pazīmes, SQL heiristikas |
