from __future__ import annotations

import argparse
import shutil
import urllib.request
import zipfile
from pathlib import Path


AAEC_URL = "https://tudatalib.ulb.tu-darmstadt.de/bitstreams/1ae1718d-7e65-42ba-9e84-dbf52fe92f56/download"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download and extract Argument Annotated Essays Corpus v2.")
    parser.add_argument("--output-dir", default="data/raw", help="Directory for downloaded and extracted AAEC files.")
    parser.add_argument("--force", action="store_true", help="Download and extract again even if files already exist.")
    return parser.parse_args()


def download_file(url: str, target: Path, force: bool = False) -> None:
    if target.exists() and not force:
        print(f"Using existing download: {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading AAEC from {url}")
    with urllib.request.urlopen(url) as response, target.open("wb") as file:
        shutil.copyfileobj(response, file)
    print(f"Saved {target}")


def extract_zip(zip_path: Path, output_dir: Path, force: bool = False) -> Path:
    corpus_dir = output_dir / "ArgumentAnnotatedEssays-2.0"
    brat_dir = corpus_dir / "brat-project-final"
    if brat_dir.exists() and not force:
        print(f"Using existing extracted corpus: {corpus_dir}")
        return corpus_dir

    print(f"Extracting {zip_path}")
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(output_dir)

    brat_zip = corpus_dir / "brat-project-final.zip"
    if brat_zip.exists():
        with zipfile.ZipFile(brat_zip) as archive:
            archive.extractall(corpus_dir)

    if not brat_dir.exists():
        raise FileNotFoundError(f"Could not find extracted BRAT directory: {brat_dir}")
    print(f"Extracted AAEC to {corpus_dir}")
    return corpus_dir


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    zip_path = output_dir / "ArgumentAnnotatedEssays-2.0.zip"
    download_file(AAEC_URL, zip_path, force=args.force)
    extract_zip(zip_path, output_dir, force=args.force)


if __name__ == "__main__":
    main()

