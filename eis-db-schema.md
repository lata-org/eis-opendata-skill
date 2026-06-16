# EIS SQLite datubaazes sheema / EIS SQLite Database Schema

> **Terminoloģijas un faktu avoti:**
> - PIL — [`eis-docs/markdown/PUBLISKO_IEPIRKUMU_LIKUMS.md`](eis-docs/markdown/PUBLISKO_IEPIRKUMU_LIKUMS.md) — pamatlikums (90 panti)
> - MK 816 — [`eis-docs/markdown/13_MK_noteikumi_816.md`](eis-docs/markdown/13_MK_noteikumi_816.md) — e-iepirkumu sistēmas regulējums
> - Analītiskā izpratne — [`UZNEMUMA_PROFILS.md`](UZNEMUMA_PROFILS.md), [`KATALOGI_UN_VV_IZPRATNE.md`](KATALOGI_UN_VV_IZPRATNE.md)
>
> Galvenie likumiskie termini, kas pārstāvēti shēmā:
> - Iepirkuma līgums = PIL 60. p. (`iepirkumu_rezultati.liguma_dok_veids = 'Līgums'`)
> - Vispārīgā vienošanās (VV) = PIL 1.p. 33), 56. p. (`ligums_ir_vv = 'Jā'`)
> - Dinamiskā iepirkumu sistēma (DIS) = PIL 1.p. 5), 57. p. (`dis_piemerosana = 'Jā'`)
> - Centralizēto iepirkumu institūcija = PIL 1.p. 4), 17. p. (VRAA, `reg_nr = '90001733697'`)
> - Pretendents = PIL 1.p. 24) (`piedavajumu_atversanas.pretendenta_*`)
> - Iepirkuma līguma grozījumi = PIL 61. p. (`liguma_dok_veids = 'Līguma grozījumi'`, ≤50% pieaugums)

---

## 1. Projekcijas principi / Design Principles

### 1.1. Gadu apvienosana

Visu gadu CSV faili tiek apvienoti **viena tabula** ar papildus kolonu `datu_gads` (INTEGER), kas norada avota faila gadu.
Tas attiecas uz visam 6 datu kopam, kam ir gada faili (pasutijumi, piegades, izsludinatie, atversana, grozijumi, rezultati).

**Pamatojums:** Datu struktura (kolonnas) ir identiska visos gados. Viena tabula ar indeksu uz `datu_gads` ir efektivaaka neka 17 atseviskjas tabulas, jo:
- Vienkarsotas vaicajumi starplaiku analizei
- Nav nepieciesams UNION ALL starp tabulam
- Indeksi efektivi filtre pec gada

### 1.2. Normalizacijas limenis

Izveleets **2NF+ limenis** ar sapratigu denormalizaciju:

**Normalize (izcel atseviskjas tabulas):**
- Organizacijas (pasutitaji + piegadataji) --> `organizacijas` tabula
- Katalogi --> `katalogi` tabula
- CPV kodi --> `cpv_kodi` tabula (galvenie un papildu)

**NENORMALIZE (atstaj ka tekstu kolonna):**
- Statusi, proceduru veidi, tiesibu akti u.c. uzskaites vertiibas --> atstaj ka TEXT, jo:
  - Maz unikaalo vertibu (3-11 varianti)
  - Nav atsevissku atributu katrai vertibai
  - SQLite nav enum tipa -- atsevisska tabula tikai pievienotu JOIN slogu bez ieguuvuma
  - Integritaati var nodrosinat ar CHECK ierobezojumiem

### 1.3. Datumu formats

CSV failos datumi ir formata `DD.MM.YYYY`. Datubaze glabaas ka **TEXT ISO-8601 formata** (`YYYY-MM-DD`) lai SQLite datumu funkcijas darbotos korekti. Konvertacija notiek importa laika.

### 1.4. Summas un skaitli

- Naudas summas -- `REAL` (SQLite nav DECIMAL tipa)
- Daudzumi -- `INTEGER`
- PVN likme -- `REAL`

---

## 2. ER diagramma (Entity-Relationship) / ER Diagram

```
                     ┌─────────────────────┐
                     │   organizacijas      │
                     │─────────────────────│
                     │ PK org_id           │
                     │    reg_nr            │
                     │    nosaukums         │
                     │    reg_nr_veids      │
                     │    augstak_org       │
                     │    ...               │
                     └──────┬──────────────┘
                            │ 1
           ┌────────────────┼─────────────────────────────┐
           │                │                             │
           ▼ N              ▼ N                           ▼ N
┌─────────────────┐ ┌──────────────────┐      ┌───────────────────────┐
│ e_pasutijumi    │ │ iepirkumi        │      │ iepirkumu_rezultati   │
│─────────────────│ │──────────────────│      │ (ligumi)              │
│ PK id           │ │ PK iepirkuma_id  │      │───────────────────────│
│ FK pasutitaja_  │ │ FK pasutitaja_   │      │ PK id                 │
│    org_id       │ │    org_id        │      │ FK iepirkuma_id       │
│ FK piegadataja_ │ │    nosaukums     │      │ FK uzvaretaja_org_id  │
│    org_id       │ │    ident_nr      │      │    liguma_summa       │
│ FK kataloga_id  │ │    cpv_galv      │      │    ...                │
│    pasut_nr     │ │    statuss       │      └───────────────────────┘
│    statuss      │ │    procedura     │                │
│    summa        │ │    ...           │                │
│    ...          │ └────────┬─────────┘       ┌────────┘
└───────┬─────────┘          │                 │
        │ 1                  │ 1               │
        ▼ N                  ├────────────┐    │
┌─────────────────┐          ▼ N          ▼ N  │
│ piegades        │ ┌──────────────┐ ┌────────────────┐
│─────────────────│ │ piedavajumu  │ │ iepirkumu       │
│ PK id           │ │ atversanas   │ │ grozijumi       │
│ FK pasutijuma_  │ │──────────────│ │────────────────│
│    id           │ │ PK id        │ │ PK id           │
│ FK pasutitaja_  │ │ FK iepirk_id │ │ FK iepirkuma_id │
│    org_id       │ │ FK pretend_  │ │    grozijumu_dat│
│ FK piegadataja_ │ │    org_id    │ │    ...           │
│    org_id       │ │    ...       │ └────────────────┘
│ FK kataloga_id  │ └──────────────┘
│    summa        │
│    ...          │       ┌──────────────┐
└─────────────────┘       │ katalogi     │
                          │──────────────│
                          │ PK kataloga_id│
                          │    numurs     │
                          │    nosaukums  │
                          └──────────────┘
```

---

## 3. Tabulu definicijas / Table Definitions

### 3.1. `organizacijas` -- Organizaciju registrs

**Avots:** `PASUTITAJI_KLAS.csv` + papildinats no piegadataju datiem citas CSV failos.
**Merkkis:** Centralizets organizaciju registrs -- gan pasutitaji, gan piegadataji.

```sql
CREATE TABLE organizacijas (
    org_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    reg_nr          TEXT NOT NULL,              -- Registracijas numurs (piem., "40003344207")
    nosaukums       TEXT,                       -- Organizacijas nosaukums
    reg_nr_veids    TEXT,                       -- "PVN maksātāja numurs" | "Personas kods/nodokļu maksātāja reģistrācijas kods"
    augstak_stavosa_organizacija TEXT,          -- Augstakstavosa org (ministrija)
    pvs_id          TEXT,                       -- PVS sistemas ID (ja zinams)
    eis_reg_datums  TEXT,                       -- Registracijas datums EIS (YYYY-MM-DD)
    ir_blokets      INTEGER DEFAULT 0,         -- 0/1 boolean
    ir_dzests       INTEGER DEFAULT 0,         -- 0/1 boolean
    ir_pasutitajs   INTEGER DEFAULT 0,         -- 0/1 -- vai registrets ka pasutitajs
    ir_piegadatajs  INTEGER DEFAULT 0,         -- 0/1 -- vai registrets ka piegadatajs
    UNIQUE(reg_nr)
);

CREATE INDEX idx_org_reg_nr ON organizacijas(reg_nr);
CREATE INDEX idx_org_nosaukums ON organizacijas(nosaukums);
CREATE INDEX idx_org_augstak ON organizacijas(augstak_stavosa_organizacija);
```

