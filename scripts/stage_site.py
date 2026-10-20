"""Copy an approved static export into site/ without changing development source."""
import argparse
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from validate_site import BASE_PATH, InvalidSite, file_hashes, validate

REPO = Path(__file__).resolve().parents[1]


def stage(source, version, spa=False, repo=REPO):
    source, repo = Path(source).resolve(), Path(repo).resolve()
    destination = repo / "site"
    if source == destination or source.is_relative_to(destination) or destination.is_relative_to(source):
        raise InvalidSite("Export source and staging destination must be separate directories.")
    if not version.strip():
        raise InvalidSite("A development commit or approved snapshot label is required.")
    if destination.is_symlink() or (hasattr(destination, "is_junction") and destination.is_junction()):
        raise InvalidSite("site/ must not be a link.")
    validate(source, require_manifest=False)
    with tempfile.TemporaryDirectory(prefix=".staging-", dir=repo) as temporary:
        prepared = Path(temporary) / "site"
        shutil.copytree(source, prepared)
        (prepared / ".nojekyll").touch()
        if spa and not (prepared / "404.html").exists():
            shutil.copyfile(prepared / "index.html", prepared / "404.html")
        manifest = {
            "source_version": version.strip(),
            "staged_at": datetime.now(timezone.utc).isoformat(),
            "base_path": BASE_PATH,
            "spa_fallback": spa,
            "files": file_hashes(prepared),
        }
        (prepared / "release-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        validate(prepared)
        if destination.exists():
            backups = repo / ".deployment-backups"
            if backups.is_symlink() or (hasattr(backups, "is_junction") and backups.is_junction()):
                raise InvalidSite("Backup directory must not be a link.")
            backups.mkdir(exist_ok=True)
            backup = backups / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            assert destination.resolve().is_relative_to(repo) and backup.resolve().is_relative_to(repo)
            destination.rename(backup)
            try:
                prepared.rename(destination)
            except OSError:
                backup.rename(destination)
                raise
        else:
            prepared.rename(destination)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Approved static export directory, never the app source directory")
    parser.add_argument("--source-version", required=True, help="Development commit or approved snapshot label")
    parser.add_argument("--spa", action="store_true", help="Add a 404.html fallback for a single-page app")
    args = parser.parse_args()
    try:
        destination = stage(args.source, args.source_version, args.spa)
    except (InvalidSite, OSError, UnicodeError) as error:
        parser.exit(1, f"Staging failed: {error}\n")
    print(f"Staged and validated: {destination}. Review the diff before committing.")


if __name__ == "__main__":
    main()
