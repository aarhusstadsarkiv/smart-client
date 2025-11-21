import os
import csv
import sys
import locale
import hashlib
import json
import urllib.parse
import uuid
from http.client import HTTPException
from pathlib import Path
from typing import Any, Optional
from xml.dom.minidom import parseString

import httpx
import dicttoxml
from gooey import Gooey, GooeyParser

import config as config


ADDITIONAL_FIELDS: list = ["navn", "email", "telefon"]

ARKIBAS_JOURNAL_COLS: list = [
    "JournalAar",
    "JournalNr",
    "ModtagetAf",
    "ModtagetDato",
    "Aftale",
    "Klausul",
    "Klausulbeskrivelse",
    "Bemærkning",
    "Stikord",
    "Giver1Navn",
    "Giver1Adresse",
    "Giver1Postnummer",
    "Giver1By",
    "Giver1Telefon",
    "Giver1Email",
    "Giver1Bemærkninger",
]

ARKIBAS_CONTENT_COLS: list = [
    "Journalnummer",
    "Indhold",
    "Råderet",
    "Mængde",
    "Placering",
    "Note",
    "Filnavn",
]


def generate_arkibas_csvs(dir_path: Path, submission: dict) -> None:
    journal_path: Path = dir_path / "journal.csv"
    content_path: Path = dir_path / "indhold.csv"

    if journal_path.exists():
        print(
            "ADVARSEL. En metadatafil fra samme uuid"
            " ligger allerede i mappen. Overskriver ikke.",
            flush=True,
        )
        return

    if content_path.exists():
        print(
            "ADVARSEL. En metadatafil fra samme uuid"
            " ligger allerede i mappen. Overskriver ikke.",
            flush=True,
        )
        return

    with open(journal_path, "w", encoding="utf-8", newline="") as j:
        journal = csv.DictWriter(j, fieldnames=ARKIBAS_JOURNAL_COLS)
        journal.writeheader()
        journal.writerow(
            {
                "Giver1Navn": submission.get("navn"),
                "Giver1Telefon": submission.get("telefon"),
                "Giver1Email": submission.get("email"),
            }
        )

    with open(content_path, "w", encoding="utf-8", newline="") as i:
        journal = csv.DictWriter(i, fieldnames=ARKIBAS_CONTENT_COLS)
        journal.writeheader()
        for file in submission.get("files", []):
            journal.writerow(
                {
                    "Indhold": submission.get("description"),
                    "Mængde": len(submission["files"]),
                    "Placering": submission.get("location"),
                    "Filnavn": file.get("filename"),
                }
            )


def default_value(field: str, value: Optional[str]) -> int:
    if field == "format":
        if value:
            if value == "json":
                return 0
            elif value == "xml":
                return 1
            elif value == "arkibas":
                return 2
    return 0


def setup_parser(cli: GooeyParser) -> Any:
    cli.add_argument(
        "uuid",
        metavar="UUID",
        help=("Unik id for afleveringen. Eks.: dbd9bcb8-8110-4a10-9fe7-d12d9ca9f09d"),
        gooey_options={"full_width": True},
    )
    cli.add_argument(
        "destination",
        metavar="Destination",
        help=(
            "Sti til rodmappen, hvor afleveringen skal gemmes.\n\n"
            "Hver aflevering, inkl. filer, bliver placeret i en undermappe til rodmappen,"
            " navngivet efter afleveringens UUID. Allerede eksisterende filer og/eller "
            "afleveringsformular bliver ikke overskrevet.\n"
        ),
        widget="DirChooser",
        type=Path,
        default=os.getenv("DEFAULT_DESTINATION")
        or str(Path(Path.home(), "Downloads", "Smartarkivering")),
        gooey_options={
            "default_path": os.getenv("DEFAULT_DESTINATION")
            or str(Path(Path.home(), "Downloads", "Smartarkivering")),
            "full_width": True,
        },
    )
    format_chooser = cli.add_mutually_exclusive_group(
        required=True,
        gooey_options={
            "title": "Metadata format",
            "show_border": True,
            "initial_selection": default_value("format", os.getenv("DEFAULT_FORMAT")),
        },
    )
    format_chooser.add_argument(
        "--json",
        dest="json",
        action="store_true",
        help="Gem metadata i json-fil",
        gooey_options={"full_width": False},
    )
    format_chooser.add_argument(
        "--xml",
        dest="xml",
        action="store_true",
        help="Gem metadata i xml-fil",
        gooey_options={"full_width": False},
    )
    format_chooser.add_argument(
        "--arkibas",
        dest="arkibas",
        action="store_true",
        help="Gem metadata i arkibas csv-format",
        gooey_options={"full_width": False},
    )

    hash_chooser = cli.add_mutually_exclusive_group(
        required=True,
        gooey_options={
            "title": "Checksum",
            "show_border": True,
            "initial_selection": 0 if os.getenv("DEFAULT_HASH") == "md5" else 1,
        },
    )
    hash_chooser.add_argument(
        "--md5",
        dest="md5",
        action="store_true",
        help="Generate MD5 checksum of downloaded files",
        gooey_options={"full_width": False},
    )
    hash_chooser.add_argument(
        "--sha256",
        dest="sha256",
        action="store_true",
        help="Generate SHA256 checksum of downloaded files",
        gooey_options={"full_width": False},
    )

    args = cli.parse_args()
    return args


