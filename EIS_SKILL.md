# EIS atvērto datu analīzes prasmes (SKILL)

> Praktisks darba rīks EIS (Elektroniskā iepirkumu sistēma) atvērto datu analīzei. Šis fails apkopo gan teorētiskās zināšanas no Publisko iepirkumu likuma (PIL) un MK noteikumiem Nr. 816, gan empīriskos atklājumus no `eis.db` datubāzes (~9.6M ierakstu, 2010–2026), gan SQL veidnes praktiskām atskaitēm.
>
> **Lietošanas konteksts:** Žurnālistiska analīze, akadēmiska pētniecība, audita pārbaudes, uzņēmuma profila atskaites.
>
> **Patiesības avoti:**
> - PIL: [`eis-docs/markdown/PUBLISKO_IEPIRKUMU_LIKUMS.md`](eis-docs/markdown/PUBLISKO_IEPIRKUMU_LIKUMS.md) (90 panti)
> - MK 816: [`eis-docs/markdown/13_MK_noteikumi_816.md`](eis-docs/markdown/13_MK_noteikumi_816.md)
> - DB shēma: [`eis-db-schema.md`](eis-db-schema.md)
> - Datubāze: `eis.db` (SQLite, 3.88 GB, 11 tabulas)

---

## 0. Lietošanas princips

Šī faila katra prasme satur:
- **Kas tiek validēts** (skaidrs jautājums)
- **PIL/MK 816 atsauce** (kāpēc tas ir jēgpilns)
- **Datu lauki un SQL veidne**
- **Interpretācijas piezīmes** (ko skaitlis NENORĀDA)
- **Sarkanie karogi** (kad jāsāk dziļāka pārbaude)

**Galvenais princips:** Atvērtajos datos ir 2 EIS apakšsistēmas no 4 (MK 816 2.1. p.) — e-pasūtījumu un e-konkursu. Tas nozīmē, ka **~75% no centralizēto VV finansiālās realizācijas ir publiski neredzama** (skat. sadaļu 9.2). Visas atskaites jāveido ar šo robežu apzināti.

---

## 1. EIS sistēmas pamats

### 1.1. Apakšsistēmas

MK 816 2.1. p. nosaka 4 apakšsistēmas:

| # | Apakšsistēma | Datu kopa | Tabulas DB |
|---|---|---|---|
| 1 | **E-pasūtījumu apakšsistēma** (e-katalogs) | Pasūtījumi pret centralizētajām VV/DIS | `e_pasutijumi`, `piegades`, `katalogi` |
| 2 | **E-konkursu apakšsistēma** | Visi iepirkumi (izsludināšana → līgums) | `iepirkumi`, `piedavajumu_atversanas`, `iepirkumu_grozijumi`, `iepirkumu_rezultati` |
| 3 | E-izziņu apakšsistēma | Piegādātāju pārbaude no 4 reģistriem | **Nav atvērtajos datos** |
| 4 | E-izsoļu apakšsistēma | Elektroniskās izsoles | **Nav atvērtajos datos** |

### 1.2. Centralizācijas pienākums (PIL 17. p.)

| Iestādes tips | Slieksnis 12 mēn. ietvaros | Obligāti caur VRAA? |
|---|---|---|
| **Tiešās pārvaldes iestādes** | ≥ **1 000 EUR** | Jā (PIL 17.p. 7.d.) |
| **Pašvaldības un to iestādes** | ≥ **10 000 EUR** | Jā (PIL 17.p. 8.d.) |

**Centralizēto preču saraksts** — MK 816 1. pielikums (13 grupas): biroja papīrs, datortehnika, programmatūra, drukas iekārtas, mēbeles, saimniecības preces, servertehnika, mākoņskaitļošana, pārtikas preces, medikamenti (Veselības min. pārziņā), civilstāvokļa veidlapas (Tieslietu min. pārziņā).

**Izņēmumi** (PIL 17.p. 10.d.):
1. VRAA piedāvājumam nav atbilstības tehniskām prasībām
2. Iestāde var iegūt zemāku cenu (jādokumentē VRAA piedāvājums 1 darbdienu pirms)

### 1.3. Iepirkuma procedūru veidi (PIL 8. p.)

| Procedūra | PIL pants | Skaits datos | Kad lieto |
|---|---|---|---|
| Atklāts konkurss | 1.p. 3) | 136,475 | Noklusējuma procedūra virs sliekšņa |
| Mazie iepirkumi | 9. p. | 65,473 | Zem PIL 8.p. 4.d. sliekšņa |
| 2. pielikuma pakalpojumi | 10. p. | 9,809 | Sociālie/īpašie pakalpojumi |
| Slēgts konkurss | 1.p. 31) | 3,011 | Tikai uzaicinātie |
| Sarunu procedūra | 1.p. 30) | 4,294 | PIL noteikti gadījumi |
| Konkursa procedūra ar sarunām | 1.p. 15) | 279 | Kad atklāts konkurss neder |
| Konkursa dialogs | 1.p. 14) | 52 | Sarežģīti iepirkumi |
| Metu konkurss | 1.p. 18) | 196 | Projektēšanas idejas |
| Inovācijas partnerības procedūra | 1.p. 12) | 1 | Inovāciju izstrāde |

**89% iepirkumu** = atklāts konkurss + mazie iepirkumi.

---

## 2. Trīs iepirkumu rezultātu tipi — KRITISKAIS PAMATS

Visa pareizā analīze sākas ar šo trīs tipu atšķirību. **Bez tās rezultāti būs sistēmiski kļūdaini**.

| Tips | `liguma_dok_veids` | `ligums_ir_vv` | Pasūtītājs | Kur redzami ieņēmumi |
|---|---|---|---|---|
| **T. Tiešais līgums** | `'Līgums'` | `'Nē'` | Jebkurš | `iepirkumu_rezultati.aktuala_summa` = faktiskā nauda |
| **V₁. Centralizētā VV** | `'Līgums'` | `'Jā'` | VRAA (`reg_nr=90001733697`) | `e_pasutijumi`/`piegades` caur katalogu |
| **V₂. Decentralizētā VV** | `'Līgums'` | `'Jā'` | Jebkura cita iestāde | **NEREDZAMI** atvērtajos datos |

**Skaitliskā realitāte (eis.db 2010–2026):**

```
KOPĀ līgumi: 252,181 + 26,032 grozījumi + 287 izbeigšanas

Tiešie (T):        202,223 (80%)  → 132 mljrd EUR
VV kopā:            49,958 (20%)  → 274 mljrd EUR griesti
├── V₁ (VRAA):       2,191 (4.4%) →  67.7 mljrd EUR
└── V₂ (citi):      47,767 (95.6%) → 206.4 mljrd EUR
```

**Stingrais noteikums:** `aktuala_summa` ir faktiskā nauda **tikai T tipam**. V₁ un V₂ summas ir **augšējie griesti**, ne ieņēmumi (PIL 11.p. 12.d.).

---

## 3. Galvenās analītiskās prasmes

### 3.1. Uzņēmuma faktiskie ieņēmumi (pareizi)

**Jautājums:** Cik konkrēts uzņēmums faktiski nopelnījis EIS sistēmā?

**Risks:** Sasummēšana ar VV griestiem dod ~2× pārvērtējumu.

**SQL veidne:**

```sql
WITH vraa AS (SELECT org_id FROM organizacijas WHERE reg_nr = '90001733697')
SELECT
  -- T: Tiešie līgumi (faktiskā nauda)
  COALESCE((SELECT SUM(ir.aktuala_summa) FROM iepirkumu_rezultati ir
            JOIN organizacijas o ON ir.uzvaretaja_org_id = o.org_id
            WHERE o.reg_nr = ?
              AND ir.liguma_dok_veids = 'Līgums'
              AND ir.ligums_ir_vv = 'Nē'), 0) AS T_tiesie_eur,

  -- V₁ realizācija caur katalogu (faktiskā nauda no centralizētajām VV)
  COALESCE((SELECT SUM(ep.summa_bez_pvn) FROM e_pasutijumi ep
            JOIN organizacijas o ON ep.piegadataja_org_id = o.org_id
            WHERE o.reg_nr = ?), 0) AS V1_kataloga_eur,

  -- V₁ griesti (TIKAI atsaucei, NE ieņēmumi)
  COALESCE((SELECT SUM(ir.aktuala_summa) FROM iepirkumu_rezultati ir
            JOIN organizacijas o ON ir.uzvaretaja_org_id = o.org_id
            WHERE o.reg_nr = ?
              AND ir.liguma_dok_veids = 'Līgums'
              AND ir.ligums_ir_vv = 'Jā'
              AND ir.pasutitaja_org_id = (SELECT org_id FROM vraa)), 0) AS V1_griesti_atsaucei,

  -- V₂ griesti (TIKAI atsaucei, realizācija nav redzama)
  COALESCE((SELECT SUM(ir.aktuala_summa) FROM iepirkumu_rezultati ir
            JOIN organizacijas o ON ir.uzvaretaja_org_id = o.org_id
            WHERE o.reg_nr = ?
              AND ir.liguma_dok_veids = 'Līgums'
              AND ir.ligums_ir_vv = 'Jā'
              AND ir.pasutitaja_org_id != (SELECT org_id FROM vraa)), 0) AS V2_griesti_atsaucei;
```