**Normalizacijas piezimes:**
- `PASUTITAJI_KLAS.csv` satur tikai pasutitajus (ir_pasutitajs=1)
- Piegadataji tiek papildinati no `e_pasutijumi` un `piegades` tabulam (reg_nr, kas nav PASUTITAJI_KLAS)
- `reg_nr` ir unikala atsleega -- viena organizacija var but gan pasutitajs, gan piegadatajs
- `reg_nr_veids` netiek normalizets atseviskja tabula (tikai 2 vertibas)

---

### 3.2. `katalogi` -- E-katalogu registrs

**Avots:** Izvilets no `e_pasutijumi` un `piegades` tabulu unikalo katalogu kombinacijam.
**Merkkis:** Centralizeta kataloga informacija, lai neatkaartotos katraa pasutijuma rinda.

```sql
CREATE TABLE katalogi (
    kataloga_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    kataloga_numurs TEXT NOT NULL UNIQUE,       -- Piem., "NVD3", "CI123V", "70000.000.0014"
    kataloga_nosaukums TEXT                     -- Piem., "Medicīnas preces", "Datortehnika I"
);

CREATE INDEX idx_kat_numurs ON katalogi(kataloga_numurs);
```

**Normalizacijas pamatojums:**
- ~147 unikalas vertiibas (2026. gada datos, ieskaitot vēsturiskās paaudzes — skat. UZNEMUMA_PROFILS.md 10. sad. par dzīves ciklu)
- Katrs katalogs atkartojas simtiem/tukstosiem rindu pasutijumos/piegades
- Ietaupa vietu un nodrosina konsekvenci
- PIL pamats: katalogs realizē PIL 56.p. VV vai 57.p. DIS (skat. MK 816 37.p.)

---

### 3.3. `e_pasutijumi` -- Pirkuma pasutijumi (e-pasutijumu apakssistema)

**Avots:** `EIS_E_PASUT_APST_YYYY.csv` (2010-2026, apvienoti)
**Grauds:** Viena rinda = viena pasutijuma preces rinda (viena prece viena pasutijuma)

```sql
CREATE TABLE e_pasutijumi (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    datu_gads           INTEGER NOT NULL,          -- Avota faila gads (2010-2026)
    pasutitaja_org_id   INTEGER REFERENCES organizacijas(org_id),
    piegadataja_org_id  INTEGER REFERENCES organizacijas(org_id),
    pasutijuma_nr       TEXT NOT NULL,             -- Pasutijuma identifikators (piem., "LRS/2025/478")
    pasutijuma_statuss  TEXT,                      -- 5 vērtības datos (no 16 pilna cikla -- skat. EIS_zinasanu_baze.md 5.2)
    apstiprinasanas_datums TEXT,                   -- YYYY-MM-DD
    kataloga_id         INTEGER REFERENCES katalogi(kataloga_id),
    pozicijas_numurs    TEXT,                      -- VV pozicijas numurs (piem., "NVD3.9.27.9")
    preces_1_pazime     TEXT,                      -- "ZPI kritēriji" | ""
    preces_2_pazime     TEXT,                      -- Otra ipasa pazime
    preces_nosaukums    TEXT,                      -- Pasutitas preces nosaukums
    preces_razotajs     TEXT,                      -- Razotaja nosaukums
    preces_razotaja_kods TEXT,                     -- Razotaja preces kods
    max_piegades_datums TEXT,                      -- YYYY-MM-DD
    summa_bez_pvn       REAL,                      -- EUR
    pvn_proc            REAL,                      -- PVN likme % (21, 12, 5, 0)
    pasutitais_skaits   INTEGER,                   -- Daudzums
    CHECK (pasutijuma_statuss IN (
        'APSTIPRINĀTS PASŪTĪJUMS',
        'PILNĪBĀ IZPILDĪTS PASŪTĪJUMS',
        'IZBEIGTS PASŪTĪJUMS',
        'IEPIRCĒJA APSTIPRINĀTAS IZMAIŅAS PIEGĀDES LAIKĀ',
        'PIEPRASĪTAS IZMAIŅAS PIEGĀDES LAIKĀ'
    ))
);

CREATE INDEX idx_epas_gads ON e_pasutijumi(datu_gads);
CREATE INDEX idx_epas_pasut_nr ON e_pasutijumi(pasutijuma_nr);
CREATE INDEX idx_epas_pasutitaja ON e_pasutijumi(pasutitaja_org_id);
CREATE INDEX idx_epas_piegadataja ON e_pasutijumi(piegadataja_org_id);
CREATE INDEX idx_epas_kataloga ON e_pasutijumi(kataloga_id);
CREATE INDEX idx_epas_datums ON e_pasutijumi(apstiprinasanas_datums);
CREATE INDEX idx_epas_statuss ON e_pasutijumi(pasutijuma_statuss);
```

**Kardinalitaate:** ~100K-300K rindu gadaa, kopaa ~4.1M rindu (2010-2026).
**Pasutijuma_nr NAV unikaals** -- viens pasutijums var saturet vairaakas preces rindas.
**Konteksts:** Šeit redzami tikai apstiprināti pasūtījumi (EIS_zinasanu_baze.md 5.2 — 16 statusu cikls); 5 statusu vērtības faktiski parādās datos.

---

### 3.4. `piegades` -- Piegaazu dati (e-pasutijumu apakssistema)

**Avots:** `EIS_E_PASUT_YYYY.csv` (2010-2026, apvienoti)
**Grauds:** Viena rinda = viena piegades preces rinda

```sql
CREATE TABLE piegades (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    datu_gads           INTEGER NOT NULL,          -- Avota faila gads
    pasutitaja_org_id   INTEGER REFERENCES organizacijas(org_id),
    piegadataja_org_id  INTEGER REFERENCES organizacijas(org_id),
    pasutijuma_nr       TEXT,                      -- Sasiistits ar e_pasutijumi.pasutijuma_nr
    kataloga_id         INTEGER REFERENCES katalogi(kataloga_id),
    pozicijas_nr        TEXT,                      -- VV pozicijas numurs
    preces_1_pazime     TEXT,                      -- "ZPI kritēriji" | ""
    preces_2_pazime     TEXT,
    pirkuma_izveid_datums TEXT,                    -- YYYY-MM-DD (pirkuma pieprasijuma izveidosanas)
    pavadzimes_nr       TEXT,                      -- Pavadzimes/piegades dokumenta numurs
    piegades_statuss    TEXT,                      -- "Kvalificēta piegāde" | "Daļēji kvalificēta piegāde"
    kval_apstipr_datums TEXT,                      -- YYYY-MM-DD
    summa_bez_pvn       REAL,                      -- EUR
    pvn_proc            REAL,                      -- PVN likme %
    kval_skaits         INTEGER,                   -- Kvalificetais daudzums
    preces_nosaukums    TEXT,                      -- Faktiski piegadatas preces nosaukums
    preces_razotajs     TEXT,                      -- Faktiski piegadatas preces razotajs
    preces_razotaja_kods TEXT,                     -- Razotaja kods
    piegades_adrese     TEXT,                      -- Fiziska piegades adrese
    CHECK (piegades_statuss IN (
        'Kvalificēta piegāde',
        'Daļēji kvalificēta piegāde'
    ))
);

CREATE INDEX idx_pieg_gads ON piegades(datu_gads);
CREATE INDEX idx_pieg_pasut_nr ON piegades(pasutijuma_nr);
CREATE INDEX idx_pieg_pasutitaja ON piegades(pasutitaja_org_id);
CREATE INDEX idx_pieg_piegadataja ON piegades(piegadataja_org_id);
CREATE INDEX idx_pieg_kataloga ON piegades(kataloga_id);
CREATE INDEX idx_pieg_kval_dat ON piegades(kval_apstipr_datums);
CREATE INDEX idx_pieg_statuss ON piegades(piegades_statuss);
```

