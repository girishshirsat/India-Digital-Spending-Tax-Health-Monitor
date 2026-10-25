
import json
from datetime import date
from pathlib import Path


def write_manifest(folder, source, file_count):
    """Write metadata about a downloaded dataset."""

    folder = Path(folder)

    manifest = {
        "source": source,
        "file_count": file_count,
        "downloaded_on": date.today().isoformat(),
    }

    manifest_path = folder / "_manifest.json"

    # Ensure the folder exists
    folder.mkdir(parents=True, exist_ok=True)

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest_path