**MĒRĀMIE ieņēmumi atvērtajos datos = T_tiesie + V₁_kataloga**

**Sarkanie karogi:**
- V₁_griesti / V₁_kataloga < 5% → "Mirusi" VV kvalifikācija
- V₂_griesti > 10× T_tiesie → uzņēmums galvenokārt darbojas neredzamajā tirgū (med./mežs/aizsardzība)

---

### 3.2. Konkurence iepirkumā (atklātie iepirkumi)

**Jautājums:** Cik īsta konkurence ir konkrētam iepirkumam vai iepirkumu kategorijai?

**PIL pamats:** PIL 2. p. — likuma mērķis nodrošināt "piegādātāju brīvu konkurenci".

**Galvenie rādītāji:**

```sql
-- Vidējais pretendentu skaits pa procedūru veidiem
SELECT i.proceduras_veids,
       COUNT(DISTINCT i.iepirkuma_id) AS iepirkumu_sk,
       ROUND(AVG(pa_sk.cnt), 2) AS vid_pretendenti,
       MAX(pa_sk.cnt) AS max_pretendenti,
       SUM(CASE WHEN pa_sk.cnt = 1 THEN 1 ELSE 0 END) AS viena_pretendenta_iep,
       ROUND(100.0 * SUM(CASE WHEN pa_sk.cnt = 1 THEN 1 ELSE 0 END) /
             COUNT(DISTINCT i.iepirkuma_id), 1) AS viena_proc
FROM iepirkumi i
LEFT JOIN (
  SELECT iepirkuma_id, datu_gads,
         COUNT(DISTINCT pretendenta_org_id) AS cnt
  FROM piedavajumu_atversanas
  GROUP BY iepirkuma_id, datu_gads
) pa_sk ON pa_sk.iepirkuma_id = i.iepirkuma_id AND pa_sk.datu_gads = i.datu_gads
WHERE i.datu_gads >= 2023
GROUP BY i.proceduras_veids
ORDER BY iepirkumu_sk DESC;
```

**Sarkanie karogi:**
- "Atklāts konkurss" ar 1 pretendentu (kā Sarunu procedūra), ja vidējais segmentā ir ≥3 — varētu būt nepamatota tehnisko prasību sašaurināšana
- Pasūtītāja "1 pretendenta %" >40% — sistēmiska konkurences trūkuma pazīme

---

### 3.3. Konkurence katalogā (e-pasūtījumu pozīcijas)

**Jautājums:** Vai konkrētajā kataloga pozīcijā ir reāla konkurence vai monopols?

**PIL pamats:** PIL 56.p. 4.d. "Pasūtītājs neizmanto vispārīgo vienošanos, lai ierobežotu konkurenci."

**Galvenais mērs — HHI (Herfindahl-Hirschman Index):**

```sql
WITH pieg_dalas AS (
  SELECT k.kataloga_numurs, ep.pozicijas_numurs,
         ep.piegadataja_org_id,
         SUM(ep.summa_bez_pvn) AS pieg_summa
  FROM e_pasutijumi ep
  JOIN katalogi k ON ep.kataloga_id = k.kataloga_id
  WHERE ep.pozicijas_numurs IS NOT NULL
    AND ep.datu_gads >= 2023
  GROUP BY k.kataloga_numurs, ep.pozicijas_numurs, ep.piegadataja_org_id
),
poz_kop AS (
  SELECT kataloga_numurs, pozicijas_numurs,
         SUM(pieg_summa) AS kopsumma,
         COUNT(*) AS piegadataju_sk
  FROM pieg_dalas
  GROUP BY kataloga_numurs, pozicijas_numurs
)
SELECT p.kataloga_numurs, p.pozicijas_numurs,
       p.piegadataju_sk,
       p.kopsumma,
       ROUND(SUM(POWER(100.0 * pd.pieg_summa / p.kopsumma, 2)), 0) AS hhi
FROM pieg_dalas pd
JOIN poz_kop p USING (kataloga_numurs, pozicijas_numurs)
WHERE p.kopsumma >= 100000
GROUP BY p.kataloga_numurs, p.pozicijas_numurs
ORDER BY hhi DESC, p.kopsumma DESC;
```

**HHI interpretācija:**
- HHI <2500 → veselīga konkurence
- HHI 2500–5000 → mērena koncentrācija
- **HHI >5000 → augsta koncentrācija (uzmanība)**
- HHI = 10,000 → pilnīgs monopols

**Sarkanie karogi:**
- HHI >5000 visos kataloga gados → strukturāls monopols
- Vairākas (>10) pozīcijas vienā katalogā ar HHI >9000 → katalogs efektīvi kontrolēts

---

### 3.4. Pozīciju popularitāte un kataloga dzīves cikls

**Jautājums:** Kuras pozīcijas ir aktīvākās, kuras "mirušas", kā mainās piegādātāju struktūra laika gaitā?

**PIL pamats:** PIL 56.p. 4.d. — VV līdz 4 gadiem. Empīriski kataloga paaudzes ir 3–5 gadi.

**Pozīciju aktivitāte pa gadiem:**

```sql
SELECT k.kataloga_numurs, ep.pozicijas_numurs,
       MIN(ep.datu_gads) AS pirmais_g,
       MAX(ep.datu_gads) AS pedejais_g,
       MAX(ep.datu_gads) - MIN(ep.datu_gads) + 1 AS dzives_ilgums,
       COUNT(*) AS pasut_sk,
       SUM(ep.summa_bez_pvn) AS kopsumma,
       COUNT(DISTINCT ep.piegadataja_org_id) AS unik_pieg
FROM e_pasutijumi ep
JOIN katalogi k ON ep.kataloga_id = k.kataloga_id
WHERE ep.pozicijas_numurs IS NOT NULL
GROUP BY k.kataloga_numurs, ep.pozicijas_numurs
ORDER BY kopsumma DESC;
```

**Kataloga paaudžu identifikācija (TOP populārākie pa funkciju):**
- Kancelejas: CI67 (2013-14) → CI88 (2014-16) → CI95 (2016-18) → CI109 (2017-21) → **CI119 (2021-25)**
- Datortehnika: CI106 → CI117V → **CI123V**
- Programmatūra: CI110 → **CI118** → (gaida 2025 jauno)
- Medikamenti: CI107R → NVD11R → **NVD10R**

**Suffix konvencijas (kā viens VV cikls rada vairākus katalogus):**

| Sufikss | Nozīme |
|---|---|
| (bāze) | Preces |
| **P** | Pakalpojumi (uzturēšana) |
| **A** | Apmācības kursi |
| **N** | Nereģistrētas (medikamentos) |
| **V/C** | Variants/apakšsegments |
| **M** | Izejmateriāli |

**Sarkanie karogi:**
- Pozīcija aktīva 5+ gadus ar to pašu vienīgo piegādātāju → strukturāls monopols
- Uzņēmuma TOP katalogs tuvojas dzīves cikla beigām → migrācijas risks
- 25% pozīciju visā EIS nodzīvo tikai 1 gadu (empīriski) — eksperimenti vai cenas neatbilstība

---

### 3.5. Pasūtītāju koncentrācija

**Jautājums:** Vai konkrēts uzņēmums sistemātiski atkarīgs no viena vai dažiem pasūtītājiem?

**Interpretācija:** Augsta koncentrācija = augsts klienta atkarības risks + jautājums par neatkarīgu uzvarēšanu konkursos.