**Kardinalitaate:** ~100K-300K rindu gadaa, kopaa ~4.1M rindu (2010-2026).
**Pasutijuma_nr NAV unikaals** -- vienam pasutijumam var but vairaakas piegades.
**Konteksts:** Atvērtajos datos parādās tikai pabeigtās piegādes (Kvalificēta vai Daļēji kvalificēta), nevis viss 6 statusu cikls (skat. EIS_zinasanu_baze.md 5.4).

---

### 3.5. `iepirkumi` -- Izsludinatie iepirkumi (e-konkursu apakssistema)

**Avots:** `EIS_E_IEPIRKUMI_IZSLUDINATIE_YYYY.csv` (2016-2026, apvienoti)
**Grauds:** Viena rinda = viens iepirkums VAI viena iepirkuma dala (ja ir dalasanas)

```sql
CREATE TABLE iepirkumi (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    datu_gads           INTEGER NOT NULL,
    iepirkuma_id        INTEGER NOT NULL,          -- EIS sistemas unikaalais ID
    iepirkuma_nosaukums TEXT,
    iepirkuma_ident_nr  TEXT,                      -- Pasutitaja pieskirts numurs (piem., "FM VID 2024/256/ĀF")
    pasutitaja_org_id   INTEGER REFERENCES organizacijas(org_id),
    citu_pasutitaju_vajadzibam TEXT,               -- "Jā" | "Nē"
    faktiskais_sanemejs TEXT,
    iepirkuma_prieksmeta_veids TEXT,               -- "Piegāde" | "Pakalpojums" | "Būvdarbi"
    cpv_kods_galvenais  TEXT,                      -- "45233200-1 Dažādi ceļu seguma būvdarbi"
    cpv_kodi_papildus   TEXT,                      -- Komats-atdaliti papildus CPV kodi
    iepirkuma_statuss   TEXT,
    izsludinasanas_datums TEXT,                    -- YYYY-MM-DD
    piedav_iesniegsanas_datums TEXT,               -- YYYY-MM-DD
    piedav_iesniegsanas_laiks TEXT,                -- HH:MM
    ieintereseto_sanaksmes TEXT,
    sniegsanas_vieta    TEXT,
    -- Liguma termins
    liguma_termina_veids TEXT,                     -- "Laiks no līguma noslēgšanas" | "Laika periods"
    liguma_termins      TEXT,                      -- Skaitliska vertiba ka teksts
    liguma_termina_mervieniba TEXT,                -- "Mēneši" | "Gadi" | "Dienas"
    liguma_izpilde_no   TEXT,                      -- YYYY-MM-DD
    liguma_izpilde_lidz TEXT,                      -- YYYY-MM-DD
    -- Ligumcena
    ligumcenas_veids    TEXT,                      -- "Paredzamā līgumcena" | "Līgumcenas diapazons" | ""
    planota_ligumcena   REAL,                      -- EUR
    planota_ligumcena_no REAL,                     -- Diapazona apakssa
    planota_ligumcena_lidz REAL,                   -- Diapazona augssa
    ligumcenas_valuta   TEXT DEFAULT 'EUR',
    -- Procedura
    regulejosais_tiesibu_akts TEXT,                -- Skat. CHECK zemāk -- 6 faktiskās vērtības datos
    proceduras_veids    TEXT,                      -- PIL 8.p. + 1.p. 3)/12)/14)/15)/18)/30)/31): "Atklāts konkurss", "Slēgts konkurss", "Sarunu procedūra", "Konkursa procedūra ar sarunām", "Konkursa dialogs", "Inovācijas partnerības procedūra", "Metu konkurss", "Mazie iepirkumi" (PIL 9.p.), "2.pielikumā minēto pakalpojumu iepirkumi" (PIL 10.p.), u.c. -- 14 vērtības datos
    kontaktpersona      TEXT,
    iesniegsanas_valoda TEXT DEFAULT 'LATVIEŠU',
    atsauce_es_projekti TEXT,
    pielaujami_varianti TEXT,                      -- "Jā" | "Nē"
    uzvaretaja_izveles_metode TEXT,                -- PIL 51.p.: "Tikai zemākās cenas vai tikai izmaksu vērtēšana" | "Saimnieciskā izdevīguma vērtēšana (cenas vai izmaksu efektivitāte un kvalitātes kritēriji)"
    iesniegsanas_vieta  TEXT,                      -- "Elektronisko iepirkumu sistēmā"
    hipersaite_eis      TEXT,
    hipersaite_iub      TEXT,
    -- Dalas
    ir_dalijums_dalas   TEXT,                      -- "Jā" | "Nē"
    dalu_iesniegsanas_nosacijumi TEXT,
    dalas_nr            TEXT,                      -- Dalas kartibas numurs (ja ir)
    dalas_nosaukums     TEXT,
    dalas_statuss       TEXT,
    -- Dalas liguma termins (atkaartojas)
    dalas_termina_veids TEXT,
    dalas_termins       TEXT,
    dalas_termina_mervieniba TEXT,
    dalas_izpilde_no    TEXT,
    dalas_izpilde_lidz  TEXT,
    dalas_ligumcenas_veids TEXT,
    dalas_ligumcena     REAL,
    dalas_ligumcena_no  REAL,
    dalas_ligumcena_lidz REAL,
    dalas_valuta        TEXT,
    -- PIL 1.p. 26)/27)/28): publisks būvdarbu / pakalpojuma / piegādes līgums
    CHECK (iepirkuma_prieksmeta_veids IN ('Piegāde', 'Pakalpojums', 'Būvdarbi', '')),
    -- Faktiskās datu vērtības (no eis.db 2010-2026):
    --   Publisko iepirkumu likums (225,083 -- PIL, pamatlikums)
    --   Sabiedrisko pakalpojumu sniedzēju iepirkumu likums (12,050 -- SPSIL)
    --   Par ārkārtējo situāciju un izņēmuma stāvokli (796 -- Covid-19/krīzes periodā)
    --   Aizsardzības un drošības jomas iepirkumu likums (545 -- ADJIL)
    --   Publisko iepirkumu likums (spēka līdz 28.02.2017) (64 -- vēsturisks)
    --   Publiskās un privātās partnerības likums (10 -- PPP)
    CHECK (regulejosais_tiesibu_akts IN (
        'Publisko iepirkumu likums',
        'Sabiedrisko pakalpojumu sniedzēju iepirkumu likums',
        'Aizsardzības un drošības jomas iepirkumu likums',
        'Publiskās un privātās partnerības likums',
        'Par ārkārtējo situāciju un izņēmuma stāvokli',
        'Publisko iepirkumu likums (spēka līdz 28.02.2017)'
    ))
);

CREATE INDEX idx_iep_gads ON iepirkumi(datu_gads);
CREATE INDEX idx_iep_id ON iepirkumi(iepirkuma_id);
CREATE INDEX idx_iep_ident_nr ON iepirkumi(iepirkuma_ident_nr);
CREATE INDEX idx_iep_pasutitaja ON iepirkumi(pasutitaja_org_id);
CREATE INDEX idx_iep_statuss ON iepirkumi(iepirkuma_statuss);
CREATE INDEX idx_iep_datums ON iepirkumi(izsludinasanas_datums);
CREATE INDEX idx_iep_cpv ON iepirkumi(cpv_kods_galvenais);
CREATE INDEX idx_iep_procedura ON iepirkumi(proceduras_veids);
CREATE INDEX idx_iep_prieksmets ON iepirkumi(iepirkuma_prieksmeta_veids);
```

**Kardinalitaate:** ~13K-33K rindu gadaa (ieskaitot dalu rindas), kopaa ~238K rindu (2016-2026).
**`iepirkuma_id` NAV unikaals tabula** -- viens iepirkums ar N dalam = N rindas.
**`iepirkuma_id` IR unikaals kad `ir_dalijums_dalas='Nē'`**.

---

### 3.6. `piedavajumu_atversanas` -- Piedaavajumu atversanas (e-konkursi)

**Avots:** `EIS_E_IEPIRKUMI_ATVERSANA_YYYY.csv` (2016-2026, apvienoti)
**Grauds:** Viena rinda = viena pretendenta piedaavajums vienam iepirkumam/dalai

