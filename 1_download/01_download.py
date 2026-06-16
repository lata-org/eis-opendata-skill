"""
EIS atvertu datu lejupielade / EIS Open Data Download
=====================================================
Lejupielade visas 9 datu kopas no data.gov.lv:
  1. Pirkuma pasutijumi (EIS_E_PASUT_APST) -- 2010-2026
  2. Piedavajumu atversanas (EIS_E_IEPIRKUMI_ATVERSANA) -- 2016-2026
  3. Iepirkumu grozijumi (EIS_E_IEPIRKUMI_GROZIJUMI) -- 2016-2026
  4. Pasutitaju klasifikators (PASUTITAJI_KLAS) -- 1 fails
  5. Izsludinatie iepirkumi (EIS_E_IEPIRKUMI_IZSLUDINATIE) -- 2016-2026
  6. Iepirkumu rezultati (EIS_E_IEPIRKUMI_REZULTATI) -- 2018-2026
  7. Piegazu dati (EIS_E_PASUT) -- 2010-2026
  8. Publiskas personas un iestades (PPI) -- 2 faili
  9. Patiesie labuma guveji (PLG) -- 1 fails (UR)

Lietojums / Usage:
  python 01_download.py              # Lejupielade tikai jaunus/mainitus failus
  python 01_download.py --force      # Parraksta visus failus
  python 01_download.py --output-dir ./my-data  # Cita izvades mape
  python 01_download.py --from-year 2022        # Tikai 2022+ gada faili (PPI, PLG un PASUTITAJI_KLAS vienmer)
  python 01_download.py --only-years 2019,2020  # Tikai konkretie gadi (PPI, PLG un PASUTITAJI_KLAS vienmer)
"""

import os
import re
import sys
import urllib.request
import urllib.error
import time
import hashlib

# ---------------------------------------------------------------------------
# Konfiguracija / Configuration
# ---------------------------------------------------------------------------

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw-data")

BASE = "https://data.gov.lv/dati/dataset"

# Datu kopu resursu ID kartejumi / Dataset resource ID mappings
# Katrs ieraksts: (faila_nosaukums, pilns_URL)

DATASETS = []

# 1. Pirkuma pasutijumi -- EIS_E_PASUT_APST_YYYY.csv
_PASUT_APST_DS = "693c289a-f2c4-4911-bc32-69fd17dbf700"
_PASUT_APST_RES = {
    2010: "a8f9c39c-5a68-4848-a6c6-57625f205c45",
    2011: "8f3d230c-1bc7-40fa-b786-8b5ac89b8496",
    2012: "2ef44ded-5080-4c93-90af-a9e605c470c4",
    2013: "c3d54b54-a2b4-4535-ac6a-40f264568648",
    2014: "9031948a-c906-4614-8274-6a62de1eeaf4",
    2015: "572a1153-371c-4a86-9cbe-a07b4a5a977a",
    2016: "4a32f248-feb9-4f54-9243-d4d98ea9d024",
    2017: "f50ac697-a3a1-453b-9fd0-c3ca16656092",
    2018: "e3be0379-c7bf-4439-9443-ffc9881f79af",
    2019: "227567af-fd4b-49df-8054-dba08676254e",
    2020: "d31fbf99-2708-4558-9c83-d16e69a70e08",
    2021: "bf623b89-ce86-4fc6-a2af-46c2c993074c",
    2022: "bad87d10-ef05-43fb-b9ba-9f0e7a761673",
    2023: "d89f4745-77b0-47e4-9e8b-ec494dc3ad1b",
    2024: "11f08c38-50f7-47f3-a700-4f60cd09d943",
    2025: "226db975-8dc7-4f59-9f92-773ef9b58739",
    2026: "a63a9503-d7f1-4840-8e53-0346ed0513a9",
}
for year, res_id in _PASUT_APST_RES.items():
    DATASETS.append((
        f"EIS_E_PASUT_APST_{year}.csv",
        f"{BASE}/{_PASUT_APST_DS}/resource/{res_id}/download/eis_e_pasut_apst_{year}.csv"
    ))

