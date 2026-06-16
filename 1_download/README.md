# 1_download — Datu lejupielāde

Šī mape satur skriptu, kas lejupielādē **Elektroniskās iepirkumu sistēmas (EIS)** atvērtos datus no data.gov.lv un sagatavo tos tālākai apstrādei.

## Datu avots

Dati nāk no **[data.gov.lv](https://data.gov.lv/dati/lv/dataset?q=eis)** atvērto datu portāla. EIS (www.eis.gov.lv) ir Latvijas valsts centralizētā e-iepirkumu platforma, ko uztur **Valsts digitālās attīstības aģentūra** (VDAA, agrāk VRAA — sistēma kopš dibināšanas pieder vienai un tai pašai aģentūrai, kas pārdēvēta). Datu kopas tiek atjauninātas **katru dienu**, licence — **CC0 1.0**.

### Datu kopas

EIS atvērtie dati ir sadalīti 9 datu kopās — pirmās 7 datu kopas atspoguļo abas galvenās EIS apakšsistēmas (**e-pasūtījumi** un **e-konkursi**) un tās publicē VDAA. 8. un 9. datu kopas (publiskās personas/iestādes un patiesie labuma guvēji) publicē **LR Uzņēmumu reģistrs** — tās nepieciešamas piegādātāju/pasūtītāju identifikācijai un īpašumtiesību analīzei.

| # | Datu kopa data.gov.lv | Failu prefikss | Periods | Failu skaits |
|---|----------------------|----------------|---------|--------------|
| 1 | [Pirkuma pasūtījumu datu grupa](https://data.gov.lv/dati/lv/dataset/pirkuma-pasutijumu-datu-grupa) | `EIS_E_PASUT_APST_YYYY.csv` | 2010-2026 | 17 |
| 2 | [Piegāžu datu grupa](https://data.gov.lv/dati/lv/dataset/piegazu-datu-grupa) | `EIS_E_PASUT_YYYY.csv` | 2010-2026 | 17 |
| 3 | [Izsludināto iepirkumu datu grupa](https://data.gov.lv/dati/lv/dataset/izsludinato-iepirkumu-datu-grupa) | `EIS_E_IEPIRKUMI_IZSLUDINATIE_YYYY.csv` | 2016-2026 | 11 |
| 4 | [Iepirkumu piedāvājumu atvēršanu datu grupa](https://data.gov.lv/dati/lv/dataset/iepirkumu-piedavajumu-atversanu-datu-grupa) | `EIS_E_IEPIRKUMI_ATVERSANA_YYYY.csv` | 2016-2026 | 11 |
| 5 | [Iepirkumu rezultātu datu grupa](https://data.gov.lv/dati/lv/dataset/iepirkumu-rezultatu-datu-grupa) | `EIS_E_IEPIRKUMI_REZULTATI_YYYY.csv` | 2018-2026 | 9 |
| 6 | [Iepirkumu grozījumu datu grupa](https://data.gov.lv/dati/lv/dataset/iepirkumu-grozijumu-datu-grupa) | `EIS_E_IEPIRKUMI_GROZIJUMI_YYYY.csv` | 2016-2026 | 11 |
| 7 | [Pasūtītāju datu grupa](https://data.gov.lv/dati/lv/dataset/pasutitaju-datu-grupa) | `PASUTITAJI_KLAS.csv` | — | 1 |
| 8 | [Publisko personu un iestāžu saraksts](https://data.gov.lv/dati/lv/dataset/public-persons-institutions) (UR) | `ppi_*.csv` | — | 2 |
| 9 | [Patiesie labuma guvēji](https://data.gov.lv/dati/lv/dataset/patiesie-labuma-guveji) (UR) | `patiesie_labuma_guveji.csv` | — | 1 |
| | | | **Kopā** | **80** |

### CSV failu apraksti

#### E-pasūtījumu (e-kataloga) datu kopas

| Fails | EIS modulis | Apraksts |
|-------|-------------|----------|
| `EIS_E_PASUT_APST_YYYY.csv` | E-pasūtījumi | Apstiprināti pirkuma pasūtījumi e-katalogā — pasūtītājs, piegādātājs, VV numurs, summas (bez/ar PVN), statusi |
| `EIS_E_PASUT_YYYY.csv` | E-pasūtījumi | Faktiski veiktās piegādes — pavadzīmes, piegādātais daudzums, saņemšanas un kvalitātes apstiprinājumi |
| `PASUTITAJI_KLAS.csv` | E-pasūtījumi | Visu EIS reģistrēto pasūtītāju klasifikators (RegNr ir primārā atslēga, kas sasaista visus pasūtījumu failus) |

#### E-konkursu datu kopas

| Fails | EIS modulis | Apraksts |
|-------|-------------|----------|
| `EIS_E_IEPIRKUMI_IZSLUDINATIE_YYYY.csv` | E-konkursi | Iepirkumu paziņojumi — izsludinātās publisko iepirkumu procedūras |
| `EIS_E_IEPIRKUMI_ATVERSANA_YYYY.csv` | E-konkursi | Piedāvājumu atvēršanas protokoli — pretendenti, piedāvātās summas |
| `EIS_E_IEPIRKUMI_REZULTATI_YYYY.csv` | E-konkursi | Noslēgtie līgumi — iepirkumu rezultāti un izvēlētie piegādātāji |
| `EIS_E_IEPIRKUMI_GROZIJUMI_YYYY.csv` | E-konkursi | Līgumu grozījumi pēc noslēgšanas |

#### Klasifikatori un UR datu kopas

| Fails | Avots | Apraksts |
|-------|-------|----------|
| `ppi_public_persons_institutions.csv` | UR | Publisko personu un iestāžu reģistrs — visas EIS pasūtītāju potenciālās iestādes (reģ.nr., padotība, statuss, dibināšanas akts) |
| `ppi_delegated_entities.csv` | UR | Deleģētās personas un iestādes — privātpersonas, kam deleģētas publiskās pārvaldes funkcijas |
| `patiesie_labuma_guveji.csv` | UR | Patiesie labuma guvēji (PLG) — fiziskās personas, kas faktiski kontrolē Latvijas tiesību subjektus. Kolonas: ID, tiesību subjekta reģ. nr., vārds, uzvārds, daļēji maskēts personas kods, dzimšanas datums, valstspiederība (ISO), dzīvesvietas valsts, reģistrācijas datums. **Saite ar EIS:** `tiesību subjekta reg.nr.` ↔ `organizacijas.reg_nr` (piegādātāju un uzvarētāju īpašnieku analīzei). Publicēts saskaņā ar likuma "Par LR Uzņēmumu reģistru" 4.10 p. 12. d. |

> **Piezīme:** Detalizētus lauku aprakstus (kolonnu nosaukumus, datu tipus, metadatus) var apskatīt katras datu kopas lapā data.gov.lv, atverot atbilstošā resursa "Datu pārskats" sadaļu. Konceptuālu lauku interpretāciju un saistību ar EIS moduļiem skatīt EIS zināšanu bāzē (`EIS_zinasanu_baze.md`).

### Datu savstarpējās saistības

```
PASUTITAJI_KLAS.csv (RegNr)
    ↕ saite caur reģistrācijas numuru
EIS_E_PASUT_APST_*.csv (pasūtījumi)
    ↕ saite caur pasūtījuma numuru
EIS_E_PASUT_*.csv (piegādes)
```

```
EIS_E_IEPIRKUMI_IZSLUDINATIE_*.csv (iepirkuma ID)
    ↕
EIS_E_IEPIRKUMI_ATVERSANA_*.csv (piedāvājumu atvēršana)
    ↕
EIS_E_IEPIRKUMI_REZULTATI_*.csv (rezultāti un līgumi)
    ↕
EIS_E_IEPIRKUMI_GROZIJUMI_*.csv (līguma grozījumi)
```

## Faili

### `01_download.py`

Lejupielādē 80 CSV failus no data.gov.lv CKAN API — visas 9 datu kopas. Pēc noklusējuma strādā **inkrementāli**: pārbauda MD5 hash un atjaunina tikai failus, kuru saturs ir mainījies.

```
python 01_download.py                          # inkrementāla lejupielāde (tikai mainītie/jaunie)
python 01_download.py --force                  # pārraksta visus failus
python 01_download.py --output-dir ./my-data   # cita izvades mape
python 01_download.py --from-year 2022         # tikai 2022+ gada faili (PPI, PLG un PASUTITAJI_KLAS vienmēr)
python 01_download.py --only-years 2019,2020   # tikai konkrētie gadi (PPI, PLG un PASUTITAJI_KLAS vienmēr)
```

**Rezultāts:** `raw-data/*.csv` projekta saknē (visi 80 faili vienā plakanā mapē, gads ir kodēts faila nosaukumā EIS failiem)

> **Piezīme par PLG URL formātu:** EIS faili izmanto CKAN `dataset/{ds-id}/resource/{res-id}/download/...` formātu, bet `patiesie_labuma_guveji.csv` izmanto datastore dump endpoint `datastore/dump/{res-id}?bom=True`. Tas ir tāpēc, ka PLG dati ir publicēti caur CKAN DataStore (strukturēta datubāze), nevis kā vienkārša statiska CSV. Abi formāti atgriež UTF-8 CSV.

## Datu plūsma

```
data.gov.lv ──────────────────────────→ ../raw-data/*.csv
                01_download.py

                        ↓
              Nākamais solis: tālākā apstrāde
```

## Priekšnosacījumi

- Python 3.10+
- Nav papildu pip pakotņu (tikai stdlib: `urllib`, `hashlib`, `re`, `os`, `sys`, `time`)
- Interneta pieslēgums (kopējais apjoms ~vairāki GB)