```sql
CREATE TABLE piedavajumu_atversanas (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    datu_gads           INTEGER NOT NULL,
    iepirkuma_id        INTEGER NOT NULL,          -- FK uz iepirkumi.iepirkuma_id (logisks, ne fizisks)
    iepirkuma_nosaukums TEXT,
    iepirkuma_ident_nr  TEXT,
    pasutitaja_org_id   INTEGER REFERENCES organizacijas(org_id),
    citu_pasutitaju_vajadzibam TEXT,
    faktiskais_sanemejs TEXT,
    iepirkuma_prieksmeta_veids TEXT,
    cpv_kods_galvenais  TEXT,
    cpv_kodi_papildus   TEXT,
    iepirkuma_statuss   TEXT,
    regulejosais_tiesibu_akts TEXT,
    proceduras_veids    TEXT,
    dis_piemerosana     TEXT,                      -- "Jā" | "Nē" — dinamiskā iepirkumu sistēma (PIL 1.p. 5), 57.p.)
    hipersaite_eis      TEXT,
    hipersaite_iub      TEXT,
    sniegsanas_vieta    TEXT,
    -- Liguma termins
    liguma_termina_veids TEXT,
    liguma_termins      TEXT,
    liguma_termina_mervieniba TEXT,
    liguma_izpilde_no   TEXT,
    liguma_izpilde_lidz TEXT,
    -- Ligumcena
    ligumcenas_veids    TEXT,
    planota_ligumcena   REAL,
    planota_ligumcena_no REAL,
    planota_ligumcena_lidz REAL,
    ligumcenas_valuta   TEXT,
    -- Dalas
    ir_dalijums_dalas   TEXT,
    dalas_nr            TEXT,
    dalas_nosaukums     TEXT,
    dalas_statuss       TEXT,
    dalas_termina_veids TEXT,
    dalas_termins       TEXT,
    dalas_termina_mervieniba TEXT,
    dalas_izpilde_no    TEXT,
    dalas_izpilde_lidz  TEXT,
    dalas_ligumcenas_veids TEXT,
    dalas_ligumcena     REAL,
    dalas_ligumcena_no  REAL,
    dalas_ligumcena_lidz REAL,
    dalas_valuta        TEXT,
    -- Piedavajumu termini
    piedav_iesniegsanas_datums TEXT,
    piedav_iesniegsanas_laiks TEXT,
    piedav_atversanas_datums TEXT,
    piedav_atversanas_laiks TEXT,
    -- Pretendenta dati (galvenais merkkis)
    pretendenta_org_id  INTEGER REFERENCES organizacijas(org_id),
    pretendenta_nosaukums TEXT,                    -- Saglaba ari tekstu (jo pretendents var but arvalstu)
    pretendenta_reg_nr  TEXT,
    pretendenta_reg_nr_veids TEXT,
    pretendenta_valsts  TEXT,                      -- "LATVIJA" | "LIETUVA" | "IGAUNIJA" | ...
    pretendenta_iesniegsanas_datums TEXT,
    pretendenta_iesniegsanas_laiks TEXT
);

CREATE INDEX idx_atv_gads ON piedavajumu_atversanas(datu_gads);
CREATE INDEX idx_atv_iepirkuma_id ON piedavajumu_atversanas(iepirkuma_id);
CREATE INDEX idx_atv_pasutitaja ON piedavajumu_atversanas(pasutitaja_org_id);
CREATE INDEX idx_atv_pretendenta ON piedavajumu_atversanas(pretendenta_org_id);
CREATE INDEX idx_atv_pretendenta_valsts ON piedavajumu_atversanas(pretendenta_valsts);
CREATE INDEX idx_atv_datums ON piedavajumu_atversanas(piedav_iesniegsanas_datums);
```

**Kardinalitaate:** ~30K-80K rindu gadaa, kopaa ~553K rindu (2016-2026).
**`iepirkuma_id` atkartojas** -- viens iepirkums var sanemt desmitiem piedaavajumu (max noveerots: 197 piedaavajumi vienam iepirkumam).

---

### 3.7. `iepirkumu_grozijumi` -- Iepirkumu grozijumi (e-konkursi)

**Avots:** `EIS_E_IEPIRKUMI_GROZIJUMI_YYYY.csv` (2016-2026, apvienoti)
**Grauds:** Viena rinda = viens grozijuma notikums vienam iepirkumam/dalai

```sql
CREATE TABLE iepirkumu_grozijumi (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    datu_gads           INTEGER NOT NULL,
    iepirkuma_id        INTEGER NOT NULL,          -- FK uz iepirkumi.iepirkuma_id
    iepirkuma_nosaukums TEXT,
    iepirkuma_ident_nr  TEXT,
    pasutitaja_org_id   INTEGER REFERENCES organizacijas(org_id),
    iepirkuma_statuss   TEXT,
    izsludinasanas_datums TEXT,                    -- YYYY-MM-DD
    grozijumu_datums    TEXT,                      -- YYYY-MM-DD
    piedav_iesniegsanas_datumlaiks TEXT,           -- Aktualizets termins (YYYY-MM-DD HH:MM)
    ieintereseto_sanaksmes TEXT,
    atsauce_es_projekti TEXT,
    hipersaite_eis      TEXT,
    hipersaite_iub      TEXT,
    ir_dalijums_dalas   TEXT,
    dalu_iesniegsanas_nosacijumi TEXT,
    dalas_nr            TEXT,
    dalas_nosaukums     TEXT,
    dalas_statuss       TEXT
);

CREATE INDEX idx_groz_gads ON iepirkumu_grozijumi(datu_gads);
CREATE INDEX idx_groz_iepirkuma_id ON iepirkumu_grozijumi(iepirkuma_id);
CREATE INDEX idx_groz_datums ON iepirkumu_grozijumi(grozijumu_datums);
CREATE INDEX idx_groz_pasutitaja ON iepirkumu_grozijumi(pasutitaja_org_id);
```

**Kardinalitaate:** ~100-9K rindu gadaa (loti svarstas), kopaa ~54K rindu (2016-2026).
**`iepirkuma_id` atkartojas** -- viens iepirkums var tikt grozits vairaakas reizes (max 34 grozijumi vienam).
**Konteksts:** Tabula satur **iepirkuma procedūras grozījumus pirms līguma noslēgšanas** (PIL 28.p. "Paziņojums par līgumu un grozījumu veikšanu"); savukārt **grozījumi PĒC līguma noslēgšanas** (PIL 61.p.) parādās `iepirkumu_rezultati` ar `liguma_dok_veids='Līguma grozījumi'`.

---

### 3.8. `iepirkumu_rezultati` -- Iepirkumu rezultaati / Ligumi (e-konkursi)

**Avots:** `EIS_E_IEPIRKUMI_REZULTATI_YYYY.csv` (2018-2026, apvienoti)
**Grauds:** Viena rinda = viens liguma dokuments (ligums, grozijums vai izbeigsana) vienam iepirkumam