def get_submission_info(uuid: str) -> dict:
    """Fetch and save submission-data

    Given a uuid and an out_dir, it tries to fetch and return the submission-data from
    the API.

    Args:
        uuid (UUID): uuid of the submission. Copy from the mail-notification
        out_dir (Path): full path to the folder where the submission.json is
            to be saved. Usually the folder is named after the uuid.

    Returns:
        A dict-representation of the submission-data returned by the api-endpoint. Currently
            https://selvbetjening.aarhuskommune.dk/da/webform_rest/smartarkivering_test/submission/{submission_id}

    Raises:
        HTTPException: All non-200 status_codes are raised
    """

    with httpx.Client() as client:
        print(f"Henter afleveringsformular med uuid: {uuid}", flush=True)
        r = client.get(
            f"{os.getenv('SUBMISSION_URL')}/{uuid}?api-key={os.getenv('API_KEY')}"
        )
        if r.status_code == 404:
            raise HTTPException(
                f"FEJl. Der findes ingen aflevering med dette uuid: {uuid}"
            )
        elif r.status_code in [401, 403]:
            raise HTTPException(
                f"FEJl. Adgang nægtet med den brugte API-nøgle til: {r.url}"
            )
        elif r.status_code != 200:
            raise HTTPException(
                f"FEJl. Kunne ikke hente en aflevering med dette uuid: {uuid}. Status_code: {r.status_code}, fejlbesked: {r.text}"
            )

        submission: dict = r.json()
        return submission


def extract_filelist(submission: dict) -> list[dict]:
    """Extract and enhance 'files'-data from the submission"""

    files: list[dict] = []
    try:
        files_dict: dict = submission["data"]["linked"]["files"]
    except Exception:
    # if not files_dict:
        raise ValueError("FEJL. Afleveringen indeholder ingen filer.")

    for k, v in files_dict.items():
        v["filename"] = urllib.parse.unquote(Path(v.get("url")).name, encoding="utf-8")  # type: ignore
        files.append(v)

    return files


def generate_submission_info(submission: dict, files: list[dict]) -> dict:
    out: dict = {}
    prefix: str = os.getenv("ARCHIVE_PREFIX", "").lower()
    for k, v in submission["data"].items():
        if not v:
            continue
        if k.startswith(prefix):
            out[k[4:]] = v
        elif k in ADDITIONAL_FIELDS:
            out[k] = v

    out["files"] = files
    # out["completed"] = submission.get("completed")
    return out


def save_submission_info(submission: dict, format: str, out_dir: Path) -> None:
    # Calculate filename
    if format == "arkibas":
        generate_arkibas_csvs(out_dir, submission)
        return

    filepath = Path(out_dir, f"submission.{format}")
    # Test if filename already exists
    if filepath.exists():
        print(
            "ADVARSEL. En metadatafil fra samme uuid"
            " ligger allerede i mappen. Overskriver ikke.",
            flush=True,
        )
        return

    with open(filepath, "w", encoding="utf-8") as f:
        if format == "json":
            json.dump(submission, f, ensure_ascii=False, indent=4)
        elif format == "xml":
            xml = dicttoxml.dicttoxml(
                submission,
                custom_root="submission",
                attr_type=False,
                item_func=lambda _: "file",
            )
            f.write(parseString(xml).toprettyxml())


def download_files(files: list[dict], out_dir: Path) -> dict:
    """Download all form-files

    Given a filelist (extracted from the submission) and an out_dir, it
    tries to download all files attached to the submitted form to the out_dir.

    Args:
        submission (dict): The submission-data returned by the API in a previous step.
        out_dir (Path): full path to the folder where the files are saved.

    Raises:
        HTTPException: All non-200 status_codes are raised
    
    Returns:
        dict of filename:status. Status can be [missing, existing, downloaded, error]
    """

    out: dict = {
        "errors": [],
        "downloaded": [],
        "existing": [],
        "missing": []
    }

    with httpx.Client() as client:
        files_len: int = len(files)
        print(f"Henter {files_len} fil(er):", flush=True)
        for idx, d in enumerate(files, start=1):
            filename = d["filename"]  # type: ignore
            filepath = Path(out_dir, filename)
            if filepath.exists():
                print(
                    f"ADVARSEL. Denne fil ligger allerede i afleveringsmappen: {filename}",
                    flush=True,
                )
                out["existing"].append(filename)
                continue

            print(
                f"{idx} af {files_len}: {filename} ({d.get('size')} bytes)...",
                flush=True,
            )

            r = client.get(d["url"], params={"api-key": os.getenv("API_KEY")})
            if r.status_code == 404:
                print(
                    f"FEJl. Afleveringen har ikke nogen vedhæftet fil med dette navn: {filename}",
                    flush=True,
                )
                out["missing"].append(filename)
                continue

            elif r.status_code in [401, 403]:
                print(f"FEJl. Adgang nægtet med den brugte API-nøgle til: {r.url}", flush=True)
                print("Denne fejl vil gentage sig for de resterende downloads, så jobbet afsluttes her.", flush=True)
                print("Prøv igen senere eller kontakt stadsarkiv@aarhus.dk", flush=True)
                sys.exit(1)

            elif str(r.status_code).startswith("5"):
                print(
                    "FEJl. Serveren har problemer. Prøv igen senere eller anmeld fejlen til stadsarkiv@aarhus.dk",
                    flush=True
                )
                sys.exit(1)

            try:
                with open(filepath, "wb") as download:
                    download.write(r.content)
                    out["downloaded"].append(filename)
            except Exception as e:
                print(
                    f"FEJl. Der Kunne ikke hentes en fil på serveren med dette navn: {filename}. Status_code: {r.status_code} Fejl: {e}"
                )
                out["errors"].append(filename)

    return out