```sql
WITH uz_pasutitajiem AS (
  SELECT ir.pasutitaja_org_id,
         COUNT(DISTINCT ir.iepirkuma_id) AS ligumu_sk,
         SUM(ir.aktuala_summa) AS summa
  FROM iepirkumu_rezultati ir
  JOIN organizacijas o ON ir.uzvaretaja_org_id = o.org_id
  WHERE o.reg_nr = ?
    AND ir.liguma_dok_veids = 'Līgums' AND ir.ligums_ir_vv = 'Nē'
  GROUP BY ir.pasutitaja_org_id
),
totals AS (SELECT SUM(summa) AS total FROM uz_pasutitajiem)
SELECT po.nosaukums, up.ligumu_sk, up.summa,
       ROUND(100.0 * up.summa / t.total, 1) AS proc_no_kopsk
FROM uz_pasutitajiem up
JOIN totals t ON 1=1
JOIN organizacijas po ON up.pasutitaja_org_id = po.org_id
ORDER BY up.summa DESC
LIMIT 10;
```

**Koncentrācijas līmeņi:**
- TOP-1 >50% → **Augsta atkarība**
- TOP-3 30–50% → Mērena
- TOP-3 <30% → Diversificēts

---

### 3.6. Iepirkuma tēmas un nozaru analīze (CPV)

**Jautājums:** Kāda ir nozaru aktivitāte, koncentrācija, pieaugums?

**Datu lauks:** `iepirkumi.cpv_kods_galvenais` — formāts `"45233200-1 Dažādi ceļu seguma būvdarbi"` (kods + nosaukums vienā laukā).

**CPV 2-ciparu līmenis = nozare:**

| CPV-2 | Nozare | Iepirkumu sk. (datos) |
|---|---|---|
| 45 | Būvdarbi | 20,765 |
| 71 | Profesionālie pakalpojumi | 9,165 |
| 33 | Medicīnas ierīces | 7,359 |
| 79 | Biznesa pakalpojumi | 5,346 |
| 09 | Naftas produkti, enerģija | 4,876 |
| 72 | IT pakalpojumi | — |
| 50 | Transporta pakalpojumi | — |
| 30 | Biroja iekārtas | — |

**SQL — uzņēmuma nozaru sadalījums:**

```sql
SELECT substr(i.cpv_kods_galvenais, 1, 2) AS cpv2,
       substr(i.cpv_kods_galvenais, 6, 50) AS apraksts,
       COUNT(DISTINCT ir.iepirkuma_id) AS ligumi,
       SUM(ir.aktuala_summa) AS summa,
       ROUND(100.0 * SUM(ir.aktuala_summa) /
             SUM(SUM(ir.aktuala_summa)) OVER (), 1) AS proc
FROM iepirkumu_rezultati ir
JOIN iepirkumi i ON ir.iepirkuma_id = i.iepirkuma_id AND ir.datu_gads = i.datu_gads
JOIN organizacijas o ON ir.uzvaretaja_org_id = o.org_id
WHERE o.reg_nr = ?
  AND ir.liguma_dok_veids = 'Līgums' AND ir.ligums_ir_vv = 'Nē'
  AND i.cpv_kods_galvenais IS NOT NULL
GROUP BY cpv2
ORDER BY summa DESC;
```

**Sarkanie karogi:**
- 1 CPV >80% no uzņēmuma ieņēmumiem → šaurā specializācija (lielas risks pie nozares lejupslīdes)
- Uzņēmums uzvar CPV, kur tā pamata reģistrētajai darbībai nav saistības — pārbaudīt

---

### 3.7. PLG (patiesie labuma guvēji) — uzņēmumu grupu un kontroles ķēžu atklāšana

**PIL pamats:** Nav tiešs (regulē UR), bet kritisks **konkurences validācijai** — uzņēmumi ar to pašu PLG nav neatkarīgi konkurenti.

**Kompozītais identifikators:** `vards + uzvards + pers_kods_maskets` (148K unikālas personas no 196K ierakstu).

**Ārvalstniekiem:** `vards + uzvards + dzimsanas_datums + valstspiederiba` (7,138 personas ar tukšu maskēto kodu).

**Grupas identifikācija:**

```sql
-- TOP personas, kas kontrolē vairākus EIS piegādātājus
SELECT plg.vards, plg.uzvards, plg.pers_kods_maskets,
       COUNT(DISTINCT o.org_id) AS uznemumi,
       GROUP_CONCAT(DISTINCT o.nosaukums, ' | ') AS saraksts
FROM patiesie_labuma_guveji plg
JOIN organizacijas o ON plg.tiesibu_subjekta_reg_nr = o.reg_nr
WHERE o.ir_piegadatajs = 1
GROUP BY plg.vards, plg.uzvards, plg.pers_kods_maskets
HAVING uznemumi >= 3
ORDER BY uznemumi DESC;
```

---

## 4. Sarkanie karogi un izmeklēšanas modeļi

### 4.1. 🚩 Phantom piedāvājumi (PLG grupās)

**Definīcija:** Vairāki vienas PLG grupas uzņēmumi piedalās tajā pašā iepirkumā, radot konkurences ilūziju.

**Atklāšanas vaicājums:**

```sql
WITH plg_grupas AS (
  SELECT plg.vards || ' ' || plg.uzvards || ' (' || plg.pers_kods_maskets || ')' AS persona,
         o.org_id
  FROM patiesie_labuma_guveji plg
  JOIN organizacijas o ON plg.tiesibu_subjekta_reg_nr = o.reg_nr
  WHERE o.ir_piegadatajs = 1
)
SELECT pg.persona,
       pa.iepirkuma_id, pa.datu_gads,
       COUNT(DISTINCT pg.org_id) AS grupas_dalibnieki,
       GROUP_CONCAT(DISTINCT o.nosaukums) AS uznemumi,
       po.nosaukums AS pasutitajs,
       i.iepirkuma_nosaukums,
       GROUP_CONCAT(DISTINCT pa.pretendenta_iesniegsanas_laiks) AS laiki
FROM piedavajumu_atversanas pa
JOIN plg_grupas pg ON pa.pretendenta_org_id = pg.org_id
JOIN organizacijas o ON pa.pretendenta_org_id = o.org_id
JOIN iepirkumi i ON pa.iepirkuma_id = i.iepirkuma_id AND pa.datu_gads = i.datu_gads
JOIN organizacijas po ON i.pasutitaja_org_id = po.org_id
GROUP BY pg.persona, pa.iepirkuma_id, pa.datu_gads
HAVING grupas_dalibnieki >= 2
ORDER BY grupas_dalibnieki DESC, pa.datu_gads DESC;
```

**Stipru pierādījumu pazīmes:**
- Iesniegumi sekunžu attālumā (Aigara Ceruša gadījumā 87s) → vienots iesniedzējs
- Identiski iesniegšanas laiki līdz sekundei → automatizēta darbplūsma
- Grupa "māsa" konsekventi piedalās, bet nekad neuzvar → paredzami pārspētie piedāvājumi

### 4.2. 🚩 "Piemērotās" kataloga pozīcijas

**Definīcija:** Pozīcija ar 1 piegādātāju + 1 dominējošu pircēju ilgākā periodā.

**Atklāšanas vaicājums:**

```sql
SELECT k.kataloga_numurs, ep.pozicijas_numurs,
       opg.nosaukums AS piegadatajs,
       opc.nosaukums AS pasutitajs,
       SUM(ep.summa_bez_pvn) AS summa,
       COUNT(*) AS pas_sk,
       MIN(ep.datu_gads) || '-' || MAX(ep.datu_gads) AS periods
FROM e_pasutijumi ep
JOIN katalogi k ON ep.kataloga_id = k.kataloga_id
JOIN organizacijas opg ON ep.piegadataja_org_id = opg.org_id
JOIN organizacijas opc ON ep.pasutitaja_org_id = opc.org_id
WHERE ep.pozicijas_numurs IS NOT NULL
GROUP BY k.kataloga_numurs, ep.pozicijas_numurs
HAVING COUNT(DISTINCT ep.piegadataja_org_id) = 1
   AND COUNT(DISTINCT ep.pasutitaja_org_id) = 1
   AND summa >= 50000
   AND pas_sk >= 3
   AND MAX(ep.datu_gads) >= 2023
ORDER BY summa DESC;
```

**Interpretācija:**
- Var būt **likumīga specifika** (MK 816 46. p. — viena piegādātāja pasūtījums)
- Bet ja pasūtītājs daudz pozīcijas iepērk šādi (>20 pozīciju ar 1+1) → sistēmiska zema diversifikācija

### 4.3. 🚩 Iepirkumu sadalīšana zem sliekšņa (PIL 11. p.)

**Definīcija:** Pasūtītājs sadala lielu iepirkumu vairākos mazos, lai izvairītos no atklātā konkursa.

**PIL 11. p. nosaka:** Paredzamā līgumcena visiem secīgi vai vienlaicīgi rīkotajiem identiska veida iepirkumiem jāsummē.

**Atklāšanas vaicājums:**