```sql
CREATE TABLE iepirkumu_rezultati (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    datu_gads           INTEGER NOT NULL,
    iepirkuma_id        INTEGER NOT NULL,
    iepirkuma_nosaukums TEXT,
    iepirkuma_ident_nr  TEXT,
    pasutitaja_org_id   INTEGER REFERENCES organizacijas(org_id),
    iepirkuma_statuss   TEXT,
    regulejosais_tiesibu_akts TEXT,
    proceduras_veids    TEXT,
    hipersaite_eis      TEXT,
    hipersaite_iub      TEXT,
    -- Dalas
    ir_dalijums_dalas   TEXT,
    dalas_nr            TEXT,
    dalas_nosaukums     TEXT,
    dalas_statuss       TEXT,
    -- Uzvaretajs
    uzvaretaja_org_id   INTEGER REFERENCES organizacijas(org_id),
    uzvaretaja_nosaukums TEXT,                     -- Saglaba tekstu (arvalstu uznemumi)
    uzvaretaja_reg_nr   TEXT,
    uzvaretaja_reg_nr_veids TEXT,
    uzvaretaja_valsts   TEXT,                      -- ISO3 kods: "LVA", "DEU", "FIN", "LTU", ...
    -- Liguma dokuments
    liguma_dok_veids    TEXT,                      -- "Līgums" | "Līguma grozījumi" | "Līguma izbeigšana"
    liguma_dok_id       TEXT,                      -- Unikaalais liguma dokumenta ID
    saistita_liguma_id  TEXT,                      -- Saistita liguma ID
    aktuala_summa       REAL,                      -- EUR
    aktuala_valuta      TEXT DEFAULT 'EUR',
    sakotneja_summa     REAL,
    sakotneja_valuta    TEXT,
    -- Liguma termins
    liguma_izpildes_termins TEXT,                  -- "Līdz saistību izpildei" | "Laika periods" | "Līdz summas apguvei" | "Beztermiņa"
    liguma_izpilde_no   TEXT,
    liguma_izpilde_lidz TEXT,
    ligums_ir_vv        TEXT,                      -- "Jā" | "Nē" — vai līgums ir vispārīgā vienošanās (PIL 1.p. 33), 56.p.)
    liguma_noslegsanas_datums TEXT,                -- YYYY-MM-DD
    liguma_publicesanas_datums TEXT,               -- YYYY-MM-DD
    izbeigsanas_datums  TEXT,                      -- YYYY-MM-DD (ja izbeigts pirms termiņa, PIL 64.p.)
    izbeigsanas_iemesls TEXT,
    -- PIL 60.p. = iepirkuma līgums; PIL 61.p. = līguma grozījumi; PIL 64.p. = pirmstermiņa izbeigšana
    CHECK (liguma_dok_veids IN ('Līgums', 'Līguma grozījumi', 'Līguma izbeigšana')),
    CHECK (liguma_izpildes_termins IN (
        'Līdz saistību izpildei', 'Laika periods',
        'Līdz summas apguvei', 'Beztermiņa', ''
    ))
);

CREATE INDEX idx_rez_gads ON iepirkumu_rezultati(datu_gads);
CREATE INDEX idx_rez_iepirkuma_id ON iepirkumu_rezultati(iepirkuma_id);
CREATE INDEX idx_rez_pasutitaja ON iepirkumu_rezultati(pasutitaja_org_id);
CREATE INDEX idx_rez_uzvaretaja ON iepirkumu_rezultati(uzvaretaja_org_id);
CREATE INDEX idx_rez_uzv_valsts ON iepirkumu_rezultati(uzvaretaja_valsts);
CREATE INDEX idx_rez_statuss ON iepirkumu_rezultati(iepirkuma_statuss);
CREATE INDEX idx_rez_dok_veids ON iepirkumu_rezultati(liguma_dok_veids);
CREATE INDEX idx_rez_nosl_datums ON iepirkumu_rezultati(liguma_noslegsanas_datums);
CREATE INDEX idx_rez_liguma_dok_id ON iepirkumu_rezultati(liguma_dok_id);
```

**Kardinalitaate:** ~20K-45K rindu gadaa, kopaa ~278K rindu (2018-2026).
**`iepirkuma_id` atkartojas** -- viens iepirkums var but vairaki ligumi (dazadas dalas + grozijumi + izbeigsanas).
**Skaitliskais sadalījums datos:** 252,181 Līgums + 26,032 Līguma grozījumi + 287 Līguma izbeigšana.
**VV identifikācija:** No 252,181 līgumiem 49,958 ir VV (`ligums_ir_vv='Jā'`) un 202,223 tiešie.

---

### 3.9. `publiskas_personas` -- Publisko personu un iestazu registrs

**Avots:** `ppi_public_persons_institutions.csv` (viens fails, atjaunojas katru dienu)
**Publicetajs:** LR Uznemumu registrs (Enterprise Register of Latvia)
**Grauds:** Viena rinda = viena publiska persona/iestade

```sql
CREATE TABLE publiskas_personas (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nosaukums           TEXT,                       -- Iestades nosaukums
    reg_nr              TEXT,                       -- Registracijas numurs (UR)
    nodoklu_maks_nr     TEXT,                       -- Nodoklu maksataja numurs
    dibinasanas_datums  TEXT,                       -- YYYY-MM-DD
    registracijas_datums TEXT,                      -- YYYY-MM-DD (registracijas datums UR)
    statuss             TEXT,                       -- "REGISTERED" | "REMOVED"
    statusa_detajas     TEXT,                       -- Statusa papildus informacija
    izslegt_datums      TEXT,                       -- YYYY-MM-DD (ja izslegt)
    neatkarigs_nodoklu_maks INTEGER,               -- 0/1 boolean
    iestades_veids      TEXT,                       -- "COURT" | "INSTITUTION_OF_DIRECT_ADMINISTRATION" | ...
    paklautibas_veids   TEXT,                       -- "SUBORDINATION" | "CONTROL" | ...
    timekla_vietne      TEXT,                       -- Majaslapa
    epasts              TEXT,                       -- E-pasts
    talrunis            TEXT,                       -- Talrunis
    adreses_kods        TEXT,                       -- Adreses registra kods
    adrese              TEXT,                       -- Pilna adrese
    ir_augstskola       INTEGER,                   -- 0/1 boolean
    augstakas_iestades_nosaukums TEXT,              -- Augstakas iestades nosaukums
    augstakas_iestades_reg_nr TEXT,                 -- Augstakas iestades reg. nr.
    augstakas_iestades_epasts TEXT,                 -- Augstakas iestades e-pasts
    dibinasanas_akta_nr TEXT,                       -- Dibinasanas dokumenta numurs
    dibinasanas_akta_datums TEXT,                   -- YYYY-MM-DD
    dibinasanas_akta_nosaukums TEXT,                -- Dokumenta nosaukums
    dibinasanas_akta_veids TEXT,                    -- "LAW" | "DECISION" | "OTHER" | ...
    likumdeveja_nosaukums TEXT,                     -- Likumdeveja/iesniedzeja nosaukums
    likumdeveja_reg_nr  TEXT                        -- Likumdeveja reg. nr.
);

CREATE INDEX idx_pp_reg_nr ON publiskas_personas(reg_nr);
CREATE INDEX idx_pp_statuss ON publiskas_personas(statuss);
CREATE INDEX idx_pp_iestades_veids ON publiskas_personas(iestades_veids);
CREATE INDEX idx_pp_augst_reg_nr ON publiskas_personas(augstakas_iestades_reg_nr);
```

**Kardinalitaate:** ~2,000-3,000 iestazu.
**`reg_nr` var savienot ar `organizacijas.reg_nr`** -- ne visas PPI iestades ir EIS lietotajas un ne visi EIS pasutitaji ir PPI registra.

---

### 3.10. `delegetas_personas` -- Delegeto personu saraksts

**Avots:** `ppi_delegated_entities.csv` (viens fails, atjaunojas katru dienu)
**Publicetajs:** LR Uznemumu registrs
**Grauds:** Viena rinda = viena privata persona, kurai delegetas publiskas parvaldes funkcijas

```sql
CREATE TABLE delegetas_personas (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nosaukums           TEXT,                       -- Delegetas personas nosaukums
    reg_nr              TEXT,                       -- Registracijas numurs
    registracijas_datums TEXT,                      -- YYYY-MM-DD
    izslegt_datums      TEXT,                       -- YYYY-MM-DD (ja izslegt)
    delegetaja_nosaukums TEXT,                      -- Delegejosas iestades nosaukums
    delegetaja_reg_nr   TEXT                        -- Delegejosas iestades reg. nr.
);

CREATE INDEX idx_dp_reg_nr ON delegetas_personas(reg_nr);
CREATE INDEX idx_dp_delegetaja_reg_nr ON delegetas_personas(delegetaja_reg_nr);
```

**Kardinalitaate:** ~300-500 delegetas personas.
**`delegetaja_reg_nr` savienojas ar `publiskas_personas.reg_nr`** -- delegejosa iestade vienmeer ir publiska persona.
**`reg_nr` var savienot ar `organizacijas.reg_nr`** -- privatpersonas, kam delegetas valsts funkcijas, var but ari EIS piegadataji.

---

### 3.11. `patiesie_labuma_guveji` -- Patiesie labuma guvēji (PLG)

