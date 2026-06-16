# eis-opendata-skill

**Rīku komplekts Latvijas Elektroniskās iepirkumu sistēmas (EIS) atvērto datu analīzei ar LLM.**

Projekts lejupielādē EIS atvērtos datus no [data.gov.lv](https://data.gov.lv/dati/lv/dataset?q=eis), apvieno tos vienā normalizētā SQLite datubāzē (`eis.db`) un pievieno **zināšanu bāzi (`EIS_SKILL.md`)**, kas ļauj jebkuram LLM (Claude Code, Codex u.c.) veidot pareizas analīzes un atskaites no šiem datiem — bez nepieciešamības pašam zināt iepirkumu likumdošanas un EIS datu nianses.

---

## Kāpēc šis projekts

EIS atvērtie dati ir publiski, bet **viegli interpretējami nepareizi**. Galvenā kļūda: visu līgumu summu sasummēšana dod ~2× pārvērtējumu, jo vispārīgo vienošanos (VV) summas ir tikai *augšējie griesti*, ne faktiskie ieņēmumi. Atvērtajos datos turklāt redzamas tikai 2 no 4 EIS apakšsistēmām, tāpēc ~75% centralizēto iepirkumu finansiālās realizācijas ir publiski neredzama.

`EIS_SKILL.md` iekapsulē šīs zināšanas — Publisko iepirkumu likuma (PIL) un MK noteikumu Nr. 816 atsauces, sarkanos karogus, gatavus SQL šablonus un interpretācijas robežas — tā, lai LLM ģenerētu metodoloģiski korektas atskaites.

**Lietošanas konteksts:** žurnālistiska analīze, akadēmiska pētniecība, audita pārbaudes, uzņēmumu profilu atskaites.

---

## Kā to lietot

Tipiskā darbplūsma — **bez koda rakstīšanas**:

1. Izveido datubāzi `eis.db` (skat. "Datubāzes sagatavošana" zemāk) vai izmanto jau esošu.
2. Atver **Claude Code** vai **Codex** (vai citu LLM aģentu ar piekļuvi failiem).
3. Iedod aģentam divus orientierus:
   - saiti / ceļu uz **`eis.db`** (SQLite datubāze),
   - saiti / ceļu uz **`EIS_SKILL.md`** (zināšanu bāze).
4. Brīvā tekstā pieprasi jebkādu pārskatu vai analīzi, piem.:
   > *"Izveido pārskatu par uzņēmuma ar reģ.nr. 40003XXXXXX faktiskajiem ieņēmumiem EIS no 2020. gada, atsevišķi nodalot tiešos līgumus un vispārīgās vienošanās."*
5. LLM nolasa `EIS_SKILL.md`, izpilda atbilstošos SQL vaicājumus pret `eis.db` un atgriež rezultātu kā **Markdown (`.md`) atskaiti**.

> **Padoms:** jo precīzāk norādi periodu, iestādi/uzņēmumu (reģ.nr.) un griezumu, jo precīzāka atskaite. `EIS_SKILL.md` 12. sadaļa satur atskaišu kontrolsarakstu, ko LLM izmanto rezultātu validēšanai.

---

## Datubāzes sagatavošana

Datubāzi veido divi soļi. Skripti izmanto tikai Python standartbibliotēku — papildu pakotnes nav vajadzīgas.

### 1. solis — lejupielāde

```bash
uv run 1_download/01_download.py            # inkrementāla lejupielāde (tikai mainītie/jaunie faili)
uv run 1_download/01_download.py --force     # pārraksta visus failus
```

Lejupielādē 80 CSV failus (9 datu kopas, 2010–2026) uz `raw-data/` mapi projekta saknē. Detaļas un papildu argumentus skat. [`1_download/README.md`](1_download/README.md).

### 2. solis — datubāzes būve

```bash
uv run 2_build_db/02_build_db.py             # izveido eis.db projekta saknē
uv run 2_build_db/02_build_db.py --db eis_prod.db   # cits DB faila nosaukums
```

Nolasa `raw-data/*.csv` un izveido normalizētu SQLite datubāzi `eis.db` (~3.9 GB, 11 tabulas, ~9.6M ierakstu).

---

## Repozitorija saturs

| Ceļš | Apraksts |
|------|----------|
| **`EIS_SKILL.md`** | **Galvenais fails** — EIS datu analīzes zināšanu bāze: PIL/MK 816 atsauces, 3 līgumu tipu pamats (T / V₁ / V₂), SQL šabloni, sarkanie karogi, atskaišu kontrolsaraksts |
| `eis-db-schema.md` | Datubāzes shēma — tabulas, kolonnas, saites, ER diagramma, projekcijas principi |
| `1_download/` | `01_download.py` + README — datu lejupielāde no data.gov.lv CKAN API |
| `2_build_db/` | `02_build_db.py` — CSV → normalizēta SQLite datubāze |
| `eis-docs/` | EIS lietotāju rokasgrāmatas, Publisko iepirkumu likums un MK 816 (Markdown) + `EIS_zinasanu_baze.md` |
| `eis.db` | *(ģenerēts)* SQLite datubāze — netiek glabāta repozitorijā |
| `raw-data/` | *(ģenerēts)* lejupielādētie CSV faili — netiek glabāti repozitorijā |

---

## Datu modelis īsumā

Datubāzes 11 tabulas atspoguļo 2 EIS apakšsistēmas:

- **E-pasūtījumi (e-katalogs):** `e_pasutijumi`, `piegades`, `katalogi`
- **E-konkursi:** `iepirkumi`, `piedavajumu_atversanas`, `iepirkumu_grozijumi`, `iepirkumu_rezultati`
- **Kopīgie / UR reģistri:** `organizacijas`, `publiskas_personas`, `delegetas_personas`, `patiesie_labuma_guveji`

Centrālā saite ir `organizacijas` tabula (pasūtītāji + piegādātāji), uz ko atsaucas visas darījumu tabulas. Pilnu shēmu skat. [`eis-db-schema.md`](eis-db-schema.md).

---

## Datu avots un licence

- **Avots:** [data.gov.lv](https://data.gov.lv/dati/lv/dataset?q=eis) — EIS atvērtie dati (publicē Valsts digitālās attīstības aģentūra) un Uzņēmumu reģistra dati.
- **Atjaunošana:** datu kopas data.gov.lv tiek atjauninātas katru dienu.
- **Licence:** CC0 1.0.

---

## Priekšnosacījumi

- Python 3.10+ (šajā vidē — palaiž ar [`uv`](https://docs.astral.sh/uv/): `uv run <skripts>`)
- Papildu pip pakotnes nav vajadzīgas (tikai standartbibliotēka)
- Interneta pieslēgums lejupielādei (kopējais apjoms ~vairāki GB)