```sql
-- Pasūtītāji ar daudziem "Mazajiem iepirkumiem" tieši zem sliekšņa
-- (PIL 8.p. 4.d. slieksnis 2024: piegādēm 70K, pakalpojumiem 70K, būvdarbiem 170K bez PVN)
SELECT po.nosaukums, i.iepirkuma_prieksmeta_veids,
       COUNT(*) AS mazo_iepirkumu_sk,
       AVG(i.planota_ligumcena) AS vid_summa,
       SUM(i.planota_ligumcena) AS kopsumma
FROM iepirkumi i
JOIN organizacijas po ON i.pasutitaja_org_id = po.org_id
WHERE i.proceduras_veids = 'Mazie iepirkumi'
  AND i.planota_ligumcena BETWEEN 50000 AND 70000  -- tuvu slieksnim
  AND i.datu_gads >= 2023
GROUP BY i.pasutitaja_org_id, i.iepirkuma_prieksmeta_veids
HAVING mazo_iepirkumu_sk >= 5  -- vairāk nekā gadījuma rakstura
ORDER BY mazo_iepirkumu_sk DESC;
```

### 4.4. 🚩 Līguma summas pieaugums >50% (PIL 61. p. 4. d.)

**Definīcija:** PIL 61.p. 4.d. aizliedz secīgu grozījumu kopējam pieaugumam pārsniegt 50% no sākotnējās līgumcenas.

```sql
SELECT po.nosaukums AS pasutitajs,
       uo.nosaukums AS piegadatajs,
       i.iepirkuma_nosaukums,
       ir.sakotneja_summa, ir.aktuala_summa,
       ROUND(100.0 * (ir.aktuala_summa - ir.sakotneja_summa) / ir.sakotneja_summa, 1) AS pieaugums_proc,
       ir.liguma_noslegsanas_datums
FROM iepirkumu_rezultati ir
JOIN organizacijas po ON ir.pasutitaja_org_id = po.org_id
JOIN organizacijas uo ON ir.uzvaretaja_org_id = uo.org_id
JOIN iepirkumi i ON ir.iepirkuma_id = i.iepirkuma_id AND ir.datu_gads = i.datu_gads
WHERE ir.liguma_dok_veids = 'Līgums'
  AND ir.ligums_ir_vv = 'Nē'
  AND ir.sakotneja_summa > 0
  AND ir.aktuala_summa / ir.sakotneja_summa > 1.5  -- >50% pieaugums
ORDER BY pieaugums_proc DESC;
```

**Piezīme:** Atsevišķi grozījumi atļauti ar papildu nelielu pieaugumu (PIL 61.p. 5.d. — līdz 10% piegādēm, 15% būvdarbiem), tāpēc 50-65% pieaugums vēl var būt likumīgs ar pamatojumu.

### 4.5. 🚩 VV "mirušā" kvalifikācija

**Definīcija:** Uzņēmums ieguva centralizēto VV (V₁), bet faktiski katalogā nesaņem pasūtījumus.

```sql
WITH vraa AS (SELECT org_id FROM organizacijas WHERE reg_nr = '90001733697'),
v1_uzv AS (
  SELECT DISTINCT ir.uzvaretaja_org_id AS org_id, ir.aktuala_summa AS griesti
  FROM iepirkumu_rezultati ir
  WHERE ir.liguma_dok_veids = 'Līgums' AND ir.ligums_ir_vv = 'Jā'
    AND ir.pasutitaja_org_id = (SELECT org_id FROM vraa)
),
v1_realiz AS (
  SELECT piegadataja_org_id, SUM(summa_bez_pvn) AS summa
  FROM e_pasutijumi GROUP BY piegadataja_org_id
)
SELECT o.nosaukums, v.griesti,
       COALESCE(r.summa, 0) AS realizetie,
       ROUND(100.0 * COALESCE(r.summa, 0) / v.griesti, 1) AS izmant_proc
FROM v1_uzv v
JOIN organizacijas o ON v.org_id = o.org_id
LEFT JOIN v1_realiz r ON v.org_id = r.piegadataja_org_id
WHERE v.griesti > 100000
ORDER BY izmant_proc ASC;
```

### 4.6. 🚩 Specifikācijas piesaiste ražotājam (PIL 20. p.)

**Definīcija:** PIL 20. p. aizliedz tehniskās specifikācijas saistīt ar konkrētu ražotāju/preču zīmi.

**Indikators datos:** `iepirkumi.iepirkuma_nosaukums` satur ražotāja nosaukumu vai konkrētu produkta modeli.

```sql
-- Iepirkumi ar ražotāja nosaukumu virsrakstā
SELECT i.iepirkuma_id, po.nosaukums AS pasutitajs,
       i.iepirkuma_nosaukums, i.proceduras_veids
FROM iepirkumi i
JOIN organizacijas po ON i.pasutitaja_org_id = po.org_id
WHERE i.iepirkuma_nosaukums LIKE '%Microsoft%'  -- vai cits zīmols
   OR i.iepirkuma_nosaukums LIKE '%Cisco%'
   OR i.iepirkuma_nosaukums LIKE '%Oracle%'
   OR i.iepirkuma_nosaukums LIKE '%SAP%'
ORDER BY i.izsludinasanas_datums DESC;
```

### 4.7. 🚩 Pasūtītāja "savs piegādātājs"

**Definīcija:** Viens piegādātājs aizņem >50% no pasūtītāja kopējiem IT/specifiskās jomas izdevumiem.

```sql
WITH par_pasut AS (
  SELECT ir.pasutitaja_org_id, ir.uzvaretaja_org_id,
         COUNT(*) AS ligumi,
         SUM(ir.aktuala_summa) AS summa
  FROM iepirkumu_rezultati ir
  WHERE ir.liguma_dok_veids = 'Līgums' AND ir.ligums_ir_vv = 'Nē'
  GROUP BY ir.pasutitaja_org_id, ir.uzvaretaja_org_id
),
pasut_kopa AS (
  SELECT pasutitaja_org_id, SUM(summa) AS kopa FROM par_pasut GROUP BY pasutitaja_org_id
)
SELECT po.nosaukums AS pasutitajs, uo.nosaukums AS piegadatajs,
       p.ligumi, p.summa,
       ROUND(100.0 * p.summa / pk.kopa, 1) AS proc_no_pasutitaja
FROM par_pasut p
JOIN pasut_kopa pk USING (pasutitaja_org_id)
JOIN organizacijas po ON p.pasutitaja_org_id = po.org_id
JOIN organizacijas uo ON p.uzvaretaja_org_id = uo.org_id
WHERE pk.kopa > 1000000 AND p.summa / pk.kopa > 0.5
ORDER BY proc_no_pasutitaja DESC;
```

### 4.8. 🚩 Sagatavošanas darba priekšrocība (SPEC→IMPL paterns)

**Definīcija:** Pretendents (vai cits PLG grupas uzņēmums) iepriekš ir uzvarējis "sagatavošanas" līgumu (tehniskā specifikācija, audits, konsultācijas, priekšizpēte, stratēģija) tajā pašā pasūtītāja iestādē — un pēc tam grupa uzvar "izpildes" līgumu (sistēmas izstrāde, ieviešana, uzturēšana, testēšana) par to pašu vai saistīto risinājumu.

**PIL pamats:** PIL 41. p. 12. d. 1) — pasūtītājam ir tiesības izslēgt pretendentu, kurš ir piedalījies sagatavošanas pasākumos pirms iepirkuma izsludināšanas, ja tas iegūst nepamatotu konkurences priekšrocību (ko nevar kompensēt ar mazāk ierobežojošiem pasākumiem). Skat. arī PIL 18. p. 2.d. (apspriedes ar piegādātājiem) un PIL 25. p. (iepirkuma komisijas neatkarība).

**Risks:** Sagatavošanas līgums (parasti 25-50K EUR) "atver durvis" uz daudzkārt lielāku izpildes līgumu (no 100K līdz vairākiem miljoniem EUR). Empīriski viens Ceruša grupas piemērs: ~316K EUR SPEC līgumi sniedz pieeju ~14.8 milj. EUR IMPL līgumiem (~47:1 attiecība).

**Sevišķi smaga forma:** SPEC un IMPL līgumi ir **dažādos PLG grupas uzņēmumos** — formāli pasūtītājs nevar piemērot PIL 41.p. 12.d. izslēgšanu, jo izpildītājs ir "cits" uzņēmums, lai gan kontroles ķēde ir tā pati.

**SQL veidne — pielāgojama jebkurai PLG grupai:**