**Avots:** `patiesie_labuma_guveji.csv` (viens fails, atjaunojas katru dienu)
**Publicētājs:** LR Uzņēmumu reģistrs
**Grauds:** Viena rinda = viena fiziskā persona (PLG) attiecībā uz vienu tiesību subjektu

```sql
CREATE TABLE patiesie_labuma_guveji (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    avota_id            INTEGER,                    -- UR sistēmas ID
    tiesibu_subjekta_reg_nr TEXT,                   -- Kontrolējamā uzņēmuma reg.nr. (sasaiste ar organizacijas.reg_nr)
    vards               TEXT,                       -- forename
    uzvards             TEXT,                       -- surname
    pers_kods_maskets   TEXT,                       -- DDMMYY-*****
    dzimsanas_datums    TEXT,                       -- YYYY-MM-DD
    valstspiederiba     TEXT,                       -- ISO valsts kods
    dzivesvietas_valsts TEXT,                       -- ISO valsts kods
    reg_datums          TEXT,                       -- YYYY-MM-DD (reģistrācijas datums UR)
    pedeja_izmainas_laiks TEXT                      -- ISO timestamp
);

-- Galvenais indekss: sasaiste ar organizāciju (uzvarētājs, piegādātājs utt.)
CREATE INDEX idx_plg_subj_reg_nr ON patiesie_labuma_guveji(tiesibu_subjekta_reg_nr);

-- KOMPOZĪTAIS PERSONAS INDEKSS — kritisks personu unikālai identifikācijai
-- Datu validācija pierāda: tikai (vārds + uzvārds + maskēts kods) kopā ir pietiekami unikāls
-- Sajaukšanas risks atsevišķi:
--   * "Jānis Bērziņš" = 49 dažādas personas (atšķiras pēc maskētā koda)
--   * Maskēts kods "050684-*****" = 25 dažādas personas (tas pats dzimšanas datums)
CREATE INDEX idx_plg_persona ON patiesie_labuma_guveji(vards, uzvards, pers_kods_maskets);

-- Ārvalstu PLG (tukšs maskēts kods, 7138 personas) — vajadzīga papildu dimensija
CREATE INDEX idx_plg_arvalstu ON patiesie_labuma_guveji(vards, uzvards, dzimsanas_datums, valstspiederiba);
```

**Kardinalitāte:** ~196,800 ierakstu, ~148,200 unikālu personu (kompozītā indeksa līmenī).

**Sajaukšanas analīze (validēta uz datiem):**
| Indekss | Unikālas | Sajaukšanas risks |
|---|---|---|
| Tikai vārds | 11,917 | Milzīgs |
| Tikai uzvārds | 57,763 | Liels |
| Vārds + uzvārds | 134,386 | 8,194 kombināciju nav unikālas |
| Tikai maskēts kods | 25,403 | 20,536 kodu nav unikāli |
| **Vārds + uzvārds + maskēts** | **148,216** | Pieņemams |

**Saites:** `tiesibu_subjekta_reg_nr ↔ organizacijas.reg_nr` — uzvarētāju/piegādātāju īpašnieku analīzei.

**Lietojuma piemērs — uzņēmumu grupēšana pa PLG:**
```sql
-- Personas, kas kontrolē vairākus uzņēmumus, kas piedalās EIS iepirkumos
SELECT vards, uzvards, pers_kods_maskets,
       COUNT(DISTINCT plg.tiesibu_subjekta_reg_nr) AS uznemumu_skaits,
       COUNT(DISTINCT ir.iepirkuma_id) AS uzvaru_skaits
FROM patiesie_labuma_guveji plg
JOIN organizacijas o ON plg.tiesibu_subjekta_reg_nr = o.reg_nr
LEFT JOIN iepirkumu_rezultati ir ON ir.uzvaretaja_org_id = o.org_id
                                  AND ir.liguma_dok_veids = 'Līgums'
GROUP BY vards, uzvards, pers_kods_maskets
HAVING uznemumu_skaits >= 3
ORDER BY uzvaru_skaits DESC;
```

---

## 4. Tabulu savstarpejas saites / Relationships

### 4.1. Logiski savienojumi (nav striktas FK, jo dati ir no atvertiem avotiem)

```
organizacijas.org_id  <──1:N──  e_pasutijumi.pasutitaja_org_id
organizacijas.org_id  <──1:N──  e_pasutijumi.piegadataja_org_id
organizacijas.org_id  <──1:N──  piegades.pasutitaja_org_id
organizacijas.org_id  <──1:N──  piegades.piegadataja_org_id
organizacijas.org_id  <──1:N──  iepirkumi.pasutitaja_org_id
organizacijas.org_id  <──1:N──  piedavajumu_atversanas.pasutitaja_org_id
organizacijas.org_id  <──1:N──  piedavajumu_atversanas.pretendenta_org_id
organizacijas.org_id  <──1:N──  iepirkumu_grozijumi.pasutitaja_org_id
organizacijas.org_id  <──1:N──  iepirkumu_rezultati.pasutitaja_org_id
organizacijas.org_id  <──1:N──  iepirkumu_rezultati.uzvaretaja_org_id

katalogi.kataloga_id  <──1:N──  e_pasutijumi.kataloga_id
katalogi.kataloga_id  <──1:N──  piegades.kataloga_id

e_pasutijumi.pasutijuma_nr ──1:N──> piegades.pasutijuma_nr  (logisks, ne FK)

iepirkumi.iepirkuma_id ──1:N──> piedavajumu_atversanas.iepirkuma_id
iepirkumi.iepirkuma_id ──1:N──> iepirkumu_grozijumi.iepirkuma_id
iepirkumi.iepirkuma_id ──1:N──> iepirkumu_rezultati.iepirkuma_id

publiskas_personas.reg_nr ──── organizacijas.reg_nr  (logisks savienojums)
delegetas_personas.delegetaja_reg_nr ──── publiskas_personas.reg_nr
delegetas_personas.reg_nr ──── organizacijas.reg_nr  (logisks savienojums)

patiesie_labuma_guveji.tiesibu_subjekta_reg_nr ──── organizacijas.reg_nr
    (PLG kontrolē uzņēmumu, kas piedalās EIS — kontroles ķēžu un grupu atklāšanai)
```

### 4.2. Cetras neatkaarigas domenas

EIS+UR dati sadalas **cetras neatkaarigas domenas**:

| Domena | Tabulas | Sasiiste | Avots |
|--------|---------|----------|-------|
| **e-pasutijumi** (e-katalogi, VV) | `e_pasutijumi`, `piegades`, `katalogi` | `pasutijuma_nr` | VDAA (EIS) |
| **e-konkursi** (iepirkumu proceduras) | `iepirkumi`, `piedavajumu_atversanas`, `iepirkumu_grozijumi`, `iepirkumu_rezultati` | `iepirkuma_id` | VDAA (EIS) |
| **publisko personu registrs** | `publiskas_personas`, `delegetas_personas` | `reg_nr` / `delegetaja_reg_nr` | LR Uzņēmumu reģistrs |
| **patiesie labuma guveji** (PLG) | `patiesie_labuma_guveji` | `tiesibu_subjekta_reg_nr` + kompozītais (vārds+uzvārds+maskēts kods) | LR Uzņēmumu reģistrs |

Visas domenas saistitas caur `reg_nr` -- organizaciju registracijas numuru (EIS domenas caur `organizacijas` tabulu, UR domenas tiesji).

**PLG domena loma:** Identificē fiziskās personas, kas kontrolē EIS piegādātāju/pretendentu uzņēmumus. Ļauj atklāt **uzņēmumu grupas** (vairāki uzņēmumi ar to pašu PLG) un **kontroles ķēdes** uzņēmumu profila analīzē.

---

## 5. Normalizacijas lemumi / Normalization Decisions

### 5.1. KAS tika normalizets un KAPEC