def update_fileinfo(files: list[dict], out_dir: Path, algoritm: str) -> list[dict]:
    """Adds checksum to and removes unnecessary metadata from each file"""
    IGNORE_KEYS = ["url", "id"]

    def compute_hash(filepath: Path) -> str:
        hash = hashlib.md5() if algoritm == "md5" else hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash.update(chunk)
        return hash.hexdigest()

    out: list[dict] = []
    for file in files:
        path = out_dir / file["filename"]
        file["checksum"] = f"{algoritm}:{compute_hash(path)}"
        new_file = {k: v for k, v in file.items() if k not in IGNORE_KEYS}
        out.append(new_file)
    return out


@Gooey(
    program_name="Smartarkivering, version 0.2.4",
    # program_name="Smartarkivering",
    program_description="Klient til at hente afleveringer og filer fra smartarkivering.dk",
    default_size=(600, 700),
    # https://github.com/chriskiehl/Gooey/issues/520#issuecomment-576155188
    # necessary for pyinstaller to work in --windowed mode (no console)
    encoding=locale.getpreferredencoding(),
    show_restart_button=False,
    show_failure_modal=False,
    show_success_modal=False,
)
def main() -> None:
    # Setup parser
    cli: GooeyParser = GooeyParser(description="Smartarkivering")
    args = setup_parser(cli)

    # Load config or print error in gooey-field and exit
    try:
        config.load_configuration()
    except FileNotFoundError:
        sys.exit(f"FEJL. Konfigurationsfilen findes ikke her:\n {Path.home() / '.smartarkivering' / 'config.json'}")
    except ValueError:
        sys.exit("FEJL. Konfigurationsfilen kan ikke parses som valid json")

    # Validate arguments
    fmt: str = ""
    if args.json:
        fmt = "json"
    elif args.xml:
        fmt = "xml"
    elif args.arkibas:
        fmt = "arkibas"
    else:
        sys.exit("FEJL. Ikke-valid format: Vælg mellem 'json', 'xml' eller 'arkibas'")

    try:
        uuid.UUID(args.uuid)
    except ValueError:
        sys.exit("FEJL. Det indtastede uuid har ikke det korrekte format.")

    if not Path(args.destination).is_dir():
        sys.exit("FEJL. Destinationen skal være en eksisterende mappe.")

    out_dir = Path(args.destination, args.uuid)
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        sys.exit(f"FEJl. Kan ikke oprette destinationsmappen: {e}")


    # Fetch submission info
    try:
        # get_submission_info prints any errors with http or json-parsing
        submission: dict = get_submission_info(args.uuid)
    except HTTPException as e:
        sys.exit(e.args[0])

    # extract info on uploaded files
    try:
        fileinfo: list[dict] = extract_filelist(submission)
    except ValueError as e:
        sys.exit(e)

    # download attached files
    file_status: list[dict] = []
    try:
        file_status = download_files(fileinfo, out_dir)
    except Exception as e:
        sys.exit(e.args[0])

    # update fileinfo
    hash = "md5" if args.md5 else "sha256"
    updated_fileinfo = update_fileinfo(fileinfo, out_dir, hash)

    # put together new submission-data
    submission = generate_submission_info(submission, updated_fileinfo)

    # save submission data to file
    save_submission_info(submission, format=fmt, out_dir=out_dir)

    print("Færdig med at hente filer og metadata for afleveringen.\n", flush=True)

    for k, v in file_status.items():
        if k == "existing" and v:
            print("The following files already existed in the submission folder:", flush=True)
            [print(url, flush=True) for url in v]
        if k == "missing" and v:
            print("The following files were registered in the submission, but missing on the server:", flush=True)
            [print(url, flush=True) for url in v]
        if k == "errors" and v:
            print("The following files were not downloaded due to unspecified errors:", flush=True)
            [print(url, flush=True) for url in v]
        if k == "downloaded" and v:
            print(f"len{v} of {len(fileinfo)} downloaded successfully", flush=True)


if __name__ == "__main__":
    main()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