```sql
-- ============================================================
-- SPEC → IMPL paterna meklēšana PLG grupā
-- ============================================================
-- Pielāgojiet @grupas_reg_nrs sarakstu vai PLG identifikatoru zemāk.
-- Piemērs: Aigars Ceruss (130573-*****) → 8 uzņēmumi.

WITH grupas_uznemumi AS (
  -- ===== A variants: tiešs reg_nr saraksts (ātrāks) =====
  SELECT org_id, reg_nr, nosaukums FROM organizacijas
  WHERE reg_nr IN (
    '40103167628',  -- Corporate Consulting SIA
    '40103307781',  -- Corporate Systems SIA
    '40103347036',  -- E-Synergy SIA
    '40003244827',  -- IT Latvija AS
    '40103244927',  -- Corporate Services SIA
    '40003861875',  -- Corporate Solutions SIA
    '40103823827',  -- SIA NET-Core
    '40003924899'   -- Monitoringa Centrs SIA
  )

  -- ===== B variants: caur PLG kompozīto indeksu =====
  -- SELECT DISTINCT o.org_id, o.reg_nr, o.nosaukums
  -- FROM patiesie_labuma_guveji plg
  -- JOIN organizacijas o ON plg.tiesibu_subjekta_reg_nr = o.reg_nr
  -- WHERE plg.vards = 'Aigars'
  --   AND plg.uzvards = 'Ceruss'
  --   AND plg.pers_kods_maskets = '130573-*****'
),

ligumi_kategorizeti AS (
  SELECT
    ir.iepirkuma_id, ir.datu_gads,
    ir.pasutitaja_org_id, opg.nosaukums AS pasutitajs,
    g.nosaukums AS grupas_uzn,
    i.iepirkuma_nosaukums,
    ir.aktuala_summa,
    ir.liguma_noslegsanas_datums AS datums,
    ir.ligums_ir_vv,
    i.cpv_kods_galvenais,
    CASE
      -- SPEC: sagatavošanas darbi (specifikācija, audits, konsultācijas)
      WHEN lower(i.iepirkuma_nosaukums) LIKE '%audit%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%konsultāc%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%konsult.%pakalp%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%priekšizpēt%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%situācijas izpēt%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%analīz%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%koncepcij%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%stratēģij%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%tehniskās specifikāc%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%specifikācijas izstr%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%specifikāciju izstr%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%specifikācijas sagatav%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%plāna izstr%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%pamatojum%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%iepirkuma atbalst%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%arhitekt.%izstr%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%projektēš%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%projektu pieteikum%'
        THEN 'SPEC'
      -- IMPL: izstrāde, uzturēšana, ieviešana (faktiskā izpilde)
      WHEN lower(i.iepirkuma_nosaukums) LIKE '%sistēmas izstr%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%sistēmu izstr%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%platformas izstr%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%risinājuma izstr%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%risinājuma iegād%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%programmatūras izstr%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%programmatūras pakalp%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%pilnveidoš%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%uzturēš%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%apkalpoš%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%papildinājumu izstr%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%ievies%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%modernizē%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%modific%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%testēš%'
        OR lower(i.iepirkuma_nosaukums) LIKE '%pielāgoš%'
        THEN 'IMPL'
      ELSE NULL
    END AS kategorija
  FROM iepirkumu_rezultati ir
  JOIN grupas_uznemumi g ON ir.uzvaretaja_org_id = g.org_id
  JOIN organizacijas opg ON ir.pasutitaja_org_id = opg.org_id
  JOIN iepirkumi i ON ir.iepirkuma_id = i.iepirkuma_id AND ir.datu_gads = i.datu_gads
  WHERE ir.liguma_dok_veids = 'Līgums'
)

SELECT
  s.pasutitajs,
  s.grupas_uzn  AS spec_uznemums,
  s.iepirkuma_nosaukums AS spec_iepirkums,
  s.aktuala_summa  AS spec_summa,
  s.datums         AS spec_datums,
  imp.grupas_uzn   AS impl_uznemums,
  imp.iepirkuma_nosaukums AS impl_iepirkums,
  imp.aktuala_summa AS impl_summa,
  imp.datums        AS impl_datums,
  CAST(JULIANDAY(imp.datums) - JULIANDAY(s.datums) AS INTEGER) AS dienas_starpiba,
  CASE WHEN s.grupas_uzn != imp.grupas_uzn
       THEN '*** DAŽĀDI grupas uzņēmumi ***'
       ELSE 'Tas pats uzņēmums' END AS modelis
FROM ligumi_kategorizeti s
JOIN ligumi_kategorizeti imp
  ON s.pasutitaja_org_id = imp.pasutitaja_org_id      -- tas pats pircējs
  AND s.kategorija = 'SPEC'
  AND imp.kategorija = 'IMPL'
  AND s.datums IS NOT NULL AND imp.datums IS NOT NULL
  AND JULIANDAY(imp.datums) > JULIANDAY(s.datums)     -- IMPL pēc SPEC
  AND JULIANDAY(imp.datums) - JULIANDAY(s.datums)
      BETWEEN 7 AND 1095                              -- nedēļa līdz 3 gadi
ORDER BY imp.aktuala_summa DESC NULLS LAST;
```

**Interpretācijas piezīmes:**

1. **Atslēgvārdu metode ir heiristiska.** Daži līgumi būs nepareizi klasificēti (89 no 184 līgumu Ceruša gadījumā bija "nekategorizēti"). Manuālā pārbaude ar `iepirkuma_nosaukums` ir obligāta.

2. **Laika logs 7–1095 dienas** (3 gadi) — pielāgojams. Īsākam logam (60–365 d.) — visdrošākie paterni. Garākam (>2 gadi) — pieaug "nejaušības" risks.

3. **"Dažādi grupas uzņēmumi" modelis (PIL 41. p. 12. d. apiešana):**
   - **Visstiprākais pierādījums** sagatavošanas darba priekšrocībai
   - SPEC uzņēmums kvalifikācijā netiek izslēgts, jo izpildītājs ir cits uzņēmums
   - Bet kontroles ķēde (PLG) ir tā pati — naudas plūsma paliek grupā

4. **"Tas pats uzņēmums" modelis:**
   - PIL 41. p. 12. d. eksplicīti pieprasa izslēgšanu, ja "nepamatota konkurences priekšrocība" nevar tikt kompensēta
   - Tomēr datos redzams, ka šis nenotiek

**Sarkanie karogi pa prioritātēm:**

| Prioritāte | Pazīme | Interpretācija |
|---|---|---|
| 🔴 **Augsta** | DAŽĀDI grupas uzņēmumi + IMPL summa > 1M EUR | Sistēmiska 41.p. apiešana ar lieliem skaitļiem |
| 🔴 **Augsta** | SPEC = drošības audits + IMPL = tās pašas sistēmas izstrāde | Tiešs konfliktu interešu pārkāpums audita neatkarībai |
| 🟡 Vidēja | SPEC = tehniskā specifikācija + IMPL = tā paša risinājuma iegāde | Klasiskais 41.p. 12.d. izslēgšanas pamats |
| 🟡 Vidēja | Vairāk nekā 3 SPEC→IMPL paterni vienai grupai pie viena pasūtītāja | Sistemātiskas attiecības, ne nejaušības |
| 🟢 Zemāka | SPEC = vispārīgas konsultācijas + IMPL = nesaistīts projekts | Var būt nejaušība |

**Padziļināta pārbaude:**

```sql
-- Pirms publicēšanas pārbaudi:
-- 1) Vai SPEC iepirkumā bijuši citi pretendenti? (vai bija konkurence pat SPEC posmā)
SELECT COUNT(DISTINCT pretendenta_org_id) AS pretendenti_spec
FROM piedavajumu_atversanas WHERE iepirkuma_id = ? AND datu_gads = ?;

-- 2) Vai IMPL iepirkumā uzvarētājs bijis vienīgais pretendents?
SELECT pa.pretendenta_nosaukums,
       CASE WHEN ir.uzvaretaja_org_id = pa.pretendenta_org_id
            THEN 'UZVARĒJA' ELSE 'zaudēja' END AS rezultats
FROM piedavajumu_atversanas pa
LEFT JOIN iepirkumu_rezultati ir ON ir.iepirkuma_id = pa.iepirkuma_id
                                  AND ir.datu_gads = pa.datu_gads
                                  AND ir.liguma_dok_veids = 'Līgums'
WHERE pa.iepirkuma_id = ? AND pa.datu_gads = ?;

-- 3) Vai SPEC un IMPL CPV kodi sasaistīti?
-- (Saistīta tematika apstiprina sagatavošanas darba priekšrocību)
```

**Empīriski validēti gadījumi (Ceruša grupa):**