| Entitaate | Izcelta tabula | Pamatojums |
|-----------|---------------|------------|
| **Organizacijas** | `organizacijas` | ~16K unikalas organizacijas, atkartojas visos datos; centralizeta parvaldiba; gan pasutitaji, gan piegadataji/pretendenti viena tabula |
| **Katalogi** | `katalogi` | ~147 unikaali katalogi; numurs+nosaukums atkartojas simtiem rindu; ietaupa vietu |
| **PLG identitate** | `patiesie_labuma_guveji` ar kompozīto indeksu | 196K ieraksti → 148K unikalu personu; kompozīts indekss (vārds+uzvārds+maskēts kods) neceš normalizāciju atseviskja tabula, bet validē unikalitāti — "Jānis Bērziņš" vien = 49 dažādas personas |

### 5.2. KAS NETIKA normalizets un KAPEC

| Lauks/Entitaate | Unikalas vertiibas | Lemums | Pamatojums |
|------------------|-------------------|--------|------------|
| `pasutijuma_statuss` | 5 | TEXT + CHECK | Par maz vertibu; nav papildu atributu |
| `piegades_statuss` | 2 | TEXT + CHECK | Tikai 2 vertibas |
| `iepirkuma_statuss` | 8 | TEXT | Neliels skaits; var atskkirties starp tabulam |
| `iepirkuma_prieksmeta_veids` | 3+1 tusss | TEXT + CHECK | Triviaali 3 vertibas |
| `proceduras_veids` | 11 | TEXT | Ierobezots skaits; nav papildu atributu |
| `regulejosais_tiesibu_akts` | 3 | TEXT + CHECK | Tikai 3 likumi |
| `liguma_dok_veids` | 3 | TEXT + CHECK | Tikai 3 vertibas |
| `liguma_izpildes_termins` | 4 | TEXT + CHECK | Tikai 4 vertibas |
| `uzvaretaja_valsts` / `pretendenta_valsts` | ~20 | TEXT | Neliels skaits; dazads formats (ISO3 vs pilnais nosaukums) |
| `pvn_proc` | 4 (0, 5, 12, 21) | REAL | Skaitliska vertiba; nav ko normalizet |
| `ligumcenas_valuta` | 2 (EUR, LATI) | TEXT | Praktiski vienmeer EUR |
| `CPV kodi` | Daudz, bet glabaajas ka teksts | TEXT | CPV kods ir standartizets; parsesana/normalizacija iespejama velak ja nepieciesams |

### 5.3. Iespejama turpmaka normalizacija (ja rada vajadziba)

- **CPV kodu tabula** -- izvilet CPV koda numuru un aprakstu atsevisski; bus noderigs, ja grib grupet pec CPV klasifikacijas
- **Iepirkumu dalu tabula** -- izdalit dalas no `iepirkumi` tabulas, lai `iepirkuma_id` butu unikaals iepirkumu tabula
- **Adresu tabula** -- izdalit piegades adreses (pilseta, novads, indekss)
- **Valstu klasifikators** -- unificet ISO3 kodus un latviskos nosaukumus

---

## 6. Indeksu strategija / Indexing Strategy

Galvenie principi:
1. **Katrai FK kolonnai** -- indekss (JOIN veiktspeja)
2. **Biezzi filtreetaam kolonnaam** -- indekss (WHERE klauzulas)
3. **Datumu kolonnaam** -- indekss (laika periodu filtracija)
4. **`datu_gads`** -- indekss katrai gadu-tabulai (biezs filtrs)
5. **`iepirkuma_id`** un **`pasutijuma_nr`** -- indeksi savienojumiem starp tabulam

Kompozitie indeksi (uznemuma profila vaicajumiem):
```sql
-- Organizacijas pasutijumi noteikta gada
CREATE INDEX idx_epas_org_gads ON e_pasutijumi(pasutitaja_org_id, datu_gads);
-- Iepirkumi pec statusa un gada
CREATE INDEX idx_iep_statuss_gads ON iepirkumi(iepirkuma_statuss, datu_gads);

-- Rezultati: dok_veids + iepirkuma_id (covering index JOIN ar iepirkumi)
CREATE INDEX idx_rez_dok_iep ON iepirkumu_rezultati(liguma_dok_veids, iepirkuma_id);
-- Rezultati: uzvaretaja org + dok veids (uznemuma uzvaras)
CREATE INDEX idx_rez_uzv_dok ON iepirkumu_rezultati(uzvaretaja_org_id, liguma_dok_veids);
-- Piedavajumi: pretendenta org + iepirkuma_id (uznemuma piedavajumi)
CREATE INDEX idx_atv_pret_iep ON piedavajumu_atversanas(pretendenta_org_id, iepirkuma_id);
-- Iepirkumi: iepirkuma_id + cpv (covering index CPV vaicajumiem)
CREATE INDEX idx_iep_id_cpv ON iepirkumi(iepirkuma_id, cpv_kods_galvenais);
-- E-pasutijumi: piegadataja org + kataloga_id + gads (uznemuma kataloga ienemumi)
CREATE INDEX idx_epas_pieg_kat_gads ON e_pasutijumi(piegadataja_org_id, kataloga_id, datu_gads);
-- Piegades: piegadataja org + kataloga_id (uznemuma piegades)
CREATE INDEX idx_pieg_pieg_kat ON piegades(piegadataja_org_id, kataloga_id);
```

---

## 7. Apjomu novertejums / Volume Estimates

| Tabula | Rindu skaits (2026-02) | Gada diapazons |
|--------|------------------------|----------------|
| `organizacijas` | 16,187 | - |
| `katalogi` | 146 | - |
| `e_pasutijumi` | 4,049,359 | 2010-2026 |
| `piegades` | 4,070,599 | 2010-2026 |
| `iepirkumi` | 228,454 | 2016-2026 |
| `piedavajumu_atversanas` | 529,039 | 2016-2026 |
| `iepirkumu_grozijumi` | 51,905 | 2016-2026 |
| `iepirkumu_rezultati` | 268,241 | 2018-2026 |
| `publiskas_personas` | ~4,179 | - |
| `delegetas_personas` | ~299 | - |
| **KOPA** | **~9,218,000** | |

Aptuvenais datubaazes izmers: **~3.6 GB** (ar indeksiem).

---

## 8. Importa procesa apraksts / Import Process

### 8.1. Seciba

1. Izveidot tabulas (CREATE TABLE)
2. Importet `PASUTITAJI_KLAS.csv` --> `organizacijas` (ar ir_pasutitajs=1)
3. Importet `EIS_E_PASUT_APST_*.csv` (visi gadi) --> `e_pasutijumi`
   - Vienlaicigi papildinaat `organizacijas` ar jauniem piegadataajiem
   - Vienlaicigi papildinaat `katalogi`
4. Importet `EIS_E_PASUT_*.csv` (visi gadi) --> `piegades`
   - Papildinaat `organizacijas` un `katalogi`
5. Importet `EIS_E_IEPIRKUMI_IZSLUDINATIE_*.csv` --> `iepirkumi`
   - Papildinaat `organizacijas`
6. Importet `EIS_E_IEPIRKUMI_ATVERSANA_*.csv` --> `piedavajumu_atversanas`
   - Papildinaat `organizacijas` (pretendenti)
7. Importet `EIS_E_IEPIRKUMI_GROZIJUMI_*.csv` --> `iepirkumu_grozijumi`
8. Importet `EIS_E_IEPIRKUMI_REZULTATI_*.csv` --> `iepirkumu_rezultati`
   - Papildinaat `organizacijas` (uzvaretaji)
9. Importet `ppi_public_persons_institutions.csv` --> `publiskas_personas`
   - Neatkariga tabula, datumi jau ISO formata
10. Importet `ppi_delegated_entities.csv` --> `delegetas_personas`

### 8.2. Datumu konvertacija

Importa laika: `DD.MM.YYYY` --> `YYYY-MM-DD`

```python
# Piemers
def convert_date(d):
    if not d:
        return None
    parts = d.strip().split('.')
    if len(parts) == 3:
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
    return d
```

### 8.3. Organizaciju sasaiste

```python
# Piemers: atrast vai izveidot organizaciju pec reg_nr
def get_or_create_org(cursor, reg_nr, nosaukums, reg_nr_veids, augstak_org=None):
    cursor.execute("SELECT org_id FROM organizacijas WHERE reg_nr = ?", (reg_nr,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("""
        INSERT INTO organizacijas (reg_nr, nosaukums, reg_nr_veids, augstak_stavosa_organizacija)
        VALUES (?, ?, ?, ?)
    """, (reg_nr, nosaukums, reg_nr_veids, augstak_org))
    return cursor.lastrowid
```