# 2. Piedavajumu atversanas -- EIS_E_IEPIRKUMI_ATVERSANA_YYYY.csv
_ATVERSANA_DS = "7cfac5a8-8e54-4151-b263-4ca9e51065e9"
_ATVERSANA_RES = {
    2016: "8e77cc9e-554e-4bfb-8772-9dc0b7d24608",
    2017: "7733be61-bca2-4ae8-8577-d948058df6c0",
    2018: "e40819ee-3a84-4205-b64e-4c67263ac237",
    2019: "7f23e4c6-9bee-4552-ba0c-a05be1f6ac62",
    2020: "eb1ddcf9-e358-4ceb-a4d7-e406a0a60d7e",
    2021: "25883190-97ef-45a1-9b89-d15cc418a644",
    2022: "4b9317d7-8495-4621-966d-48e00639e2cb",
    2023: "7f4f7e75-8207-4ab1-9470-bcd0112653e9",
    2024: "0bba780e-5ae3-4701-ab16-8f804d5a3e57",
    2025: "4540cc38-0f5f-42a9-9749-3896c3da4488",
    2026: "a45acd54-2e8f-4fb5-b757-31654e875563",
}
for year, res_id in _ATVERSANA_RES.items():
    DATASETS.append((
        f"EIS_E_IEPIRKUMI_ATVERSANA_{year}.csv",
        f"{BASE}/{_ATVERSANA_DS}/resource/{res_id}/download/eis_e_iepirkumi_atversana_{year}.csv"
    ))

# 3. Iepirkumu grozijumi -- EIS_E_IEPIRKUMI_GROZIJUMI_YYYY.csv
_GROZIJUMI_DS = "5f8373da-714d-4202-beed-b473eb564a6d"
_GROZIJUMI_RES = {
    2016: "792209b1-1465-41f9-b6e7-93878722c249",
    2017: "92e512ed-013b-4757-ba19-56662630f6e6",
    2018: "a1e67b0e-704a-4ca1-96dc-39c87d35c04e",
    2019: "d5e7494f-6f7f-42a9-9683-3c855f3d00a1",
    2020: "3438f0eb-d7d2-4d0c-a1f2-e1d2420c848f",
    2021: "ec6da601-c7f6-466e-9bcb-4efea45dab36",
    2022: "4ad302df-c832-48e5-bd67-89d470ae43b3",
    2023: "25b0c081-49d9-4bea-9e5f-ecac3573d6cb",
    2024: "f8e2e074-e29e-409f-8fec-5d22c7b0bcd1",
    2025: "f7b96bf6-2af8-446a-a6ee-6022601fef7c",
    2026: "d9e4d487-1f1a-4b37-9735-e411708d7288",
}
for year, res_id in _GROZIJUMI_RES.items():
    DATASETS.append((
        f"EIS_E_IEPIRKUMI_GROZIJUMI_{year}.csv",
        f"{BASE}/{_GROZIJUMI_DS}/resource/{res_id}/download/eis_e_iepirkumi_grozijumi_{year}.csv"
    ))

# 4. Pasutitaju klasifikators -- PASUTITAJI_KLAS.csv
_PASUTITAJI_DS = "841ab05a-5a19-4757-9b76-d383359619c5"
_PASUTITAJI_RES = "08a09865-b831-462a-a5ce-226f9293ff3e"
DATASETS.append((
    "PASUTITAJI_KLAS.csv",
    f"{BASE}/{_PASUTITAJI_DS}/resource/{_PASUTITAJI_RES}/download/pasutitaji_klas.csv"
))

# 5. Izsludinatie iepirkumi -- EIS_E_IEPIRKUMI_IZSLUDINATIE_YYYY.csv
_IZSLUDINATIE_DS = "f78dd9df-25fb-4e3e-8247-1db02684819a"
_IZSLUDINATIE_RES = {
    2016: "d3f8737c-8395-4fab-8ef1-8f05a359b612",
    2017: "1325a615-0bdf-4333-8e91-30f209892f61",
    2018: "51dcbd26-379e-4c62-b51a-e8a230881773",
    2019: "f381ac66-f96c-41a6-a51d-fc5898ebcb06",
    2020: "e6038531-e12d-4bc7-8357-89e37d7de476",
    2021: "6bd2e287-c494-4ddc-9525-802d88872edc",
    2022: "0c4d15c4-cf59-4239-ba76-de4bbf48d824",
    2023: "b8927a5d-1274-4262-bccc-16d21abcf4a3",
    2024: "d7204b7f-0767-472e-b1c7-b85816992885",
    2025: "42739f4f-d625-46a7-9668-ef2e0376e421",
    2026: "f2a08974-d59a-4d83-92f2-4194cb2bd97d",
}
for year, res_id in _IZSLUDINATIE_RES.items():
    DATASETS.append((
        f"EIS_E_IEPIRKUMI_IZSLUDINATIE_{year}.csv",
        f"{BASE}/{_IZSLUDINATIE_DS}/resource/{res_id}/download/eis_e_iepirkumi_izsludinatie_{year}.csv"
    ))