| Pasūtītājs | SPEC | SPEC summa | IMPL | IMPL summa | Modelis |
|---|---|---|---|---|---|
| **Tiesu administrācija** | Corporate Consulting (3 auditi/izpētes) | ? | E-Synergy (uzturēšana+izstrāde) | **6 040 000** | 🔴 DAŽĀDI |
| **VRAA** | Corporate Consulting (konsultācija) | 38 900 | Corporate Consulting (Ģeoportāla izstr.) | **1 400 000** | Tas pats |
| **Pierīgas Izgl. p.** | Corporate Consulting (audits + spec.) | 51 040 | Corporate Systems (RUMIS izstr.) | **447 183** | 🔴 DAŽĀDI |
| **VID** | Corporate Consulting (konsultācija) | 41 999 | Corporate Systems (PAM iegāde) | **266 104** | 🔴 DAŽĀDI |
| **Prokuratūra** | Corporate Consulting (TS sagatav.) | 26 900 | Corporate Consulting (stratēģija) | 49 000 | Tas pats |

---

## 5. Likumiskās robežas kā audita standarti

| Likums | Norma | Validācijas vaicājums |
|---|---|---|
| PIL 56.p. 4.d. | VV ≤ 4 gadi | `(JULIANDAY(liguma_izpilde_lidz) - JULIANDAY(liguma_izpilde_no))/365.25 > 4.2` |
| PIL 60.p. 7.d. | Nogaidīšanas termiņš 10 d.d. pirms līguma noslēgšanas | Salīdzināt `iepirkumi.piedav_iesniegsanas_datums` ar `iepirkumu_rezultati.liguma_noslegsanas_datums` |
| PIL 61.p. 4.d. | Grozījumi ≤ 50% | `aktuala_summa / sakotneja_summa > 1.5` |
| PIL 17.p. 7.d. | Tiešās pārvaldes obligāti caur VRAA ≥1K€ | Decentralizēti iepirkumi CPV 30, 72 sliekšņa virs 1K€ |
| PIL 47. p. (MK 816) | Pakalpojuma iepirkums ≤1M€ | `planota_ligumcena > 1_000_000` ar 39./44./46. veidu |
| MK 816 38. p. | Zemākās cenas atlase | `iepirkumi.uzvaretaja_izveles_metode = 'Tikai zemākās cenas...'` ar augstu vidējo summu |

---

## 6. ES projektu finansējums

**Datu lauks:** `iepirkumi.atsauce_es_projekti` un `iepirkumu_grozijumi.atsauce_es_projekti` — teksta lauks ar atsauci uz ES programmu/projektu.

**Lietderība:** Atzīmē iepirkumus, kuru īstenošanā ir ES nauda — papildu uzraudzības pienākums (kohēzijas politika, KPVIS u.c.).

```sql
SELECT
  CASE WHEN atsauce_es_projekti IS NOT NULL AND atsauce_es_projekti != ''
       THEN 'ES finansēts' ELSE 'Nav ES' END AS tips,
  COUNT(*) AS iepirkumi,
  SUM(planota_ligumcena) AS kop_summa
FROM iepirkumi
WHERE datu_gads >= 2023
GROUP BY tips;
```

---

## 7. Zaļais iepirkums (PIL 19. p., 1. p. 34))

**PIL 1.p. 34):** Zaļais publiskais iepirkums = "tādu preču, pakalpojumu un būvdarbu iepirkums, kuru ietekme uz vidi to aprites ciklā ir mazāka..."

**Datu lauks:** `e_pasutijumi.preces_1_pazime = 'ZPI kritēriji'` — pozīcijas, kas atzīmētas kā zaļais iepirkums.

```sql
SELECT k.kataloga_numurs, ep.preces_1_pazime,
       COUNT(*) AS pasut_sk,
       SUM(ep.summa_bez_pvn) AS summa
FROM e_pasutijumi ep
JOIN katalogi k ON ep.kataloga_id = k.kataloga_id
WHERE ep.preces_1_pazime IS NOT NULL AND ep.preces_1_pazime != ''
GROUP BY k.kataloga_numurs, ep.preces_1_pazime
ORDER BY summa DESC;
```

---

## 8. Strīdu un sūdzību identifikācija (PIL 68. p.)

**Tieša datu lauka nav**, bet netiešas pazīmes:
- `iepirkuma_statuss` "Apturēts" vai "Pārtraukts" → iespējama IUB iejaukšanās
- `liguma_dok_veids = 'Līguma izbeigšana'` ar `izbeigsanas_iemesls` — agrīna pārtraukšana
- Iepirkums ar daudziem grozījumiem (`iepirkumu_grozijumi` >5 vienam ID) → strīdīga procedūra

```sql
-- Iepirkumi ar lielu grozījumu skaitu
SELECT i.iepirkuma_id, i.iepirkuma_nosaukums,
       po.nosaukums AS pasutitajs,
       COUNT(g.id) AS grozijumu_sk
FROM iepirkumi i
JOIN organizacijas po ON i.pasutitaja_org_id = po.org_id
LEFT JOIN iepirkumu_grozijumi g ON g.iepirkuma_id = i.iepirkuma_id AND g.datu_gads = i.datu_gads
GROUP BY i.iepirkuma_id, i.datu_gads
HAVING grozijumu_sk >= 5
ORDER BY grozijumu_sk DESC;
```

---

## 9. Atvērto datu robežas — ko mēs NEZINĀM

| Aspekts | Robežas |
|---|---|
| **V₂ realizācija** | 95% VV ir decentralizētas. Faktiskie pasūtījumi nav atvērtajos datos. |
| **Cenas piedāvājumi** | EIS atvērtajos datos nav redzamas konkrētās piedāvājuma cenas. Tās atrodas PROPFIS dokumentos (atsevišķi skrāpējams `eis_cenas.db`). |
| **Iesniegumi par pārkāpumiem** | PIL 68.-72. p. iesniegumi nav redzami atvērtajos datos. |
| **Tehniskās specifikācijas** | Iepirkuma dokumentu detaļas (TS, vērtēšanas kritēriji) ir tikai EIS UI, ne CSV. |
| **Komisijas locekļi un kontaktpersonas** | Tikai daļēji laukā `iepirkumi.kontaktpersona` (teksts). |
| **Reālie pretendentu sastāvi (konsorciji)** | `pretendenta_nosaukums` var būt "Personu apvienība", bet konsorcija dalībnieki nav atsevišķi. |
| **Piegādātāju kvalifikācijas atbilstība** | PIL 42. p. izslēgšanas pamatojumi nav publiski. |

---

## 10. Praktiskie vaicājumu šabloni — kombinētas atskaites

### 10.1. Uzņēmuma pilna profila SQL

```sql
WITH vraa AS (SELECT org_id FROM organizacijas WHERE reg_nr = '90001733697'),
org AS (SELECT org_id, nosaukums FROM organizacijas WHERE reg_nr = ?)
SELECT
  o.nosaukums,
  -- T
  (SELECT COUNT(DISTINCT iepirkuma_id) FROM iepirkumu_rezultati
   WHERE uzvaretaja_org_id = o.org_id AND liguma_dok_veids='Līgums' AND ligums_ir_vv='Nē') AS t_ligumi,
  (SELECT SUM(aktuala_summa) FROM iepirkumu_rezultati
   WHERE uzvaretaja_org_id = o.org_id AND liguma_dok_veids='Līgums' AND ligums_ir_vv='Nē') AS t_summa,
  -- V₁
  (SELECT COUNT(*) FROM iepirkumu_rezultati
   WHERE uzvaretaja_org_id = o.org_id AND liguma_dok_veids='Līgums' AND ligums_ir_vv='Jā'
     AND pasutitaja_org_id = (SELECT org_id FROM vraa)) AS v1_kval,
  -- V₁ realizācija
  (SELECT SUM(summa_bez_pvn) FROM e_pasutijumi
   WHERE piegadataja_org_id = o.org_id) AS v1_realizetie,
  -- V₂
  (SELECT COUNT(*) FROM iepirkumu_rezultati
   WHERE uzvaretaja_org_id = o.org_id AND liguma_dok_veids='Līgums' AND ligums_ir_vv='Jā'
     AND pasutitaja_org_id != (SELECT org_id FROM vraa)) AS v2_kval,
  -- Konkursu aktivitāte
  (SELECT COUNT(DISTINCT iepirkuma_id) FROM piedavajumu_atversanas
   WHERE pretendenta_org_id = o.org_id) AS piedavajumi,
  -- PLG
  (SELECT GROUP_CONCAT(vards || ' ' || uzvards) FROM patiesie_labuma_guveji
   WHERE tiesibu_subjekta_reg_nr = ?) AS plg
FROM org o;
```