### 8.4. Encoding

CSV faili ir **UTF-8 ar BOM** (baitu secibas atzime `\xEF\xBB\xBF` pirma kolonna). Importa laika jamaina `utf-8-sig` kodejums.

---

## 9. Otra datubaze: `eis_cenas.db` -- Pretendentu cenu piedavajumi / Bid Price Database

### 9.1. Merkis

`eis_cenas.db` ir atseviskka SQLite datubaze, kas satur no EIS PROPFIS dokumentiem izvilktos pretendentu cenu piedavajumus. Datus iegust skripts `03_scrape_propfis.py`, kas lejupelade un parsee PROPFIS DOCX failus no EIS.

**Saikne ar `eis.db`:** Iepirkumu identifikatori (`iepirkuma_id`) ir kopigi ar `eis.db` e-konkursu tabulum. Pretendentu registracijas numuri tiek samekleti no `eis.db` tabulas `piedavajumu_atversanas`.

### 9.2. Tabulu definicijas

#### `piedavajumi` -- Pretendentu piedavajumi

**Grauds:** Viena rinda = viena pretendenta piedavajums vienai iepirkuma dalai

```sql
CREATE TABLE piedavajumi (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    iepirkuma_id          INTEGER NOT NULL,          -- FK uz eis.db iepirkumi.iepirkuma_id
    iepirkuma_ident_nr    TEXT,                      -- Iepirkuma identifikacijas numurs
    dalas_nr              TEXT,                      -- Iepirkuma dalas numurs (ja ir)
    dalas_nosaukums       TEXT,                      -- Dalas nosaukums (no PROPFIS tabulas)
    pretendenta_nosaukums TEXT NOT NULL,             -- Pretendenta nosaukums (no PROPFIS)
    pretendenta_reg_nr    TEXT,                      -- Registracijas numurs (sameklets no eis.db)
    iesniegsanas_laiks    TEXT,                      -- Piedavajuma iesniegsanas datums/laiks (ja pieejams)
    propfis_doc_id        INTEGER,                   -- PROPFIS dokumenta ID EIS sistema
    scrapets              TEXT DEFAULT (datetime('now'))  -- Datu ieguves laiks
);
CREATE INDEX idx_pied_iepirkuma ON piedavajumi(iepirkuma_id);
CREATE INDEX idx_pied_pretend ON piedavajumi(pretendenta_nosaukums);
CREATE INDEX idx_pied_regnr ON piedavajumi(pretendenta_reg_nr);
CREATE INDEX idx_pied_dala ON piedavajumi(iepirkuma_id, dalas_nr);
```

#### `cenas` -- Piedavato cenu detalizacija

**Grauds:** Viena rinda = viena cenas kolonna viena pretendenta piedavajumam (long-table formata)

```sql
CREATE TABLE cenas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    piedavajuma_id  INTEGER NOT NULL REFERENCES piedavajumi(id),
    iepirkuma_id    INTEGER NOT NULL,
    kolonnas_nos    TEXT NOT NULL,                   -- Cenas kolonnas nosaukums (piem., "Kopeja liguma cena, EUR")
    kolonnas_idx    INTEGER NOT NULL DEFAULT 0,      -- Kolonnas kartibas numurs (0-based)
    cena_teksts     TEXT,                            -- Originalais teksts no PROPFIS sunas
    cena_eur        REAL,                            -- Parseta skaitliska vertiba EUR
    valuta          TEXT DEFAULT 'EUR'               -- Valutas kods
);
CREATE INDEX idx_cenas_pied ON cenas(piedavajuma_id);
CREATE INDEX idx_cenas_iepirkuma ON cenas(iepirkuma_id);
```

#### `scrape_log` -- Apstrades zurnaals

**Grauds:** Viena rinda = viena iepirkuma apstrades meginajums (nodrosina resume speju)

```sql
CREATE TABLE scrape_log (
    iepirkuma_id    INTEGER PRIMARY KEY,             -- Viens ieraksts uz iepirkumu
    statuss         TEXT NOT NULL,                   -- "OK" | "NO_PROPFIS" | "PDF_FORMAT" | "XLSX_FORMAT" | "DL_FAIL" | "PARSE_ERR" | "ERROR"
    propfis_doc_id  INTEGER,                         -- PROPFIS dokumenta ID (ja atrasts)
    piedavajumu_sk  INTEGER DEFAULT 0,               -- Cik piedavajumu izvilkti
    cenu_sk         INTEGER DEFAULT 0,               -- Cik cenu ierakstu izvilkti
    kludas_teksts   TEXT,                            -- Kludas apraksts (ja ir)
    scrapets        TEXT DEFAULT (datetime('now'))
);
```

### 9.3. Statuss kodi

| Statuss | Nozime |
|---------|--------|
| `OK` | Veiksmigi izvilkti dati no PROPFIS DOCX |
| `NO_PROPFIS` | Iepirkumam nav PROPFIS dokumenta |
| `PDF_FORMAT` | PROPFIS ir PDF formata (2016-2017 periods), automatiski neparsejams |
| `XLSX_FORMAT` | PROPFIS ir Excel formata (reti gadijumi) |
| `DL_FAIL` | PROPFIS lejupielade neizdevas |
| `PARSE_ERR` | DOCX parsesanas kluda |
| `ERROR` | Nezinama kluda |

### 9.4. Saites ar `eis.db`

```
eis.db                                    eis_cenas.db
┌──────────────────────────┐              ┌──────────────────┐
│ piedavajumu_atversanas   │              │ piedavajumi      │
│   iepirkuma_id ──────────┼──────────────┼─ iepirkuma_id    │
│   pretendenta_nosaukums  │   nosaukumu  │  pretendenta_nos │
│   pretendenta_reg_nr ────┼── sasaiste ──┼─ pretendenta_reg │
└──────────────────────────┘              │                  │
                                          │  id ─────────────┤
┌──────────────────────────┐              └────────┬─────────┘
│ iepirkumi                │                       │ 1
│   iepirkuma_id ──────────┤                       ▼ N
│   iepirkuma_ident_nr     │              ┌──────────────────┐
└──────────────────────────┘              │ cenas            │
                                          │   piedavajuma_id │
                                          │   cena_eur       │
                                          │   kolonnas_nos   │
                                          └──────────────────┘
```

---

## 10. Noderigi vaicajumu piemeri / Useful Query Examples

```sql
-- Top 10 pasutitaji pec kopejam summaam 2025. gada
SELECT o.nosaukums, SUM(ep.summa_bez_pvn) AS kopsumma
FROM e_pasutijumi ep
JOIN organizacijas o ON ep.pasutitaja_org_id = o.org_id
WHERE ep.datu_gads = 2025
GROUP BY o.nosaukums
ORDER BY kopsumma DESC
LIMIT 10;

-- Iepirkumi, kur uzvaretajs nav no Latvijas
SELECT ir.iepirkuma_nosaukums, ir.uzvaretaja_nosaukums, ir.uzvaretaja_valsts,
       ir.aktuala_summa
FROM iepirkumu_rezultati ir
WHERE ir.uzvaretaja_valsts != 'LVA' AND ir.uzvaretaja_valsts != ''
ORDER BY ir.aktuala_summa DESC;

-- Videjais piedavajumu skaits uz vienu iepirkumu pa gadiem
SELECT datu_gads, COUNT(*) * 1.0 / COUNT(DISTINCT iepirkuma_id) AS vid_piedavajumi
FROM piedavajumu_atversanas
GROUP BY datu_gads
ORDER BY datu_gads;

-- Pasutijumu un piegazu sasaiste
SELECT ep.pasutijuma_nr, ep.preces_nosaukums AS pasutita_prece,
       p.preces_nosaukums AS piegadata_prece, p.piegades_statuss
FROM e_pasutijumi ep
JOIN piegades p ON ep.pasutijuma_nr = p.pasutijuma_nr
WHERE ep.datu_gads = 2025
LIMIT 20;
```