# 6. Iepirkumu rezultati -- EIS_E_IEPIRKUMI_REZULTATI_YYYY.csv
_REZULTATI_DS = "e909312a-61c9-4cde-a72a-0a09dd75ef43"
_REZULTATI_RES = {
    2018: "cecd0be7-c8e0-451a-8314-f1d806db3bc1",
    2019: "1d37ba16-4d7b-4c1e-9650-1ee9b6a32666",
    2020: "abf811a3-26e8-48c2-bc86-e9b74ca0b385",
    2021: "a1342945-ce4b-480b-abb5-b74d43c41534",
    2022: "97a7c410-60c0-4d08-b554-4d1abb9092da",
    2023: "71f88053-97c1-4928-93c3-8d83d714f27f",
    2024: "3a02a1a7-0322-4c0d-9700-8af9832f0f91",
    2025: "79b34e1c-8989-4984-816a-8e8f92b701f3",
    2026: "c4007411-1ba5-40f3-9b50-f25881c93f51",
}
for year, res_id in _REZULTATI_RES.items():
    DATASETS.append((
        f"EIS_E_IEPIRKUMI_REZULTATI_{year}.csv",
        f"{BASE}/{_REZULTATI_DS}/resource/{res_id}/download/eis_e_iepirkumi_rezultati_{year}.csv"
    ))

# 7. Piegazu dati -- EIS_E_PASUT_YYYY.csv
_PIEGAZU_DS = "a56ad23d-c8d5-43f4-8b51-7bb534c39051"
_PIEGAZU_RES = {
    2010: "cd17b62c-b7e5-416e-adcc-707e2b109a6f",
    2011: "bb62ce35-46eb-49ed-8e95-474d0918dd65",
    2012: "1c638795-cb24-4b57-a11a-124e48b274c0",
    2013: "cba668cc-2535-458a-ac21-9022f0ded50f",
    2014: "cdd75d59-407b-4e7e-b4a2-834db2ee00f8",
    2015: "cd1bd12c-7e52-40ee-b65b-66364a0c9120",
    2016: "dc0f81fd-c48c-4740-b479-07b1218e7ef2",
    2017: "78ca35ae-8ce7-4593-97ac-faf8348a18af",
    2018: "7d152654-74c8-45af-a024-fdbd002fa706",
    2019: "addf3381-f57e-40a7-82e7-e228fb121367",
    2020: "fe5a1ee0-c228-46d8-9d2f-022d9aee1ae9",
    2021: "ead3e185-b006-45f5-ace9-4fb2fc3c15ad",
    2022: "99565544-1fd2-441d-b408-df33066a3867",
    2023: "b7cc1f82-10c7-45f1-ad22-d3339bf990ee",
    2024: "041097af-09c4-4ce6-b427-ad6921456c71",
    2025: "91f940ab-9132-40c0-aa8b-433ced22c17d",
    2026: "c6aed1c6-94bc-4c83-936f-3c37648aca4b",
}
for year, res_id in _PIEGAZU_RES.items():
    DATASETS.append((
        f"EIS_E_PASUT_{year}.csv",
        f"{BASE}/{_PIEGAZU_DS}/resource/{res_id}/download/eis_e_pasut_{year}.csv"
    ))

# 8. Publiskas personas un iestades (PPI) -- 2 faili
_PPI_DS = "2e4926ea-8648-44e6-9227-3cb20604ec31"
_PPI_INSTITUTIONS_RES = "190ba502-08d1-4c4c-b1b9-b58299bf9a9f"
_PPI_DELEGATED_RES = "090df3ca-0873-42d8-b375-1a2454700a13"
DATASETS.append((
    "ppi_public_persons_institutions.csv",
    f"{BASE}/{_PPI_DS}/resource/{_PPI_INSTITUTIONS_RES}/download/ppi_public_persons_institutions.csv"
))
DATASETS.append((
    "ppi_delegated_entities.csv",
    f"{BASE}/{_PPI_DS}/resource/{_PPI_DELEGATED_RES}/download/ppi_delegated_entities.csv"
))

# 9. Patiesie labuma guveji (PLG) -- LR Uznemumu registrs
# Datu kopa: https://data.gov.lv/dati/lv/dataset/patiesie-labuma-guveji
# Saturs: zinas par tiesibu subjektu aktualiem patiesajiem labuma guvejiem (fiziskam personam)
# Atjaunina katru dienu. Licence: CC0-1.0. Publicetajs: LR Uznemumu registrs.
# URL formats atskiras no EIS: datastore/dump endpoint ar BOM (UTF-8-sig)
_PLG_RES = "20a9b26d-d056-4dbb-ae18-9ff23c87bdee"
DATASETS.append((
    "patiesie_labuma_guveji.csv",
    f"https://data.gov.lv/dati/lv/datastore/dump/{_PLG_RES}?bom=True"
))