### 10.2. Iepirkuma pilna konteksta vaicājums

```sql
-- Konkrēta iepirkuma visi pretendenti, rezultāti, grozījumi
SELECT 'IEPIRKUMS' AS bloks, * FROM iepirkumi
WHERE iepirkuma_id = ? AND datu_gads = ?
UNION ALL
SELECT 'PRETENDENTI', * FROM piedavajumu_atversanas
WHERE iepirkuma_id = ? AND datu_gads = ?
UNION ALL
SELECT 'GROZIJUMI', * FROM iepirkumu_grozijumi
WHERE iepirkuma_id = ? AND datu_gads = ?
UNION ALL
SELECT 'REZULTATI', * FROM iepirkumu_rezultati
WHERE iepirkuma_id = ? AND datu_gads = ?;
```

### 10.3. Kataloga suffix sistēma un statusa noteikšana

VV var radīt **vairākus saistītus katalogus** vienā ciklā ar burtu sufiksiem:

| Sufikss | Nozīme | Piemērs |
|---|---|---|
| (bāze) | Preces | CI105 — Asmeņserveri |
| **P** | Pakalpojumi (uzturēšana) | CI105P, CI110P, CI118P |
| **A** | Apmācības kursi | CI110A, CI118A |
| **N** | Nereģistrētas (medikamenti) | CI107N, CI110N |
| **V/C** | Variants (apakšsegments) | CI117V, CI117P, CI117C |
| **M** | Izejmateriāli | CI114M |
| **DP** | Drukas paplašināšana | CI114DP |

**Praktiskā nozīme:** uzņēmums var uzvarēt CI105 (asmeņserveri), bet ne CI105P (to uzturēšana) — tās ir **divas atsevišķas VV** ar atsevišķiem uzvarētāju sarakstiem.

**Kataloga statusa kategorijas (uzņēmuma profilā):**

| Statuss | Definīcija | Stāsts uzņēmumam |
|---|---|---|
| **Aktīvs** | Pēdējais pasūtījums = pēdējais gads datos | Šobrīd reālie ieņēmumi |
| **Beidzies** | Pēdējais pasūtījums < pēdējais gads | Vēsturiski ieņēmumi, **nepagarināms** |
| **Migrēts** | Beidzies, bet pastāv pēctece ar tādu pašu nosaukumu | Jāpārbauda, vai uzņēmums uzvarēja arī pēctecē |

**Empīriski no datiem (CI118 "Standarta programmatūra" piemērā):** 652 unikālas pozīcijas — 25% dzīvo 1 gadu, 15% — 2 gadus, 60% — 3-5 gadus. Pozīciju "miršana" ir dabīga, nevis konkurences zaudēšana.

```sql
-- Kataloga statusa un uzņēmuma ieņēmumu vaicājums
WITH kat_stat AS (
  SELECT k.kataloga_id, k.kataloga_numurs, k.kataloga_nosaukums,
         MIN(ep.datu_gads) AS no_gada,
         MAX(ep.datu_gads) AS lidz_gadam,
         CASE
           WHEN MAX(ep.datu_gads) = (SELECT MAX(datu_gads) FROM e_pasutijumi) THEN 'AKTĪVS'
           ELSE 'BEIDZIES'
         END AS statuss
  FROM e_pasutijumi ep
  JOIN katalogi k ON ep.kataloga_id = k.kataloga_id
  GROUP BY k.kataloga_id
)
SELECT k.kataloga_numurs, k.kataloga_nosaukums,
       k.no_gada || '-' || k.lidz_gadam AS periods, k.statuss,
       COUNT(DISTINCT ep.pasutijuma_nr) AS uznemuma_pasutijumi,
       SUM(ep.summa_bez_pvn) AS uznemuma_ienemumi
FROM kat_stat k
JOIN e_pasutijumi ep ON ep.kataloga_id = k.kataloga_id
JOIN organizacijas o ON ep.piegadataja_org_id = o.org_id
WHERE o.reg_nr = ?
GROUP BY k.kataloga_id
ORDER BY k.lidz_gadam DESC, uznemuma_ienemumi DESC;
```

**Migrācijas pārbaude** — vai uzņēmums "izdzīvoja" katalogu nomaiņu:

```sql
WITH manas_kataloga_vesture AS (
  SELECT k.kataloga_id, k.kataloga_numurs, k.kataloga_nosaukums,
         MAX(ep.datu_gads) AS lidz_gadam
  FROM e_pasutijumi ep
  JOIN katalogi k ON ep.kataloga_id = k.kataloga_id
  JOIN organizacijas o ON ep.piegadataja_org_id = o.org_id
  WHERE o.reg_nr = ?
  GROUP BY k.kataloga_id
)
SELECT m.kataloga_numurs AS beidzies, m.kataloga_nosaukums, m.lidz_gadam,
       p.kataloga_numurs AS pectece,
       CASE WHEN EXISTS (
         SELECT 1 FROM e_pasutijumi ep2
         JOIN organizacijas o2 ON ep2.piegadataja_org_id = o2.org_id
         WHERE o2.reg_nr = ? AND ep2.kataloga_id = p.kataloga_id
       ) THEN 'MIGRĒJA ✓' ELSE 'ZAUDĒJA ✗' END AS migracija
FROM manas_kataloga_vesture m
LEFT JOIN katalogi p ON p.kataloga_nosaukums = m.kataloga_nosaukums
                    AND p.kataloga_id != m.kataloga_id
WHERE m.lidz_gadam < (SELECT MAX(datu_gads) FROM e_pasutijumi);
```

### 10.4. PLG grupu un phantom piedāvājumu meklēšana

**Personas unikāla identifikācija** prasa 3 lauku kombināciju: `vards + uzvards + pers_kods_maskets`. Ārvalstniekiem (~7,138 personas ar tukšu maskēto kodu) lieto `vards + uzvards + dzimsanas_datums + valstspiederiba`.

**Grupas meklēšana** — kuri cilvēki kontrolē daudz EIS piegādātāju:

```sql
SELECT plg.vards, plg.uzvards, plg.pers_kods_maskets,
       COUNT(DISTINCT o.org_id) AS uznemumi_sk,
       GROUP_CONCAT(DISTINCT o.nosaukums, ' | ') AS uznemumi
FROM patiesie_labuma_guveji plg
JOIN organizacijas o ON plg.tiesibu_subjekta_reg_nr = o.reg_nr
WHERE o.ir_piegadatajs = 1
GROUP BY plg.vards, plg.uzvards, plg.pers_kods_maskets
HAVING uznemumi_sk >= 5
ORDER BY uznemumi_sk DESC;
```

**Phantom piedāvājumu šablons** — vai vienas PLG grupas vairāki uzņēmumi piedalās vienā iepirkumā:

```sql
WITH plg_grupas AS (
  SELECT plg.vards || ' ' || plg.uzvards || ' (' || plg.pers_kods_maskets || ')' AS persona,
         o.org_id
  FROM patiesie_labuma_guveji plg
  JOIN organizacijas o ON plg.tiesibu_subjekta_reg_nr = o.reg_nr
  WHERE o.ir_piegadatajs = 1
)
SELECT pg.persona, pa.iepirkuma_id, pa.datu_gads,
       COUNT(DISTINCT pg.org_id) AS grupas_dalibnieki,
       GROUP_CONCAT(DISTINCT o.nosaukums) AS dalibnieki,
       po.nosaukums AS pasutitajs, i.iepirkuma_nosaukums
FROM piedavajumu_atversanas pa
JOIN plg_grupas pg ON pa.pretendenta_org_id = pg.org_id
JOIN organizacijas o ON pa.pretendenta_org_id = o.org_id
JOIN iepirkumi i ON pa.iepirkuma_id = i.iepirkuma_id AND pa.datu_gads = i.datu_gads
JOIN organizacijas po ON i.pasutitaja_org_id = po.org_id
GROUP BY pg.persona, pa.iepirkuma_id, pa.datu_gads
HAVING grupas_dalibnieki >= 2
ORDER BY pa.datu_gads DESC, grupas_dalibnieki DESC;
```

**Grupas dominance konkrētā iestādē** — vai grupa sistemātiski uzvar pie viena pasūtītāja:

