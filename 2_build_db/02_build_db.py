"""
EIS SQLite datubaazes izveide / EIS SQLite Database Builder
===========================================================
Nolasa CSV failus no raw-data/ mapes un izveido normalizetu SQLite datubazi.

Tabulas:
  - organizacijas    (centralizets org registrs)
  - katalogi         (e-katalogu registrs)
  - e_pasutijumi     (pirkuma pasutijumu rindas, 2010-2026)
  - piegades         (piegazu rindas, 2010-2026)
  - iepirkumi        (izsludinatie iepirkumi, 2016-2026)
  - piedavajumu_atversanas (piedavajumu atversanas, 2016-2026)
  - iepirkumu_grozijumi    (iepirkumu grozijumi, 2016-2026)
  - iepirkumu_rezultati    (rezultati/ligumi, 2018-2026)
  - publiskas_personas     (publisko personu un iestazu registrs)
  - delegetas_personas     (delegeto personu saraksts)
  - patiesie_labuma_guveji (PLG -- fiziskas personas, kas kontrole tiesibu subjektus)

Lietojums / Usage:
  python 02_build_db.py                        # Izveido eis.db
  python 02_build_db.py --db eis_prod.db       # Cits DB fails
  python 02_build_db.py --raw-dir ./my-data    # Cita avota mape
"""

import csv
import glob
import os
import re
import sqlite3
import sys
import time

# ---------------------------------------------------------------------------
# Konfiguracija / Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_RAW_DIR = os.path.join(PROJECT_ROOT, "raw-data")
DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, "eis.db")

# ---------------------------------------------------------------------------
# Paliigfunkcijas / Helpers
# ---------------------------------------------------------------------------


def convert_date(d):
    """DD.MM.YYYY -> YYYY-MM-DD. Atgriez None ja tukss vai nederigs."""
    if not d or not d.strip():
        return None
    d = d.strip()
    m = re.match(r"^(\d{2})\.(\d{2})\.(\d{4})$", d)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    # Ja jau ISO formata
    if re.match(r"^\d{4}-\d{2}-\d{2}$", d):
        return d
    return d


def convert_datetime(dt):
    """DD.MM.YYYY HH:MM -> YYYY-MM-DD HH:MM. Atgriez None ja tukss."""
    if not dt or not dt.strip():
        return None
    dt = dt.strip()
    m = re.match(r"^(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}:\d{2})", dt)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)} {m.group(4)}"
    return dt


def safe_float(val):
    """Konverte tekstu uz float, atgriez None ja nederigs."""
    if not val or not val.strip():
        return None
    try:
        return float(val.strip().replace(",", "."))
    except (ValueError, TypeError):
        return None


def safe_int(val):
    """Konverte tekstu uz int, atgriez None ja nederigs."""
    if not val or not val.strip():
        return None
    try:
        v = val.strip().replace(",", ".")
        return int(float(v))
    except (ValueError, TypeError):
        return None


def clean(val):
    """Notira teksta vertibu -- strip, None ja tukss."""
    if val is None:
        return None
    v = val.strip()
    return v if v else None


def extract_year_from_filename(filename):
    """Izvelk gadu no faila nosaukuma (piem., EIS_E_PASUT_APST_2026.csv -> 2026)."""
    m = re.search(r"_(\d{4})\.csv$", filename)
    if m:
        return int(m.group(1))
    return None


def _strip_eq(val):
    """Notira ='...' formatu: =\"vērtība\" -> vērtība."""
    v = val.strip()
    if v.startswith('="') and v.endswith('"'):
        return v[2:-1]
    if v.startswith("='") and v.endswith("'"):
        return v[2:-1]
    return v


def _semicolon_eq_reader(f):
    """Generators kas nolasa semicolon-delimited =\"val\" formata rindas."""
    for line in f:
        line = line.rstrip("\n").rstrip("\r")
        if not line:
            continue
        parts = line.split(";")
        yield [_strip_eq(p) for p in parts]


def open_csv(filepath):
    """Atver CSV failu ar UTF-8-sig kodejumu un atgriez (reader, header).
    Automatiski nosaka formatu:
      - comma-delimited (standarta CSV)
      - semicolon ar =\"val\" quoting (vecais EIS formats)
      - semicolon ar standarta CSV quoting (piem., PPI dati)
    """
    f = open(filepath, "r", encoding="utf-8-sig", newline="")
    # Nolasit pirmo rindu lai noteiktu formatu
    first_line = f.readline()
    header_raw = first_line.strip().lstrip("\ufeff")

    # Noteikt vai ir semicolon formats
    is_semicolon = ";" in header_raw and "," not in header_raw

    if is_semicolon:
        # Paskatities otra rinda lai noteiktu vai ir ="val" formats
        pos = f.tell()
        peek_line = f.readline().strip()
        f.seek(pos)

        if peek_line and ('="' in peek_line or "='" in peek_line):
            # Vecais EIS formats ar ="val" quoting
            header = [h.strip().lstrip("\ufeff") for h in header_raw.split(";")]
            reader = _semicolon_eq_reader(f)
        else:
            # Standarta semicolon-delimited CSV (piem., PPI dati)
            f.seek(0)
            reader = csv.reader(f, delimiter=";")
            header = next(reader)
            header = [h.strip().lstrip("\ufeff") for h in header]
    else:
        # Atgriezties uz sakumu un izmantot standarta csv.reader
        f.seek(0)
        reader = csv.reader(f)
        header = next(reader)
        header = [h.strip().lstrip("\ufeff") for h in header]

    return f, reader, header


def find_csv_files(raw_dir, pattern):
    """Atrod CSV failus pec patterns un sakarto pec gada."""
    files = glob.glob(os.path.join(raw_dir, pattern))
    files.sort()
    return files


# ---------------------------------------------------------------------------
# Organizaciju kess / Organization cache
# ---------------------------------------------------------------------------