# ---------------------------------------------------------------------------
# Lejupielades logika / Download logic
# ---------------------------------------------------------------------------

def file_md5(path):
    """Aprekinat faila MD5 hash."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def download_file(url, dest_path, force=False):
    """
    Lejupielade vienu failu. Atgriez True ja fails tika lejupieladets/atjaunots.
    Ja force=False, izlaidz ja fails jau eksiste un izmers nav 0.
    """
    if not force and os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return False

    tmp_path = dest_path + ".tmp"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "EIS-data-downloader/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp, open(tmp_path, "wb") as out:
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                out.write(chunk)

        # Parbaude vai lejupieladetas fails nav tusss
        if os.path.getsize(tmp_path) == 0:
            os.remove(tmp_path)
            print(f"  BRIDINAAJUMS: Tusss fails, izlaists: {os.path.basename(dest_path)}")
            return False

        # Parbaude vai saturs ir mainijies (ja vecais fails eksiste)
        if os.path.exists(dest_path):
            old_hash = file_md5(dest_path)
            new_hash = file_md5(tmp_path)
            if old_hash == new_hash:
                os.remove(tmp_path)
                return False

        # Parvieto tmp -> galigo vietu
        if os.path.exists(dest_path):
            os.remove(dest_path)
        os.rename(tmp_path, dest_path)
        return True

    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        print(f"  KLUUDA: {e}")
        return False


def main():
    force = "--force" in sys.argv

    # Atrodam output direktoriju
    output_dir = OUTPUT_DIR
    from_year = None
    only_years = None
    for i, arg in enumerate(sys.argv):
        if arg == "--output-dir" and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
        if arg == "--from-year" and i + 1 < len(sys.argv):
            from_year = int(sys.argv[i + 1])
        if arg == "--only-years" and i + 1 < len(sys.argv):
            only_years = {int(y) for y in sys.argv[i + 1].split(",")}

    # Filtrejam DATASETS pec gada (faili bez gada, piem., PASUTITAJI_KLAS un PPI, paliek)
    datasets = DATASETS
    if only_years is not None:
        filtered = []
        for fname, url in DATASETS:
            m = re.search(r"_(\d{4})\.csv$", fname)
            if m:
                if int(m.group(1)) in only_years:
                    filtered.append((fname, url))
            else:
                filtered.append((fname, url))
        datasets = filtered
    elif from_year is not None:
        filtered = []
        for fname, url in DATASETS:
            m = re.search(r"_(\d{4})\.csv$", fname)
            if m:
                if int(m.group(1)) >= from_year:
                    filtered.append((fname, url))
            else:
                filtered.append((fname, url))
        datasets = filtered

    os.makedirs(output_dir, exist_ok=True)

    print(f"EIS atvertu datu lejupielade")
    print(f"Izvades mape: {output_dir}")
    print(f"Kopaa failu: {len(datasets)}" + (f" (filtrs: from-year={from_year})" if from_year else ""))
    print(f"Rezims: {'FORCE (parraksta visus)' if force else 'INKREMENTALS (tikai jaunus)'}")
    print("-" * 60)

    downloaded = 0
    skipped = 0
    errors = 0
    t0 = time.time()

    for i, (filename, url) in enumerate(datasets, 1):
        dest = os.path.join(output_dir, filename)
        existed = os.path.exists(dest) and os.path.getsize(dest) > 0

        sys.stdout.write(f"[{i:3d}/{len(datasets)}] {filename} ... ")
        sys.stdout.flush()

        try:
            result = download_file(url, dest, force=force)
            if result:
                size_mb = os.path.getsize(dest) / (1024 * 1024)
                print(f"OK ({size_mb:.1f} MB)" + (" [ATJAUNOTS]" if existed else " [JAUNS]"))
                downloaded += 1
            else:
                if os.path.exists(dest) and os.path.getsize(dest) > 0:
                    print("izlaists (nemainits)")
                    skipped += 1
                else:
                    print("KLUUDA")
                    errors += 1
        except Exception as e:
            print(f"KLUUDA: {e}")
            errors += 1

    elapsed = time.time() - t0
    print("-" * 60)
    print(f"Pabeigts {elapsed:.1f}s laika.")
    print(f"  Lejupieladeti/atjaunoti: {downloaded}")
    print(f"  Izlaisti (nemainiti):     {skipped}")
    print(f"  Kludas:                   {errors}")

    # Kopsavilkums par failu apjomu
    total_size = 0
    for filename, _ in datasets:
        p = os.path.join(output_dir, filename)
        if os.path.exists(p):
            total_size += os.path.getsize(p)
    print(f"  Kopejais apjoms:          {total_size / (1024**3):.2f} GB")

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