```sql
WITH grupa AS (
  SELECT o.org_id
  FROM patiesie_labuma_guveji plg
  JOIN organizacijas o ON plg.tiesibu_subjekta_reg_nr = o.reg_nr
  WHERE plg.vards = ? AND plg.uzvards = ? AND plg.pers_kods_maskets = ?
),
grupas_pa_pasutitajiem AS (
  SELECT ir.pasutitaja_org_id, SUM(ir.aktuala_summa) AS grupas_summa
  FROM iepirkumu_rezultati ir
  WHERE ir.uzvaretaja_org_id IN (SELECT org_id FROM grupa)
    AND ir.liguma_dok_veids = 'Līgums' AND ir.ligums_ir_vv = 'Nē'
  GROUP BY ir.pasutitaja_org_id
),
pasutitaja_kopejas AS (
  SELECT pasutitaja_org_id, SUM(aktuala_summa) AS kopa
  FROM iepirkumu_rezultati
  WHERE liguma_dok_veids = 'Līgums' AND ligums_ir_vv = 'Nē'
  GROUP BY pasutitaja_org_id
)
SELECT po.nosaukums, g.grupas_summa, pk.kopa,
       ROUND(100.0 * g.grupas_summa / pk.kopa, 1) AS tirgus_dala_proc
FROM grupas_pa_pasutitajiem g
JOIN pasutitaja_kopejas pk USING (pasutitaja_org_id)
JOIN organizacijas po ON g.pasutitaja_org_id = po.org_id
WHERE pk.kopa > 50000
ORDER BY tirgus_dala_proc DESC;
```

### 10.5. Konkurences modeļi katalogā (MK 816)

PIL un MK 816 paredz **dažādu intensitāti konkurencei katalogā**:

| Modelis | MK 816 pants | Datu pazīme | Konkurence |
|---|---|---|---|
| **A. Standarta pasūtījums (sistēma izvēlas)** | 38. p. | 1 piegādātājs, ne īpaši liela summa | Tikai pa cenu kataloga līmenī |
| **B. Standarta ar specifikāciju (lejupejošā solīšana, 1 d.d.)** | 39. p. | Vairāki piegādātāji vienā pozīcijā + dienā + pircēja | Reāla, asa |
| **C. Lielas vērtības pasūtījums (3 d.d.)** | 40. p. | Lielāka summa virs sliekšņa | Reāla, ar laiku |
| **D. Nedalāms vai viena piegādātāja** | 44., 46. p. | 1 piegādātājs ar lielu summu vai eksplicītu pamatojumu | Nav konkurences |

```sql
-- B/C modeļa identifikācija (reāli konkurences notikumi katalogā)
WITH konkurence AS (
  SELECT apstiprinasanas_datums, pasutitaja_org_id, kataloga_id, pozicijas_numurs,
         COUNT(DISTINCT piegadataja_org_id) AS piegadataju_sk
  FROM e_pasutijumi
  WHERE apstiprinasanas_datums IS NOT NULL
  GROUP BY apstiprinasanas_datums, pasutitaja_org_id, kataloga_id, pozicijas_numurs
  HAVING piegadataju_sk > 1
)
SELECT datu_gads, COUNT(*) AS konkur_notikumi
FROM e_pasutijumi ep
JOIN konkurence k USING (apstiprinasanas_datums, pasutitaja_org_id, kataloga_id, pozicijas_numurs)
GROUP BY datu_gads;
```

### 10.6. Vizuālā prezentācija — uzņēmuma profila šablons

```
┌─────────────────────────────────────────────────────────┐
│ T. TIEŠIE LĪGUMI (ligums_ir_vv = 'Nē')                 │
│ Skaits: {N}    Kopējā vērtība: {X} EUR (faktiskie ieņ.) │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│ V₁. CENTRALIZĒTĀS VV — caur EIS katalogu (VRAA)        │
│ Kvalifikācijas: {N}   Griesti: {X} EUR (⚠ NAV ieņ.)    │
│ Realizētie: {Y} EUR (caur e_pasutijumi)                │
│ Izmantošanas koef.: {Y/X}%  (<5% = mirusi kvalifikācija)│
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│ V₂. DECENTRALIZĒTĀS VV — tiešās ar iestādēm            │
│ Kvalifikācijas: {N}   Griesti: {X} EUR (⚠ NAV ieņ.)    │
│ Realizācija: NAV DATU (ārpus atvērtajiem)              │
│ Atšķirīgi pasūtītāji: {N}                               │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│ MĒRĀMIE FAKTISKIE IEŅĒMUMI = T + V₁ realizētie         │
│ ⚠ V₂ ieņēmumi pastāv, bet nav publicēti                 │
└─────────────────────────────────────────────────────────┘
```

---

## 11. Termini un saīsinājumi

| Termins | Pilnais nosaukums | PIL atsauce |
|---|---|---|
| **PIL** | Publisko iepirkumu likums | — |
| **SPSIL** | Sabiedrisko pakalpojumu sniedzēju iepirkumu likums | — |
| **ADJIL** | Aizsardzības un drošības jomas iepirkumu likums | — |
| **PPP likums** | Publiskās un privātās partnerības likums | — |
| **VV** | Vispārīgā vienošanās | PIL 1.p. 33), 56.p. |
| **DIS** | Dinamiskā iepirkumu sistēma | PIL 1.p. 5), 57.p. |
| **CPV** | Common Procurement Vocabulary (iepirkuma nomenklatūra) | PIL 1.p. 10) |
| **VRAA** | Valsts reģionālās attīstības aģentūra (juridiski) / Valsts digitālās attīstības aģentūra (datos) | MK 816, EIS pārzinis |
| **VDAA** | Valsts digitālās attīstības aģentūra | reg_nr 90001733697 |
| **EIS** | Elektroniskā iepirkumu sistēma | MK 816 2.1.p. |
| **IUB** | Iepirkumu uzraudzības birojs | PIL 65.-67.p. |
| **PVS** | Publikāciju vadības sistēma | PIL 1.p. 25) |
| **ZPI** | Zaļais publiskais iepirkums | PIL 1.p. 34), 19.p. |
| **PLG** | Patiesie labuma guvēji | LR Uzņēmumu reģistra dati |
| **T / V₁ / V₂** | Tiešais līgums / Centralizētā VV / Decentralizētā VV | Šī faila konvencija |
| **MK 816** | MK noteikumi Nr. 816 "Publisko elektronisko iepirkumu noteikumi" | 20.12.2022 |

---

## 12. Atskaites izstrādes kontrolsaraksts

Pirms publicēt jebkuru atskaiti par EIS datiem, pārbaudi:

- [ ] Vai ieņēmumu summa filtrē `ligums_ir_vv = 'Nē'` (T tips) NEVIS visi `aktuala_summa`?
- [ ] Vai VV (V₁/V₂) tiek prezentētas atsevišķā blokā, ne sajauktā ar tiešajiem līgumiem?
- [ ] Vai V₁ realizācija meklēta `e_pasutijumi` (caur to pašu piegādātāju), nevis `iepirkumu_rezultati`?
- [ ] Vai uzvarētāju skaitlis filtrē `liguma_dok_veids = 'Līgums'` (ne grozījumi/izbeigšanas)?
- [ ] Vai konkurentu analīze pārbauda PLG grupas (vai nav phantom piedāvājumi)?
- [ ] Vai pasūtītāja identifikācija centralizētajos iepirkumos atšķir VRAA vs faktiskais saņēmējs?
- [ ] Vai kataloga aktivitātes analīze ņem vērā 3-5 gadu dzīves ciklu (vai katalogs beidzies)?
- [ ] Vai laika periodi salīdzināmi? (PIL un MK 816 redakcijas mainās)
- [ ] Vai trūkstošie dati (V₂ realizācija, cenas, sūdzības) ir eksplicīti norādīti?

---

## 13. Saistīto failu rādītājs

| Fails | Vajadzīgs, kad... |
|---|---|
| **`EIS_SKILL.md`** (šis) | Vienmēr — galvenais analīzes rīks, satur visu konceptuālo pamatu, sarkanos karogus un SQL šablonus |
| **`eis-db-schema.md`** | Sniegt LLM/analītiķim tehnisko shēmu |
| **`eis-docs/markdown/PUBLISKO_IEPIRKUMU_LIKUMS.md`** | Konkrēts likumiskais jautājums |
| **`eis-docs/markdown/13_MK_noteikumi_816.md`** | Centralizācijas un kataloga procesa jautājumi |
| **`eis-docs/EIS_zinasanu_baze.md`** | Pasūtījumu/piegāžu statusu cikls, EIS lomas |
| **`eis-docs/markdown/01-12_*.md`** | EIS UI lietošanas detaļas (reti vajadzīgs analīzei) |
| **`eis.db`** | Visi SQL vaicājumi |
| **`CERUSS_KEDES.md`**, **`CERUSS_KONTEKSTS.md`** | Empīrisko paterniem piemērs — Aigara Ceruša grupa |