class OrgCache:
    """Organizaciju kess -- izvairas no atkartotiem DB vaicajumiem."""

    def __init__(self, cursor):
        self.cursor = cursor
        self.cache = {}  # reg_nr -> org_id
        # Ieladet esosaas
        cursor.execute("SELECT org_id, reg_nr FROM organizacijas")
        for org_id, reg_nr in cursor.fetchall():
            self.cache[reg_nr] = org_id

    def get_or_create(
        self,
        reg_nr,
        nosaukums=None,
        reg_nr_veids=None,
        augstak_org=None,
        pvs_id=None,
        is_buyer=False,
        is_supplier=False,
    ):
        """Atgriez org_id. Izveido jaunu, ja neeksiste."""
        if not reg_nr or not reg_nr.strip():
            return None
        reg_nr = reg_nr.strip()

        if reg_nr in self.cache:
            org_id = self.cache[reg_nr]
            # Atjaunot flagus ja nepieciesams
            if is_buyer:
                self.cursor.execute(
                    "UPDATE organizacijas SET ir_pasutitajs = 1 WHERE org_id = ? AND ir_pasutitajs = 0",
                    (org_id,),
                )
            if is_supplier:
                self.cursor.execute(
                    "UPDATE organizacijas SET ir_piegadatajs = 1 WHERE org_id = ? AND ir_piegadatajs = 0",
                    (org_id,),
                )
            # Atjaunot pvs_id ja tagad zinams un iepriekss nebija
            if pvs_id:
                self.cursor.execute(
                    "UPDATE organizacijas SET pvs_id = ? WHERE org_id = ? AND pvs_id IS NULL",
                    (pvs_id, org_id),
                )
            return org_id

        self.cursor.execute(
            """
            INSERT INTO organizacijas (reg_nr, nosaukums, reg_nr_veids,
                augstak_stavosa_organizacija, pvs_id, ir_pasutitajs, ir_piegadatajs)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                reg_nr,
                clean(nosaukums),
                clean(reg_nr_veids),
                clean(augstak_org),
                clean(pvs_id),
                1 if is_buyer else 0,
                1 if is_supplier else 0,
            ),
        )
        org_id = self.cursor.lastrowid
        self.cache[reg_nr] = org_id
        return org_id


# ---------------------------------------------------------------------------
# Katalogu kess / Catalog cache
# ---------------------------------------------------------------------------


class CatalogCache:
    """Katalogu kess."""

    def __init__(self, cursor):
        self.cursor = cursor
        self.cache = {}  # kataloga_numurs -> kataloga_id

    def get_or_create(self, numurs, nosaukums=None):
        """Atgriez kataloga_id. Izveido jaunu, ja neeksiste."""
        if not numurs or not numurs.strip():
            return None
        numurs = numurs.strip()

        if numurs in self.cache:
            return self.cache[numurs]

        self.cursor.execute(
            "SELECT kataloga_id FROM katalogi WHERE kataloga_numurs = ?", (numurs,)
        )
        row = self.cursor.fetchone()
        if row:
            self.cache[numurs] = row[0]
            return row[0]

        self.cursor.execute(
            "INSERT INTO katalogi (kataloga_numurs, kataloga_nosaukums) VALUES (?, ?)",
            (numurs, clean(nosaukums)),
        )
        cat_id = self.cursor.lastrowid
        self.cache[numurs] = cat_id
        return cat_id


# ---------------------------------------------------------------------------
# Sheemas izveide / Schema creation
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS organizacijas (
    org_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    reg_nr          TEXT NOT NULL,
    nosaukums       TEXT,
    reg_nr_veids    TEXT,
    augstak_stavosa_organizacija TEXT,
    pvs_id          TEXT,
    eis_reg_datums  TEXT,
    ir_blokets      INTEGER DEFAULT 0,
    ir_dzests       INTEGER DEFAULT 0,
    ir_pasutitajs   INTEGER DEFAULT 0,
    ir_piegadatajs  INTEGER DEFAULT 0,
    UNIQUE(reg_nr)
);

CREATE TABLE IF NOT EXISTS katalogi (
    kataloga_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    kataloga_numurs TEXT NOT NULL UNIQUE,
    kataloga_nosaukums TEXT
);

CREATE TABLE IF NOT EXISTS e_pasutijumi (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    datu_gads           INTEGER NOT NULL,
    pasutitaja_org_id   INTEGER REFERENCES organizacijas(org_id),
    piegadataja_org_id  INTEGER REFERENCES organizacijas(org_id),
    pasutijuma_nr       TEXT NOT NULL,
    pasutijuma_statuss  TEXT,
    apstiprinasanas_datums TEXT,
    kataloga_id         INTEGER REFERENCES katalogi(kataloga_id),
    pozicijas_numurs    TEXT,
    preces_1_pazime     TEXT,
    preces_2_pazime     TEXT,
    preces_nosaukums    TEXT,
    preces_razotajs     TEXT,
    preces_razotaja_kods TEXT,
    max_piegades_datums TEXT,
    summa_bez_pvn       REAL,
    pvn_proc            REAL,
    pasutitais_skaits   INTEGER
);

CREATE TABLE IF NOT EXISTS piegades (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    datu_gads           INTEGER NOT NULL,
    pasutitaja_org_id   INTEGER REFERENCES organizacijas(org_id),
    piegadataja_org_id  INTEGER REFERENCES organizacijas(org_id),
    pasutijuma_nr       TEXT,
    kataloga_id         INTEGER REFERENCES katalogi(kataloga_id),
    pozicijas_nr        TEXT,
    preces_1_pazime     TEXT,
    preces_2_pazime     TEXT,
    pirkuma_izveid_datums TEXT,
    pavadzimes_nr       TEXT,
    piegades_statuss    TEXT,
    kval_apstipr_datums TEXT,
    summa_bez_pvn       REAL,
    pvn_proc            REAL,
    kval_skaits         INTEGER,
    preces_nosaukums    TEXT,
    preces_razotajs     TEXT,
    preces_razotaja_kods TEXT,
    piegades_adrese     TEXT
);

CREATE TABLE IF NOT EXISTS iepirkumi (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    datu_gads           INTEGER NOT NULL,
    iepirkuma_id        INTEGER NOT NULL,
    iepirkuma_nosaukums TEXT,
    iepirkuma_ident_nr  TEXT,
    pasutitaja_org_id   INTEGER REFERENCES organizacijas(org_id),
    citu_pasutitaju_vajadzibam TEXT,
    faktiskais_sanemejs TEXT,
    iepirkuma_prieksmeta_veids TEXT,
    cpv_kods_galvenais  TEXT,
    cpv_kodi_papildus   TEXT,
    iepirkuma_statuss   TEXT,
    izsludinasanas_datums TEXT,
    piedav_iesniegsanas_datums TEXT,
    piedav_iesniegsanas_laiks TEXT,
    ieintereseto_sanaksmes TEXT,
    sniegsanas_vieta    TEXT,
    liguma_termina_veids TEXT,
    liguma_termins      TEXT,
    liguma_termina_mervieniba TEXT,
    liguma_izpilde_no   TEXT,
    liguma_izpilde_lidz TEXT,
    ligumcenas_veids    TEXT,
    planota_ligumcena   REAL,
    planota_ligumcena_no REAL,
    planota_ligumcena_lidz REAL,
    ligumcenas_valuta   TEXT,
    regulejosais_tiesibu_akts TEXT,
    proceduras_veids    TEXT,
    kontaktpersona      TEXT,
    iesniegsanas_valoda TEXT,
    atsauce_es_projekti TEXT,
    pielaujami_varianti TEXT,
    uzvaretaja_izveles_metode TEXT,
    iesniegsanas_vieta  TEXT,
    hipersaite_eis      TEXT,
    hipersaite_iub      TEXT,
    ir_dalijums_dalas   TEXT,
    dalu_iesniegsanas_nosacijumi TEXT,
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
    dalas_valuta        TEXT
);

CREATE TABLE IF NOT EXISTS piedavajumu_atversanas (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    datu_gads           INTEGER NOT NULL,
    iepirkuma_id        INTEGER NOT NULL,
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
    dis_piemerosana     TEXT,
    hipersaite_eis      TEXT,
    hipersaite_iub      TEXT,
    sniegsanas_vieta    TEXT,
    liguma_termina_veids TEXT,
    liguma_termins      TEXT,
    liguma_termina_mervieniba TEXT,
    liguma_izpilde_no   TEXT,
    liguma_izpilde_lidz TEXT,
    ligumcenas_veids    TEXT,
    planota_ligumcena   REAL,
    planota_ligumcena_no REAL,
    planota_ligumcena_lidz REAL,
    ligumcenas_valuta   TEXT,
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
    piedav_iesniegsanas_datums TEXT,
    piedav_iesniegsanas_laiks TEXT,
    piedav_atversanas_datums TEXT,
    piedav_atversanas_laiks TEXT,
    pretendenta_org_id  INTEGER REFERENCES organizacijas(org_id),
    pretendenta_nosaukums TEXT,
    pretendenta_reg_nr  TEXT,
    pretendenta_reg_nr_veids TEXT,
    pretendenta_valsts  TEXT,
    pretendenta_iesniegsanas_datums TEXT,
    pretendenta_iesniegsanas_laiks TEXT
);

CREATE TABLE IF NOT EXISTS iepirkumu_grozijumi (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    datu_gads           INTEGER NOT NULL,
    iepirkuma_id        INTEGER NOT NULL,
    iepirkuma_nosaukums TEXT,
    iepirkuma_ident_nr  TEXT,
    pasutitaja_org_id   INTEGER REFERENCES organizacijas(org_id),
    iepirkuma_statuss   TEXT,
    izsludinasanas_datums TEXT,
    grozijumu_datums    TEXT,
    piedav_iesniegsanas_datumlaiks TEXT,
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

CREATE TABLE IF NOT EXISTS iepirkumu_rezultati (
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
    ir_dalijums_dalas   TEXT,
    dalas_nr            TEXT,
    dalas_nosaukums     TEXT,
    dalas_statuss       TEXT,
    uzvaretaja_org_id   INTEGER REFERENCES organizacijas(org_id),
    uzvaretaja_nosaukums TEXT,
    uzvaretaja_reg_nr   TEXT,
    uzvaretaja_reg_nr_veids TEXT,
    uzvaretaja_valsts   TEXT,
    liguma_dok_veids    TEXT,
    liguma_dok_id       TEXT,
    saistita_liguma_id  TEXT,
    aktuala_summa       REAL,
    aktuala_valuta      TEXT,
    sakotneja_summa     REAL,
    sakotneja_valuta    TEXT,
    liguma_izpildes_termins TEXT,
    liguma_izpilde_no   TEXT,
    liguma_izpilde_lidz TEXT,
    ligums_ir_vv        TEXT,
    liguma_noslegsanas_datums TEXT,
    liguma_publicesanas_datums TEXT,
    izbeigsanas_datums  TEXT,
    izbeigsanas_iemesls TEXT
);

CREATE TABLE IF NOT EXISTS publiskas_personas (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nosaukums           TEXT,
    reg_nr              TEXT,
    nodoklu_maks_nr     TEXT,
    dibinasanas_datums  TEXT,
    registracijas_datums TEXT,
    statuss             TEXT,
    statusa_detajas     TEXT,
    izslegt_datums      TEXT,
    neatkarigs_nodoklu_maks INTEGER,
    iestades_veids      TEXT,
    paklautibas_veids   TEXT,
    timekla_vietne      TEXT,
    epasts              TEXT,
    talrunis            TEXT,
    adreses_kods        TEXT,
    adrese              TEXT,
    ir_augstskola       INTEGER,
    augstakas_iestades_nosaukums TEXT,
    augstakas_iestades_reg_nr TEXT,
    augstakas_iestades_epasts TEXT,
    dibinasanas_akta_nr TEXT,
    dibinasanas_akta_datums TEXT,
    dibinasanas_akta_nosaukums TEXT,
    dibinasanas_akta_veids TEXT,
    likumdeveja_nosaukums TEXT,
    likumdeveja_reg_nr  TEXT
);

CREATE TABLE IF NOT EXISTS delegetas_personas (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nosaukums           TEXT,
    reg_nr              TEXT,
    registracijas_datums TEXT,
    izslegt_datums      TEXT,
    delegetaja_nosaukums TEXT,
    delegetaja_reg_nr   TEXT
);

CREATE TABLE IF NOT EXISTS patiesie_labuma_guveji (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    avota_id            INTEGER,                    -- UR sistemas ID (CSV 'id')
    tiesibu_subjekta_reg_nr TEXT,                   -- kontrolejama uznemuma reg.nr. (CSV 'legal_entity_registration_number')
    vards               TEXT,                       -- (CSV 'forename')
    uzvards             TEXT,                       -- (CSV 'surname')
    pers_kods_maskets   TEXT,                       -- DDMMYY-***** (CSV 'latvian_identity_number_masked')
    dzimsanas_datums    TEXT,                       -- YYYY-MM-DD (CSV 'birth_date')
    valstspiederiba     TEXT,                       -- ISO valsts kods (CSV 'nationality')
    dzivesvietas_valsts TEXT,                       -- ISO valsts kods (CSV 'residence')
    reg_datums          TEXT,                       -- YYYY-MM-DD (CSV 'registered_on')
    pedeja_izmainas_laiks TEXT                      -- ISO timestamp (CSV 'last_modified_at')
);
"""

INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_org_reg_nr ON organizacijas(reg_nr);
CREATE INDEX IF NOT EXISTS idx_org_nosaukums ON organizacijas(nosaukums);
CREATE INDEX IF NOT EXISTS idx_org_augstak ON organizacijas(augstak_stavosa_organizacija);
CREATE INDEX IF NOT EXISTS idx_kat_numurs ON katalogi(kataloga_numurs);

CREATE INDEX IF NOT EXISTS idx_epas_gads ON e_pasutijumi(datu_gads);
CREATE INDEX IF NOT EXISTS idx_epas_pasut_nr ON e_pasutijumi(pasutijuma_nr);
CREATE INDEX IF NOT EXISTS idx_epas_pasutitaja ON e_pasutijumi(pasutitaja_org_id);
CREATE INDEX IF NOT EXISTS idx_epas_piegadataja ON e_pasutijumi(piegadataja_org_id);
CREATE INDEX IF NOT EXISTS idx_epas_kataloga ON e_pasutijumi(kataloga_id);
CREATE INDEX IF NOT EXISTS idx_epas_datums ON e_pasutijumi(apstiprinasanas_datums);
CREATE INDEX IF NOT EXISTS idx_epas_statuss ON e_pasutijumi(pasutijuma_statuss);
CREATE INDEX IF NOT EXISTS idx_epas_org_gads ON e_pasutijumi(pasutitaja_org_id, datu_gads);

CREATE INDEX IF NOT EXISTS idx_pieg_gads ON piegades(datu_gads);
CREATE INDEX IF NOT EXISTS idx_pieg_pasut_nr ON piegades(pasutijuma_nr);
CREATE INDEX IF NOT EXISTS idx_pieg_pasutitaja ON piegades(pasutitaja_org_id);
CREATE INDEX IF NOT EXISTS idx_pieg_piegadataja ON piegades(piegadataja_org_id);
CREATE INDEX IF NOT EXISTS idx_pieg_kataloga ON piegades(kataloga_id);
CREATE INDEX IF NOT EXISTS idx_pieg_kval_dat ON piegades(kval_apstipr_datums);
CREATE INDEX IF NOT EXISTS idx_pieg_statuss ON piegades(piegades_statuss);

CREATE INDEX IF NOT EXISTS idx_iep_gads ON iepirkumi(datu_gads);
CREATE INDEX IF NOT EXISTS idx_iep_id ON iepirkumi(iepirkuma_id);
CREATE INDEX IF NOT EXISTS idx_iep_ident_nr ON iepirkumi(iepirkuma_ident_nr);
CREATE INDEX IF NOT EXISTS idx_iep_pasutitaja ON iepirkumi(pasutitaja_org_id);
CREATE INDEX IF NOT EXISTS idx_iep_statuss ON iepirkumi(iepirkuma_statuss);
CREATE INDEX IF NOT EXISTS idx_iep_datums ON iepirkumi(izsludinasanas_datums);
CREATE INDEX IF NOT EXISTS idx_iep_cpv ON iepirkumi(cpv_kods_galvenais);
CREATE INDEX IF NOT EXISTS idx_iep_procedura ON iepirkumi(proceduras_veids);
CREATE INDEX IF NOT EXISTS idx_iep_statuss_gads ON iepirkumi(iepirkuma_statuss, datu_gads);
CREATE INDEX IF NOT EXISTS idx_iep_prieksmets ON iepirkumi(iepirkuma_prieksmeta_veids);

CREATE INDEX IF NOT EXISTS idx_atv_gads ON piedavajumu_atversanas(datu_gads);
CREATE INDEX IF NOT EXISTS idx_atv_iepirkuma_id ON piedavajumu_atversanas(iepirkuma_id);
CREATE INDEX IF NOT EXISTS idx_atv_pasutitaja ON piedavajumu_atversanas(pasutitaja_org_id);
CREATE INDEX IF NOT EXISTS idx_atv_pretendenta ON piedavajumu_atversanas(pretendenta_org_id);
CREATE INDEX IF NOT EXISTS idx_atv_pretendenta_valsts ON piedavajumu_atversanas(pretendenta_valsts);
CREATE INDEX IF NOT EXISTS idx_atv_datums ON piedavajumu_atversanas(piedav_iesniegsanas_datums);

CREATE INDEX IF NOT EXISTS idx_groz_gads ON iepirkumu_grozijumi(datu_gads);
CREATE INDEX IF NOT EXISTS idx_groz_iepirkuma_id ON iepirkumu_grozijumi(iepirkuma_id);
CREATE INDEX IF NOT EXISTS idx_groz_datums ON iepirkumu_grozijumi(grozijumu_datums);
CREATE INDEX IF NOT EXISTS idx_groz_pasutitaja ON iepirkumu_grozijumi(pasutitaja_org_id);

CREATE INDEX IF NOT EXISTS idx_rez_gads ON iepirkumu_rezultati(datu_gads);
CREATE INDEX IF NOT EXISTS idx_rez_iepirkuma_id ON iepirkumu_rezultati(iepirkuma_id);
CREATE INDEX IF NOT EXISTS idx_rez_pasutitaja ON iepirkumu_rezultati(pasutitaja_org_id);
CREATE INDEX IF NOT EXISTS idx_rez_uzvaretaja ON iepirkumu_rezultati(uzvaretaja_org_id);
CREATE INDEX IF NOT EXISTS idx_rez_uzv_valsts ON iepirkumu_rezultati(uzvaretaja_valsts);
CREATE INDEX IF NOT EXISTS idx_rez_statuss ON iepirkumu_rezultati(iepirkuma_statuss);
CREATE INDEX IF NOT EXISTS idx_rez_dok_veids ON iepirkumu_rezultati(liguma_dok_veids);
CREATE INDEX IF NOT EXISTS idx_rez_nosl_datums ON iepirkumu_rezultati(liguma_noslegsanas_datums);
CREATE INDEX IF NOT EXISTS idx_rez_liguma_dok_id ON iepirkumu_rezultati(liguma_dok_id);

CREATE INDEX IF NOT EXISTS idx_pp_reg_nr ON publiskas_personas(reg_nr);
CREATE INDEX IF NOT EXISTS idx_pp_statuss ON publiskas_personas(statuss);
CREATE INDEX IF NOT EXISTS idx_pp_iestades_veids ON publiskas_personas(iestades_veids);
CREATE INDEX IF NOT EXISTS idx_pp_augst_reg_nr ON publiskas_personas(augstakas_iestades_reg_nr);

CREATE INDEX IF NOT EXISTS idx_dp_reg_nr ON delegetas_personas(reg_nr);
CREATE INDEX IF NOT EXISTS idx_dp_delegetaja_reg_nr ON delegetas_personas(delegetaja_reg_nr);

-- PLG indeksi
-- Galvenais: kontrolejama tiesibu subjekta reg.nr. (sasaiste ar organizacijas.reg_nr)
CREATE INDEX IF NOT EXISTS idx_plg_subj_reg_nr ON patiesie_labuma_guveji(tiesibu_subjekta_reg_nr);
-- KOMPOZITAIS PERSONAS INDEKSS: vards + uzvards + maskets pers.kods
-- Pamatojums: 8194 (V+U) kombinacijas ar vairakiem maskotiem kodiem (piem., "Janis Berzins" = 49 personas)
-- un 20536 maskoti kodi ar vairakiem vardiem. Tikai visi 3 kopa veido pietiekami unikalu PLG identifikatoru.
CREATE INDEX IF NOT EXISTS idx_plg_persona ON patiesie_labuma_guveji(vards, uzvards, pers_kods_maskets);
-- Papildu indekss arvalstu PLG, kuriem masketais kods ir tukss (7138 personas)
-- Tiem nepieciesams birth_date + nationality, lai atskirtu
CREATE INDEX IF NOT EXISTS idx_plg_arvalstu ON patiesie_labuma_guveji(vards, uzvards, dzimsanas_datums, valstspiederiba);

-- Kompozītie indeksi uzņēmuma profila vaicājumiem
-- Rezultāti: dok_veids + iepirkuma_id (covering index JOIN ar iepirkumi)
CREATE INDEX IF NOT EXISTS idx_rez_dok_iep ON iepirkumu_rezultati(liguma_dok_veids, iepirkuma_id);
-- Rezultāti: uzvarētāja org + dok veids (uzņēmuma uzvaras)
CREATE INDEX IF NOT EXISTS idx_rez_uzv_dok ON iepirkumu_rezultati(uzvaretaja_org_id, liguma_dok_veids);
-- Piedāvājumi: pretendenta org + iepirkuma_id (uzņēmuma piedāvājumi)
CREATE INDEX IF NOT EXISTS idx_atv_pret_iep ON piedavajumu_atversanas(pretendenta_org_id, iepirkuma_id);
-- Iepirkumi: iepirkuma_id + cpv (covering index CPV vaicājumiem)
CREATE INDEX IF NOT EXISTS idx_iep_id_cpv ON iepirkumi(iepirkuma_id, cpv_kods_galvenais);
-- E-pasūtījumi: piegādātāja org + kataloga_id + gads (uzņēmuma kataloga ieņēmumi)
CREATE INDEX IF NOT EXISTS idx_epas_pieg_kat_gads ON e_pasutijumi(piegadataja_org_id, kataloga_id, datu_gads);
-- Piegādes: piegādātāja org + kataloga_id (uzņēmuma piegādes)
CREATE INDEX IF NOT EXISTS idx_pieg_pieg_kat ON piegades(piegadataja_org_id, kataloga_id);
"""

# ---------------------------------------------------------------------------
# Importa funkcijas / Import functions
# ---------------------------------------------------------------------------


def import_pasutitaji(cursor, orgs, raw_dir):
    """Importet PASUTITAJI_KLAS.csv -> organizacijas tabula."""
    filepath = os.path.join(raw_dir, "PASUTITAJI_KLAS.csv")
    if not os.path.exists(filepath):
        print("  BRIDINAAJUMS: PASUTITAJI_KLAS.csv nav atrasts, izlaists.")
        return 0

    f, reader, header = open_csv(filepath)
    count = 0
    for row in reader:
        if len(row) < 8:
            continue
        reg_nr = clean(row[2])
        if not reg_nr:
            continue
        nosaukums = clean(row[1])
        reg_nr_veids = clean(row[3])
        augstak_org = clean(row[4])
        reg_datums = convert_date(row[5]) if len(row) > 5 else None
        blokets = 1 if row[6].strip() in ("Bloķēts", "Blokets") else 0
        dzests = 1 if row[7].strip() in ("Dzēsts", "Dzests") else 0

        org_id = orgs.get_or_create(
            reg_nr, nosaukums, reg_nr_veids, augstak_org, is_buyer=True
        )
        # Atjaunot papildu laukus
        cursor.execute(
            """
            UPDATE organizacijas SET eis_reg_datums = ?, ir_blokets = ?, ir_dzests = ?
            WHERE org_id = ?
        """,
            (reg_datums, blokets, dzests, org_id),
        )
        count += 1

    f.close()
    return count


def import_e_pasutijumi(cursor, orgs, cats, raw_dir):
    """Importet EIS_E_PASUT_APST_*.csv -> e_pasutijumi tabula."""
    files = find_csv_files(raw_dir, "EIS_E_PASUT_APST_*.csv")
    total = 0

    for filepath in files:
        year = extract_year_from_filename(os.path.basename(filepath))
        if year is None:
            continue

        f, reader, header = open_csv(filepath)
        batch = []
        count = 0

        for row in reader:
            if len(row) < 23:
                continue

            pas_org_id = orgs.get_or_create(
                row[2], row[1], row[3], row[4], is_buyer=True
            )
            pieg_org_id = orgs.get_or_create(row[9], row[8], row[10], is_supplier=True)
            cat_id = cats.get_or_create(row[11], row[12])

            batch.append(
                (
                    year,
                    pas_org_id,
                    pieg_org_id,
                    clean(row[5]),  # pasutijuma_nr
                    clean(row[6]),  # statuss
                    convert_date(row[7]),  # apstiprinasanas_datums
                    cat_id,
                    clean(row[13]),  # pozicijas_numurs
                    clean(row[14]),  # preces_1_pazime
                    clean(row[15]),  # preces_2_pazime
                    clean(row[16]),  # preces_nosaukums
                    clean(row[17]),  # preces_razotajs
                    clean(row[18]),  # preces_razotaja_kods
                    convert_date(row[19]),  # max_piegades_datums
                    safe_float(row[20]),  # summa_bez_pvn
                    safe_float(row[21]),  # pvn_proc
                    safe_int(row[22]),  # pasutitais_skaits
                )
            )
            count += 1

            if len(batch) >= 5000:
                cursor.executemany(
                    """
                    INSERT INTO e_pasutijumi (
                        datu_gads, pasutitaja_org_id, piegadataja_org_id,
                        pasutijuma_nr, pasutijuma_statuss, apstiprinasanas_datums,
                        kataloga_id, pozicijas_numurs, preces_1_pazime, preces_2_pazime,
                        preces_nosaukums, preces_razotajs, preces_razotaja_kods,
                        max_piegades_datums, summa_bez_pvn, pvn_proc, pasutitais_skaits
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                    batch,
                )
                batch.clear()

        if batch:
            cursor.executemany(
                """
                INSERT INTO e_pasutijumi (
                    datu_gads, pasutitaja_org_id, piegadataja_org_id,
                    pasutijuma_nr, pasutijuma_statuss, apstiprinasanas_datums,
                    kataloga_id, pozicijas_numurs, preces_1_pazime, preces_2_pazime,
                    preces_nosaukums, preces_razotajs, preces_razotaja_kods,
                    max_piegades_datums, summa_bez_pvn, pvn_proc, pasutitais_skaits
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
                batch,
            )

        f.close()
        total += count
        print(f"    {os.path.basename(filepath)}: {count:,} rindas")

    return total


def import_piegades(cursor, orgs, cats, raw_dir):
    """Importet EIS_E_PASUT_*.csv (piegazu dati) -> piegades tabula."""
    files = find_csv_files(raw_dir, "EIS_E_PASUT_*.csv")
    # Izslegt PASUT_APST failus
    files = [f for f in files if "PASUT_APST" not in os.path.basename(f)]
    total = 0

    for filepath in files:
        year = extract_year_from_filename(os.path.basename(filepath))
        if year is None:
            continue

        f, reader, header = open_csv(filepath)
        batch = []
        count = 0

        for row in reader:
            if len(row) < 25:
                continue

            pas_org_id = orgs.get_or_create(
                row[2], row[1], row[3], row[4], is_buyer=True
            )
            pieg_org_id = orgs.get_or_create(row[7], row[6], row[8], is_supplier=True)
            cat_id = cats.get_or_create(row[9], row[10])

            batch.append(
                (
                    year,
                    pas_org_id,
                    pieg_org_id,
                    clean(row[5]),  # pasutijuma_nr
                    cat_id,
                    clean(row[11]),  # pozicijas_nr
                    clean(row[12]),  # preces_1_pazime
                    clean(row[13]),  # preces_2_pazime
                    convert_date(row[14]),  # pirkuma_izveid_datums
                    clean(row[15]),  # pavadzimes_nr
                    clean(row[16]),  # piegades_statuss
                    convert_date(row[17]),  # kval_apstipr_datums
                    safe_float(row[18]),  # summa_bez_pvn
                    safe_float(row[19]),  # pvn_proc
                    safe_int(row[20]),  # kval_skaits
                    clean(row[21]),  # preces_nosaukums
                    clean(row[22]),  # preces_razotajs
                    clean(row[23]),  # preces_razotaja_kods
                    clean(row[24]),  # piegades_adrese
                )
            )
            count += 1

            if len(batch) >= 5000:
                cursor.executemany(
                    """
                    INSERT INTO piegades (
                        datu_gads, pasutitaja_org_id, piegadataja_org_id,
                        pasutijuma_nr, kataloga_id, pozicijas_nr,
                        preces_1_pazime, preces_2_pazime, pirkuma_izveid_datums,
                        pavadzimes_nr, piegades_statuss, kval_apstipr_datums,
                        summa_bez_pvn, pvn_proc, kval_skaits,
                        preces_nosaukums, preces_razotajs, preces_razotaja_kods,
                        piegades_adrese
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                    batch,
                )
                batch.clear()

        if batch:
            cursor.executemany(
                """
                INSERT INTO piegades (
                    datu_gads, pasutitaja_org_id, piegadataja_org_id,
                    pasutijuma_nr, kataloga_id, pozicijas_nr,
                    preces_1_pazime, preces_2_pazime, pirkuma_izveid_datums,
                    pavadzimes_nr, piegades_statuss, kval_apstipr_datums,
                    summa_bez_pvn, pvn_proc, kval_skaits,
                    preces_nosaukums, preces_razotajs, preces_razotaja_kods,
                    piegades_adrese
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
                batch,
            )

        f.close()
        total += count
        print(f"    {os.path.basename(filepath)}: {count:,} rindas")

    return total


def import_iepirkumi(cursor, orgs, raw_dir):
    """Importet EIS_E_IEPIRKUMI_IZSLUDINATIE_*.csv -> iepirkumi tabula."""
    files = find_csv_files(raw_dir, "EIS_E_IEPIRKUMI_IZSLUDINATIE_*.csv")
    total = 0

    for filepath in files:
        year = extract_year_from_filename(os.path.basename(filepath))
        if year is None:
            continue

        f, reader, header = open_csv(filepath)
        batch = []
        count = 0

        for row in reader:
            if len(row) < 54:
                continue

            pas_org_id = orgs.get_or_create(
                row[4], row[3], row[5], row[7], pvs_id=row[6], is_buyer=True
            )

            batch.append(
                (
                    year,
                    safe_int(row[0]),  # iepirkuma_id
                    clean(row[1]),  # nosaukums
                    clean(row[2]),  # ident_nr
                    pas_org_id,
                    clean(row[8]),  # citu_pasutitaju_vajadzibam
                    clean(row[9]),  # faktiskais_sanemejs
                    clean(row[10]),  # prieksmeta_veids
                    clean(row[11]),  # cpv_galvenais
                    clean(row[12]),  # cpv_papildus
                    clean(row[13]),  # statuss
                    convert_date(row[14]),  # izsludinasanas_datums
                    convert_date(row[15]),  # piedav_iesniegsanas_datums
                    clean(row[16]),  # piedav_iesniegsanas_laiks
                    clean(row[17]),  # ieintereseto_sanaksmes
                    clean(row[18]),  # sniegsanas_vieta
                    clean(row[19]),  # liguma_termina_veids
                    clean(row[20]),  # liguma_termins
                    clean(row[21]),  # liguma_termina_mervieniba
                    convert_date(row[22]),  # liguma_izpilde_no
                    convert_date(row[23]),  # liguma_izpilde_lidz
                    clean(row[24]),  # ligumcenas_veids
                    safe_float(row[25]),  # planota_ligumcena
                    safe_float(row[26]),  # planota_ligumcena_no
                    safe_float(row[27]),  # planota_ligumcena_lidz
                    clean(row[28]),  # ligumcenas_valuta
                    clean(row[29]),  # regulejosais_tiesibu_akts
                    clean(row[30]),  # proceduras_veids
                    clean(row[31]),  # kontaktpersona
                    clean(row[32]),  # iesniegsanas_valoda
                    clean(row[33]),  # atsauce_es_projekti
                    clean(row[34]),  # pielaujami_varianti
                    clean(row[35]),  # uzvaretaja_izveles_metode
                    clean(row[36]),  # iesniegsanas_vieta
                    clean(row[37]),  # hipersaite_eis
                    clean(row[38]),  # hipersaite_iub
                    clean(row[39]),  # ir_dalijums_dalas
                    clean(row[40]),  # dalu_iesniegsanas_nosacijumi
                    clean(row[41]),  # dalas_nr
                    clean(row[42]),  # dalas_nosaukums
                    clean(row[43]),  # dalas_statuss
                    clean(row[44]),  # dalas_termina_veids
                    clean(row[45]),  # dalas_termins
                    clean(row[46]),  # dalas_termina_mervieniba
                    convert_date(row[47]),  # dalas_izpilde_no
                    convert_date(row[48]),  # dalas_izpilde_lidz
                    clean(row[49]),  # dalas_ligumcenas_veids
                    safe_float(row[50]),  # dalas_ligumcena
                    safe_float(row[51]),  # dalas_ligumcena_no
                    safe_float(row[52]),  # dalas_ligumcena_lidz
                    clean(row[53]),  # dalas_valuta
                )
            )
            count += 1

            if len(batch) >= 2000:
                _insert_iepirkumi_batch(cursor, batch)
                batch.clear()

        if batch:
            _insert_iepirkumi_batch(cursor, batch)

        f.close()
        total += count
        print(f"    {os.path.basename(filepath)}: {count:,} rindas")

    return total


def _insert_iepirkumi_batch(cursor, batch):
    cursor.executemany(
        """
        INSERT INTO iepirkumi (
            datu_gads, iepirkuma_id, iepirkuma_nosaukums, iepirkuma_ident_nr,
            pasutitaja_org_id, citu_pasutitaju_vajadzibam, faktiskais_sanemejs,
            iepirkuma_prieksmeta_veids, cpv_kods_galvenais, cpv_kodi_papildus,
            iepirkuma_statuss, izsludinasanas_datums,
            piedav_iesniegsanas_datums, piedav_iesniegsanas_laiks,
            ieintereseto_sanaksmes, sniegsanas_vieta,
            liguma_termina_veids, liguma_termins, liguma_termina_mervieniba,
            liguma_izpilde_no, liguma_izpilde_lidz,
            ligumcenas_veids, planota_ligumcena, planota_ligumcena_no,
            planota_ligumcena_lidz, ligumcenas_valuta,
            regulejosais_tiesibu_akts, proceduras_veids,
            kontaktpersona, iesniegsanas_valoda, atsauce_es_projekti,
            pielaujami_varianti, uzvaretaja_izveles_metode, iesniegsanas_vieta,
            hipersaite_eis, hipersaite_iub,
            ir_dalijums_dalas, dalu_iesniegsanas_nosacijumi,
            dalas_nr, dalas_nosaukums, dalas_statuss,
            dalas_termina_veids, dalas_termins, dalas_termina_mervieniba,
            dalas_izpilde_no, dalas_izpilde_lidz,
            dalas_ligumcenas_veids, dalas_ligumcena, dalas_ligumcena_no,
            dalas_ligumcena_lidz, dalas_valuta
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,
        batch,
    )


def import_atversanas(cursor, orgs, raw_dir):
    """Importet EIS_E_IEPIRKUMI_ATVERSANA_*.csv -> piedavajumu_atversanas tabula."""
    files = find_csv_files(raw_dir, "EIS_E_IEPIRKUMI_ATVERSANA_*.csv")
    total = 0

    for filepath in files:
        year = extract_year_from_filename(os.path.basename(filepath))
        if year is None:
            continue

        f, reader, header = open_csv(filepath)
        batch = []
        count = 0

        for row in reader:
            if len(row) < 55:
                continue

            pas_org_id = orgs.get_or_create(
                row[5], row[4], row[6], row[8], pvs_id=row[7], is_buyer=True
            )
            pret_org_id = orgs.get_or_create(
                row[50], row[49], row[51], is_supplier=True
            )

            batch.append(
                (
                    year,
                    safe_int(row[1]),  # iepirkuma_id
                    clean(row[2]),  # nosaukums
                    clean(row[3]),  # ident_nr
                    pas_org_id,
                    clean(row[9]),  # citu_pasutitaju_vajadzibam
                    clean(row[10]),  # faktiskais_sanemejs
                    clean(row[11]),  # prieksmeta_veids
                    clean(row[12]),  # cpv_galvenais
                    clean(row[13]),  # cpv_papildus
                    clean(row[14]),  # statuss
                    clean(row[15]),  # regulejosais_tiesibu_akts
                    clean(row[16]),  # proceduras_veids
                    clean(row[17]),  # dis_piemerosana
                    clean(row[18]),  # hipersaite_eis
                    clean(row[19]),  # hipersaite_iub
                    clean(row[20]),  # sniegsanas_vieta
                    clean(row[21]),  # liguma_termina_veids
                    clean(row[22]),  # liguma_termins
                    clean(row[23]),  # liguma_termina_mervieniba
                    convert_date(row[24]),  # liguma_izpilde_no
                    convert_date(row[25]),  # liguma_izpilde_lidz
                    clean(row[26]),  # ligumcenas_veids
                    safe_float(row[27]),  # planota_ligumcena
                    safe_float(row[28]),  # planota_ligumcena_no
                    safe_float(row[29]),  # planota_ligumcena_lidz
                    clean(row[30]),  # ligumcenas_valuta
                    clean(row[31]),  # ir_dalijums_dalas
                    clean(row[32]),  # dalas_nr
                    clean(row[33]),  # dalas_nosaukums
                    clean(row[34]),  # dalas_statuss
                    clean(row[35]),  # dalas_termina_veids
                    clean(row[36]),  # dalas_termins
                    clean(row[37]),  # dalas_termina_mervieniba
                    convert_date(row[38]),  # dalas_izpilde_no
                    convert_date(row[39]),  # dalas_izpilde_lidz
                    clean(row[40]),  # dalas_ligumcenas_veids
                    safe_float(row[41]),  # dalas_ligumcena
                    safe_float(row[42]),  # dalas_ligumcena_no
                    safe_float(row[43]),  # dalas_ligumcena_lidz
                    clean(row[44]),  # dalas_valuta
                    convert_date(row[45]),  # piedav_iesniegsanas_datums
                    clean(row[46]),  # piedav_iesniegsanas_laiks
                    convert_date(row[47]),  # piedav_atversanas_datums
                    clean(row[48]),  # piedav_atversanas_laiks
                    pret_org_id,
                    clean(row[49]),  # pretendenta_nosaukums
                    clean(row[50]),  # pretendenta_reg_nr
                    clean(row[51]),  # pretendenta_reg_nr_veids
                    clean(row[52]),  # pretendenta_valsts
                    convert_date(row[53]),  # pretendenta_iesniegsanas_datums
                    clean(row[54]),  # pretendenta_iesniegsanas_laiks
                )
            )
            count += 1

            if len(batch) >= 2000:
                _insert_atversanas_batch(cursor, batch)
                batch.clear()

        if batch:
            _insert_atversanas_batch(cursor, batch)

        f.close()
        total += count
        print(f"    {os.path.basename(filepath)}: {count:,} rindas")

    return total


def _insert_atversanas_batch(cursor, batch):
    cursor.executemany(
        """
        INSERT INTO piedavajumu_atversanas (
            datu_gads, iepirkuma_id, iepirkuma_nosaukums, iepirkuma_ident_nr,
            pasutitaja_org_id, citu_pasutitaju_vajadzibam, faktiskais_sanemejs,
            iepirkuma_prieksmeta_veids, cpv_kods_galvenais, cpv_kodi_papildus,
            iepirkuma_statuss, regulejosais_tiesibu_akts, proceduras_veids,
            dis_piemerosana, hipersaite_eis, hipersaite_iub, sniegsanas_vieta,
            liguma_termina_veids, liguma_termins, liguma_termina_mervieniba,
            liguma_izpilde_no, liguma_izpilde_lidz,
            ligumcenas_veids, planota_ligumcena, planota_ligumcena_no,
            planota_ligumcena_lidz, ligumcenas_valuta,
            ir_dalijums_dalas, dalas_nr, dalas_nosaukums, dalas_statuss,
            dalas_termina_veids, dalas_termins, dalas_termina_mervieniba,
            dalas_izpilde_no, dalas_izpilde_lidz,
            dalas_ligumcenas_veids, dalas_ligumcena, dalas_ligumcena_no,
            dalas_ligumcena_lidz, dalas_valuta,
            piedav_iesniegsanas_datums, piedav_iesniegsanas_laiks,
            piedav_atversanas_datums, piedav_atversanas_laiks,
            pretendenta_org_id, pretendenta_nosaukums,
            pretendenta_reg_nr, pretendenta_reg_nr_veids,
            pretendenta_valsts,
            pretendenta_iesniegsanas_datums, pretendenta_iesniegsanas_laiks
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,
        batch,
    )


def import_grozijumi(cursor, orgs, raw_dir):
    """Importet EIS_E_IEPIRKUMI_GROZIJUMI_*.csv -> iepirkumu_grozijumi tabula."""
    files = find_csv_files(raw_dir, "EIS_E_IEPIRKUMI_GROZIJUMI_*.csv")
    total = 0

    for filepath in files:
        year = extract_year_from_filename(os.path.basename(filepath))
        if year is None:
            continue

        f, reader, header = open_csv(filepath)
        batch = []
        count = 0

        for row in reader:
            if len(row) < 21:
                continue

            pas_org_id = orgs.get_or_create(
                row[4], row[3], row[5], row[7], pvs_id=row[6], is_buyer=True
            )

            batch.append(
                (
                    year,
                    safe_int(row[0]),  # iepirkuma_id
                    clean(row[1]),  # nosaukums
                    clean(row[2]),  # ident_nr
                    pas_org_id,
                    clean(row[8]),  # statuss
                    convert_date(row[9]),  # izsludinasanas_datums
                    convert_date(row[10]),  # grozijumu_datums
                    convert_datetime(row[11]),  # piedav_iesniegsanas_datumlaiks
                    clean(row[12]),  # ieintereseto_sanaksmes
                    clean(row[13]),  # atsauce_es_projekti
                    clean(row[14]),  # hipersaite_eis
                    clean(row[15]),  # hipersaite_iub
                    clean(row[16]),  # ir_dalijums_dalas
                    clean(row[17]),  # dalu_iesniegsanas_nosacijumi
                    clean(row[18]),  # dalas_nr
                    clean(row[19]),  # dalas_nosaukums
                    clean(row[20]),  # dalas_statuss
                )
            )
            count += 1

            if len(batch) >= 2000:
                cursor.executemany(
                    """
                    INSERT INTO iepirkumu_grozijumi (
                        datu_gads, iepirkuma_id, iepirkuma_nosaukums, iepirkuma_ident_nr,
                        pasutitaja_org_id, iepirkuma_statuss,
                        izsludinasanas_datums, grozijumu_datums,
                        piedav_iesniegsanas_datumlaiks,
                        ieintereseto_sanaksmes, atsauce_es_projekti,
                        hipersaite_eis, hipersaite_iub,
                        ir_dalijums_dalas, dalu_iesniegsanas_nosacijumi,
                        dalas_nr, dalas_nosaukums, dalas_statuss
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                    batch,
                )
                batch.clear()

        if batch:
            cursor.executemany(
                """
                INSERT INTO iepirkumu_grozijumi (
                    datu_gads, iepirkuma_id, iepirkuma_nosaukums, iepirkuma_ident_nr,
                    pasutitaja_org_id, iepirkuma_statuss,
                    izsludinasanas_datums, grozijumu_datums,
                    piedav_iesniegsanas_datumlaiks,
                    ieintereseto_sanaksmes, atsauce_es_projekti,
                    hipersaite_eis, hipersaite_iub,
                    ir_dalijums_dalas, dalu_iesniegsanas_nosacijumi,
                    dalas_nr, dalas_nosaukums, dalas_statuss
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
                batch,
            )

        f.close()
        total += count
        print(f"    {os.path.basename(filepath)}: {count:,} rindas")

    return total


def import_rezultati(cursor, orgs, raw_dir):
    """Importet EIS_E_IEPIRKUMI_REZULTATI_*.csv -> iepirkumu_rezultati tabula."""
    files = find_csv_files(raw_dir, "EIS_E_IEPIRKUMI_REZULTATI_*.csv")
    total = 0

    for filepath in files:
        year = extract_year_from_filename(os.path.basename(filepath))
        if year is None:
            continue

        f, reader, header = open_csv(filepath)
        batch = []
        count = 0

        for row in reader:
            if len(row) < 36:
                continue

            pas_org_id = orgs.get_or_create(
                row[4], row[3], row[5], row[7], pvs_id=row[6], is_buyer=True
            )
            uzv_org_id = orgs.get_or_create(row[18], row[17], row[19], is_supplier=True)

            batch.append(
                (
                    year,
                    safe_int(row[0]),  # iepirkuma_id
                    clean(row[1]),  # nosaukums
                    clean(row[2]),  # ident_nr
                    pas_org_id,
                    clean(row[8]),  # statuss
                    clean(row[9]),  # regulejosais_tiesibu_akts
                    clean(row[10]),  # proceduras_veids
                    clean(row[11]),  # hipersaite_eis
                    clean(row[12]),  # hipersaite_iub
                    clean(row[13]),  # ir_dalijums_dalas
                    clean(row[14]),  # dalas_nr
                    clean(row[15]),  # dalas_nosaukums
                    clean(row[16]),  # dalas_statuss
                    uzv_org_id,
                    clean(row[17]),  # uzvaretaja_nosaukums
                    clean(row[18]),  # uzvaretaja_reg_nr
                    clean(row[19]),  # uzvaretaja_reg_nr_veids
                    clean(row[20]),  # uzvaretaja_valsts
                    clean(row[21]),  # liguma_dok_veids
                    clean(row[22]),  # liguma_dok_id
                    clean(row[23]),  # saistita_liguma_id
                    safe_float(row[24]),  # aktuala_summa
                    clean(row[25]),  # aktuala_valuta
                    safe_float(row[26]),  # sakotneja_summa
                    clean(row[27]),  # sakotneja_valuta
                    clean(row[28]),  # liguma_izpildes_termins
                    convert_date(row[29]),  # liguma_izpilde_no
                    convert_date(row[30]),  # liguma_izpilde_lidz
                    clean(row[31]),  # ligums_ir_vv
                    convert_date(row[32]),  # liguma_noslegsanas_datums
                    convert_date(row[33]),  # liguma_publicesanas_datums
                    convert_date(row[34]),  # izbeigsanas_datums
                    clean(row[35]),  # izbeigsanas_iemesls
                )
            )
            count += 1

            if len(batch) >= 2000:
                _insert_rezultati_batch(cursor, batch)
                batch.clear()

        if batch:
            _insert_rezultati_batch(cursor, batch)

        f.close()
        total += count
        print(f"    {os.path.basename(filepath)}: {count:,} rindas")

    return total


def _insert_rezultati_batch(cursor, batch):
    cursor.executemany(
        """
        INSERT INTO iepirkumu_rezultati (
            datu_gads, iepirkuma_id, iepirkuma_nosaukums, iepirkuma_ident_nr,
            pasutitaja_org_id, iepirkuma_statuss,
            regulejosais_tiesibu_akts, proceduras_veids,
            hipersaite_eis, hipersaite_iub,
            ir_dalijums_dalas, dalas_nr, dalas_nosaukums, dalas_statuss,
            uzvaretaja_org_id, uzvaretaja_nosaukums,
            uzvaretaja_reg_nr, uzvaretaja_reg_nr_veids, uzvaretaja_valsts,
            liguma_dok_veids, liguma_dok_id, saistita_liguma_id,
            aktuala_summa, aktuala_valuta, sakotneja_summa, sakotneja_valuta,
            liguma_izpildes_termins, liguma_izpilde_no, liguma_izpilde_lidz,
            ligums_ir_vv, liguma_noslegsanas_datums, liguma_publicesanas_datums,
            izbeigsanas_datums, izbeigsanas_iemesls
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,
        batch,
    )


def import_publiskas_personas(cursor, raw_dir):
    """Importet ppi_public_persons_institutions.csv -> publiskas_personas tabula."""
    filepath = os.path.join(raw_dir, "ppi_public_persons_institutions.csv")
    if not os.path.exists(filepath):
        print("  BRIDINAAJUMS: ppi_public_persons_institutions.csv nav atrasts, izlaists.")
        return 0

    f, reader, header = open_csv(filepath)
    batch = []
    count = 0

    for row in reader:
        if len(row) < 26:
            continue

        batch.append(
            (
                clean(row[0]),   # nosaukums (name)
                clean(row[1]),   # reg_nr (registrationNumber)
                clean(row[2]),   # nodoklu_maks_nr (taxpayerUnitNumber)
                clean(row[3]),   # dibinasanas_datums (establishedOn) -- jau ISO formata
                clean(row[4]),   # registracijas_datums (registeredOn)
                clean(row[5]),   # statuss (Status)
                clean(row[6]),   # statusa_detajas (statusDetails)
                clean(row[7]),   # izslegt_datums (removedOn)
                1 if row[8].strip().lower() == "t" else 0,  # neatkarigs_nodoklu_maks
                clean(row[9]),   # iestades_veids (authorityType)
                clean(row[10]),  # paklautibas_veids (subordinationType)
                clean(row[11]),  # timekla_vietne (website)
                clean(row[12]),  # epasts (email)
                clean(row[13]),  # talrunis (phone)
                clean(row[14]),  # adreses_kods (addressRegisterCode)
                clean(row[15]),  # adrese (address)
                1 if row[16].strip().lower() == "t" else 0,  # ir_augstskola
                clean(row[17]),  # augstakas_iestades_nosaukums (higherAuthorityName)
                clean(row[18]),  # augstakas_iestades_reg_nr (higherAuthorityNumber)
                clean(row[19]),  # augstakas_iestades_epasts (higherAuthorityEmail)
                clean(row[20]),  # dibinasanas_akta_nr (establishingActNumber)
                clean(row[21]),  # dibinasanas_akta_datums (establishingActDate)
                clean(row[22]),  # dibinasanas_akta_nosaukums (establishingActTitle)
                clean(row[23]),  # dibinasanas_akta_veids (establishingActType)
                clean(row[24]),  # likumdeveja_nosaukums (establishingActLegislatorName)
                clean(row[25]),  # likumdeveja_reg_nr (establishingActLegislatorNumber)
            )
        )
        count += 1

        if len(batch) >= 2000:
            cursor.executemany(
                """
                INSERT INTO publiskas_personas (
                    nosaukums, reg_nr, nodoklu_maks_nr,
                    dibinasanas_datums, registracijas_datums,
                    statuss, statusa_detajas, izslegt_datums,
                    neatkarigs_nodoklu_maks, iestades_veids, paklautibas_veids,
                    timekla_vietne, epasts, talrunis, adreses_kods, adrese,
                    ir_augstskola, augstakas_iestades_nosaukums,
                    augstakas_iestades_reg_nr, augstakas_iestades_epasts,
                    dibinasanas_akta_nr, dibinasanas_akta_datums,
                    dibinasanas_akta_nosaukums, dibinasanas_akta_veids,
                    likumdeveja_nosaukums, likumdeveja_reg_nr
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
                batch,
            )
            batch.clear()

    if batch:
        cursor.executemany(
            """
            INSERT INTO publiskas_personas (
                nosaukums, reg_nr, nodoklu_maks_nr,
                dibinasanas_datums, registracijas_datums,
                statuss, statusa_detajas, izslegt_datums,
                neatkarigs_nodoklu_maks, iestades_veids, paklautibas_veids,
                timekla_vietne, epasts, talrunis, adreses_kods, adrese,
                ir_augstskola, augstakas_iestades_nosaukums,
                augstakas_iestades_reg_nr, augstakas_iestades_epasts,
                dibinasanas_akta_nr, dibinasanas_akta_datums,
                dibinasanas_akta_nosaukums, dibinasanas_akta_veids,
                likumdeveja_nosaukums, likumdeveja_reg_nr
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
            batch,
        )

    f.close()
    return count


def import_patiesie_labuma_guveji(cursor, raw_dir):
    """Importet patiesie_labuma_guveji.csv -> patiesie_labuma_guveji tabula.

    CSV formats: komatu-atdalits ar UTF-8-sig (BOM). 11 kolonas:
      _id, id, legal_entity_registration_number, forename, surname,
      latvian_identity_number_masked, birth_date, nationality, residence,
      registered_on, last_modified_at

    Kolonu nosaukumi tiek normalizeti uz latvisku versiju (skat. shemu).
    Datumi (birth_date, registered_on) ir jau ISO formata vai ar T separatoru.
    """
    filepath = os.path.join(raw_dir, "patiesie_labuma_guveji.csv")
    if not os.path.exists(filepath):
        print("  BRIDINAAJUMS: patiesie_labuma_guveji.csv nav atrasts, izlaists.")
        return 0

    f, reader, header = open_csv(filepath)
    batch = []
    count = 0

    for row in reader:
        if len(row) < 11:
            continue

        # Datumu lauki var saturet laika dalu (piem., "2019-05-02T00:00:00")
        # Atstajam tikai datuma dalu
        birth = clean(row[6])
        if birth and "T" in birth:
            birth = birth.split("T")[0]
        reg_dat = clean(row[9])
        if reg_dat and "T" in reg_dat:
            reg_dat = reg_dat.split("T")[0]

        batch.append(
            (
                safe_int(row[1]),       # avota_id (UR sistemas 'id', ne CSV _id)
                clean(row[2]),          # tiesibu_subjekta_reg_nr
                clean(row[3]),          # vards
                clean(row[4]),          # uzvards
                clean(row[5]),          # pers_kods_maskets
                birth,                  # dzimsanas_datums
                clean(row[7]),          # valstspiederiba
                clean(row[8]),          # dzivesvietas_valsts
                reg_dat,                # reg_datums
                clean(row[10]),         # pedeja_izmainas_laiks (atstajam ar T)
            )
        )
        count += 1

        if len(batch) >= 5000:
            cursor.executemany(
                """
                INSERT INTO patiesie_labuma_guveji (
                    avota_id, tiesibu_subjekta_reg_nr,
                    vards, uzvards, pers_kods_maskets,
                    dzimsanas_datums, valstspiederiba, dzivesvietas_valsts,
                    reg_datums, pedeja_izmainas_laiks
                ) VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
                batch,
            )
            batch.clear()

    if batch:
        cursor.executemany(
            """
            INSERT INTO patiesie_labuma_guveji (
                avota_id, tiesibu_subjekta_reg_nr,
                vards, uzvards, pers_kods_maskets,
                dzimsanas_datums, valstspiederiba, dzivesvietas_valsts,
                reg_datums, pedeja_izmainas_laiks
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
        """,
            batch,
        )

    f.close()
    return count


def import_delegetas_personas(cursor, raw_dir):
    """Importet ppi_delegated_entities.csv -> delegetas_personas tabula."""
    filepath = os.path.join(raw_dir, "ppi_delegated_entities.csv")
    if not os.path.exists(filepath):
        print("  BRIDINAAJUMS: ppi_delegated_entities.csv nav atrasts, izlaists.")
        return 0

    f, reader, header = open_csv(filepath)
    batch = []
    count = 0

    for row in reader:
        if len(row) < 6:
            continue

        # Datumi var saturet laika komponentu (piem., "2018-09-13 11:28:18.124")
        # Saglabajam tikai datuma dalu
        reg_datums = clean(row[2])
        if reg_datums and " " in reg_datums:
            reg_datums = reg_datums.split(" ")[0]
        izslegt_datums = clean(row[3])
        if izslegt_datums and " " in izslegt_datums:
            izslegt_datums = izslegt_datums.split(" ")[0]

        batch.append(
            (
                clean(row[0]),   # nosaukums (delegatedEntityName)
                clean(row[1]),   # reg_nr (delegatedEntityRegistrationNumber)
                reg_datums,      # registracijas_datums (delegatedEntityRegisteredOn)
                izslegt_datums,  # izslegt_datums (delegatedEntityRemovedOn)
                clean(row[4]),   # delegetaja_nosaukums (name)
                clean(row[5]),   # delegetaja_reg_nr (registrationNumber)
            )
        )
        count += 1

        if len(batch) >= 2000:
            cursor.executemany(
                """
                INSERT INTO delegetas_personas (
                    nosaukums, reg_nr, registracijas_datums, izslegt_datums,
                    delegetaja_nosaukums, delegetaja_reg_nr
                ) VALUES (?,?,?,?,?,?)
            """,
                batch,
            )
            batch.clear()

    if batch:
        cursor.executemany(
            """
            INSERT INTO delegetas_personas (
                nosaukums, reg_nr, registracijas_datums, izslegt_datums,
                delegetaja_nosaukums, delegetaja_reg_nr
            ) VALUES (?,?,?,?,?,?)
        """,
            batch,
        )

    f.close()
    return count


# ---------------------------------------------------------------------------
# Galvenaa funkcija / Main
# ---------------------------------------------------------------------------


def main():
    raw_dir = DEFAULT_RAW_DIR
    db_path = DEFAULT_DB_PATH

    for i, arg in enumerate(sys.argv):
        if arg == "--raw-dir" and i + 1 < len(sys.argv):
            raw_dir = sys.argv[i + 1]
        elif arg == "--db" and i + 1 < len(sys.argv):
            db_path = sys.argv[i + 1]

    # Dzest esoso DB ja eksiste
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Dzesta iespreekseja datubaze: {db_path}")

    print(f"EIS SQLite datubaazes izveide")
    print(f"Avota mape:  {raw_dir}")
    print(f"Datubaze:    {db_path}")
    print("=" * 60)

    t0 = time.time()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Sheemas izveide
    print("\n[1/11] Sheemas izveide...")
    cursor.executescript(SCHEMA_SQL)
    conn.commit()

    orgs = OrgCache(cursor)
    cats = CatalogCache(cursor)

    # 2. Pasutitaji
    print("\n[2/11] Pasutitaju imports (PASUTITAJI_KLAS.csv)...")
    n = import_pasutitaji(cursor, orgs, raw_dir)
    conn.commit()
    print(f"  => {n:,} organizacijas")

    # 3. E-pasutijumi
    print("\n[3/11] E-pasutijumu imports (EIS_E_PASUT_APST_*.csv)...")
    n = import_e_pasutijumi(cursor, orgs, cats, raw_dir)
    conn.commit()
    print(f"  => {n:,} rindas kopa")

    # 4. Piegades
    print("\n[4/11] Piegazu imports (EIS_E_PASUT_*.csv)...")
    n = import_piegades(cursor, orgs, cats, raw_dir)
    conn.commit()
    print(f"  => {n:,} rindas kopa")

    # 5. Iepirkumi
    print("\n[5/11] Iepirkumu imports (EIS_E_IEPIRKUMI_IZSLUDINATIE_*.csv)...")
    n = import_iepirkumi(cursor, orgs, raw_dir)
    conn.commit()
    print(f"  => {n:,} rindas kopa")

    # 6. Atversanas
    print("\n[6/11] Piedavajumu atversanu imports (EIS_E_IEPIRKUMI_ATVERSANA_*.csv)...")
    n = import_atversanas(cursor, orgs, raw_dir)
    conn.commit()
    print(f"  => {n:,} rindas kopa")

    # 7. Grozijumi
    print("\n[7/11] Iepirkumu grozijumu imports (EIS_E_IEPIRKUMI_GROZIJUMI_*.csv)...")
    n = import_grozijumi(cursor, orgs, raw_dir)
    conn.commit()
    print(f"  => {n:,} rindas kopa")

    # 8. Rezultati
    print("\n[8/11] Iepirkumu rezultatu imports (EIS_E_IEPIRKUMI_REZULTATI_*.csv)...")
    n = import_rezultati(cursor, orgs, raw_dir)
    conn.commit()
    print(f"  => {n:,} rindas kopa")

    # 9. Publiskas personas
    print("\n[9/11] Publisko personu imports (ppi_public_persons_institutions.csv)...")
    n = import_publiskas_personas(cursor, raw_dir)
    conn.commit()
    print(f"  => {n:,} rindas")

    # 10. Delegetas personas
    print("\n[10/11] Delegeto personu imports (ppi_delegated_entities.csv)...")
    n = import_delegetas_personas(cursor, raw_dir)
    conn.commit()
    print(f"  => {n:,} rindas")

    # 11. Patiesie labuma guveji (PLG)
    print("\n[11/11] PLG imports (patiesie_labuma_guveji.csv)...")
    n = import_patiesie_labuma_guveji(cursor, raw_dir)
    conn.commit()
    print(f"  => {n:,} rindas")

    # Indeksu izveide
    print("\nIndeksu izveide...")
    t_idx = time.time()
    cursor.executescript(INDEX_SQL)
    conn.commit()
    print(f"  Indeksi izveidoti {time.time() - t_idx:.1f}s")

    # Kopsavilkums
    print("\n" + "=" * 60)
    print("KOPSAVILKUMS")
    print("=" * 60)

    tables = [
        "organizacijas",
        "katalogi",
        "e_pasutijumi",
        "piegades",
        "iepirkumi",
        "piedavajumu_atversanas",
        "iepirkumu_grozijumi",
        "iepirkumu_rezultati",
        "publiskas_personas",
        "delegetas_personas",
        "patiesie_labuma_guveji",
    ]
    total_rows = 0
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = cursor.fetchone()[0]
        total_rows += cnt
        print(f"  {t:30s} {cnt:>12,} rindas")

    print(f"  {'KOPA':30s} {total_rows:>12,} rindas")

    conn.execute("PRAGMA optimize")
    conn.close()

    db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
    elapsed = time.time() - t0
    print(f"\nDatubaze: {db_path}")
    print(f"Izmers:   {db_size_mb:.1f} MB")
    print(f"Laiks:    {elapsed:.1f}s")


if __name__ == "__main__":
    main()
