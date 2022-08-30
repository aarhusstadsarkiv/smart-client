import codecs
from http.client import HTTPException
import sys
import os
import json
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import httpx
from gooey import Gooey, GooeyParser

import smart_client.config as config

# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------
__version__ = "0.1.0"

utf8_stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
utf8_stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")
if sys.stdout.encoding != "UTF-8":
    sys.stdout = utf8_stdout  # type: ignore
if sys.stderr.encoding != "UTF-8":
    sys.stderr = utf8_stderr  # type: ignore


def setup_parser(cli: Any) -> Any:
    cli.add_argument(
        "uuid",
        metavar="Afleveringens uuid",
        help=("Unik id for afleveringen. Eks.: dbd9bcb8-8110-4a10-9fe7-d12d9ca9f09d"),
        gooey_options={"full_width": True},
    )
    cli.add_argument(
        "destination",
        metavar="Destination",
        help=(
            "Sti til rodmappen, hvor filer og metadata skal kopieres (mappen behøver ikke"
            " eksistere i forvejen)"
        ),
        widget="DirChooser",
        type=Path,
        gooey_options={
            "default_path": str(Path(Path.home(), "Downloads", "Smartarkivering")),
            "full_width": True,
        },
    )
    # cli.add_argument(
    #     "--delete",
    #     metavar="Slet oprindelige filer",
    #     action="store_true",
    #     help="Slet filerne fra deres oprindelige placering efter kopiering",
    # )

    args = cli.parse_args()
    return args


def get_submission(uuid: str, out_dir: Path) -> dict:
    """Fetch and save submission-data

    Given a uuid and an out_dir, it tries to fetch the submission-data from
    the API. If fetched, it is then saved to a json-file and returned as a
    dict.

    Args:
        uuid (UUID): uuid of the submission. Has to be copied from the mail-notification
        out_dir (Path): full path to the folder where the submission.json is saved. Usually
            the folder is named after the uuid

    Returns:
        A dict-representation of the submission-data returned by the api-endpoint. Currently
            https://selvbetjening.aarhuskommune.dk/da/webform_rest/smartarkivering_test/submission/{submission_id}

    Raises:
        HTTPException: All non-200 status_codes are raised
    """

    with httpx.Client() as client:
        r = client.get(
            f"{os.getenv('SUBMISSION_URL')}/{uuid}?api-key={os.getenv('API_KEY')}"
        )
        if r.status_code == 404:
            raise HTTPException(
                f"FEJl. Der findes ikke en aflevering med dette uuid: {uuid}"
            )
        elif r.status_code != 200:
            raise HTTPException(
                f"FEJl. Kunne ikke hente en aflevering med dette uuid: {uuid}"
            )

        submission: dict = r.json()
        with open(Path(out_dir, "submission.json"), "w", encoding="utf-8") as f:
            json.dump(submission, f, ensure_ascii=False, indent=4)
        return submission


def download_files(submission: dict, out_dir: Path) -> None:
    """Download all form-files

    Given a submission-dict (returned from get_submission()) and an out_dir, it
    tries to download all files attached to the submitted form to the out_dir.

    Args:
        submission (dict): The submission-data returned by the API in a previous step.
        out_dir (Path): full path to the folder where the files are saved.

    Raises:
        HTTPException: All non-200 status_codes are raised
    """

    # get file_ids from the "file_chooser" ()
    file_ids: list = submission["data"].get("file_chooser", [])
    if not file_ids:
        raise ValueError("FEJL. Afleveringen indeholder ingen filer.")

    with httpx.Client() as client:
        for file_id in file_ids:
            # get file-metadata
            url: str = (
                f"{os.getenv('FILEDATA_URL')}/{file_id}?api-key={os.getenv('API_KEY')}"
            )
            print(f"Henter metadata om fil_id {file_id}: {url}", flush=True)
            r = client.get(url)
            if r.status_code == 404:
                raise HTTPException(
                    f"FEJl. Der findes ikke en fil på serveren med dette fil_id: {file_id}"
                )
            elif r.status_code != 200:
                raise HTTPException(
                    f"FEJl. Der Kunne ikke hentes en fil på serveren med dette fil_id: {file_id}"
                )
            metadata = r.json
            filename: str = metadata["filename"].get("value")
            url = f"{os.getenv('BLOB_URL')}//{metadata}?api-key={os.getenv('API_KEY')}"
            print(f"Henter fil: {url}", flush=True)
            # fetch blob
            with urlopen(url) as blob:
                content = blob.read()
            # save blob
            file_path: Path = out_dir / filename
            with open(file_path, "wb") as download:
                download.write(content)

            # f = client.get(url)
            # with open(file_path, "wb") as download:
            #     download.write(f.content)


@Gooey(
    program_name=f"Smartarkivering, version {__version__}",
    program_description="Klient til at hente afleveringer fra smartarkivering.dk",
    default_size=(600, 700),
    show_restart_button=False,
    show_failure_modal=False,
    show_success_modal=False,
)
def main() -> None:
    # Load config or exit
    try:
        config.load_configuration()
    except Exception as e:
        sys.exit(e)

    # General parser
    cli = GooeyParser(description="Smartarkivering")
    args = setup_parser(cli)

    # Tests
    if not Path(args.destination).is_dir():
        print(f"FEJL. Destinationen skal være en mappe.", flush=True)

    out_dir = Path(args.destination, args.uuid)
    # if out_dir.exists():
    #     print(f"ADVARSEL. Destinationsmappen eksisterer allerede. Slet den inden ")
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        sys.exit(f"FEJl. Kan ikke oprette destinationsmappen: {e}")

    try:
        # get_submission prints any errors with http or json-parsing
        submission: dict = get_submission(args.uuid, out_dir)
    except (HTTPException, ValueError) as e:
        sys.exit(e)

    try:
        download_files(submission, out_dir)
    except (HTTPException, ValueError) as e:
        sys.exit(e)


if __name__ == "__main__":
    main()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
