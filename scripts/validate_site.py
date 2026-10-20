"""Validate a static artifact for this repository's GitHub Pages project path."""
import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

BASE_PATH = "/project-n-preview"
ALLOWED = {".html", ".css", ".js", ".json", ".png", ".jpg", ".jpeg", ".gif",
           ".svg", ".webp", ".ico", ".avif", ".ttf", ".otf", ".woff", ".woff2",
           ".txt", ".webmanifest", ".wasm", ".mp3", ".mp4", ".webm"}
TEXT = {".html", ".css", ".js", ".json", ".txt", ".svg", ".webmanifest"}
SECRET = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
                    r"\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}|"
                    r"\bAKIA[A-Z0-9]{16}\b|\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}")


class InvalidSite(ValueError):
    pass


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.has_title = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "title":
            self.has_title = True
        if tag == "base":
            raise InvalidSite("HTML base elements are unsupported; export with the correct base path.")
        if tag in {"script", "img", "source", "video", "audio", "iframe"}:
            if values.get("src"):
                self.urls.append(values["src"])
        if tag == "link" and values.get("href"):
            self.urls.append(values["href"])
        if values.get("srcset"):
            if "data:" in values["srcset"]:
                raise InvalidSite("Use separate image files instead of data URLs in srcset.")
            self.urls.extend(item.strip().split()[0] for item in values["srcset"].split(",") if item.strip())


def check_url(root, owner, url):
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc:
        if parsed.hostname in {"localhost", "127.0.0.1", "0.0.0.0"}:
            raise InvalidSite(f"Local development URL in {owner.relative_to(root)}")
        if parsed.scheme not in {"https", "data"} and not (not parsed.scheme and parsed.netloc):
            raise InvalidSite(f"Unsupported resource URL in {owner.relative_to(root)}")
        return
    path = unquote(parsed.path)
    if not path:
        return
    if path.startswith("/"):
        if not path.startswith(BASE_PATH + "/"):
            raise InvalidSite(f"Resource outside {BASE_PATH}/ in {owner.relative_to(root)}: {path}")
        target = root / path[len(BASE_PATH) + 1:]
    else:
        target = owner.parent / path
    target = target.resolve()
    if not target.is_relative_to(root):
        raise InvalidSite(f"Resource escapes the artifact in {owner.relative_to(root)}")
    if target.is_dir():
        target = target / "index.html"
    if not target.is_file():
        raise InvalidSite(f"Missing local resource in {owner.relative_to(root)}: {path}")


def file_hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and p != root / "release-manifest.json"}


def validate(root, require_manifest=True):
    root = Path(root)
    if root.is_symlink() or (hasattr(root, "is_junction") and root.is_junction()):
        raise InvalidSite("Artifact root must not be a link.")
    root = root.resolve()
    if not (root / "index.html").is_file():
        raise InvalidSite("No site/index.html. Stage an approved static export before deploying.")
    total = 0
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            raise InvalidSite(f"Links are not allowed: {relative}")
        if any(part.startswith(".") for part in relative.parts) and relative.as_posix() != ".nojekyll":
            raise InvalidSite(f"Hidden development file: {relative}")
        if not path.is_file():
            continue
        if path.name != ".nojekyll" and path.suffix.lower() not in ALLOWED:
            raise InvalidSite(f"Unsupported artifact file (source maps and source files are excluded): {relative}")
        total += path.stat().st_size
        if total > 100 * 1024 * 1024:
            raise InvalidSite("Preview artifact exceeds the preparation limit of 100 MiB.")
        if path.suffix.lower() in TEXT:
            content = path.read_text(encoding="utf-8")
            if SECRET.search(content):
                raise InvalidSite(f"Possible embedded credential in {relative}; inspect locally.")
            if path.suffix.lower() == ".html":
                parser = References()
                parser.feed(content)
                if not parser.has_title:
                    raise InvalidSite(f"Missing document title in {relative}")
                for url in parser.urls:
                    check_url(root, path, url)
            elif path.suffix.lower() == ".css":
                for match in re.finditer(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)", content):
                    check_url(root, path, match.group(1).strip())
    if require_manifest:
        if not (root / ".nojekyll").is_file():
            raise InvalidSite("Missing .nojekyll marker.")
        try:
            manifest = json.loads((root / "release-manifest.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise InvalidSite("Missing or invalid release-manifest.json; stage the export again.") from error
        if not manifest.get("source_version") or manifest.get("base_path") != BASE_PATH:
            raise InvalidSite("Release manifest needs a source version and the correct base path.")
        if manifest.get("files") != file_hashes(root):
            raise InvalidSite("Artifact differs from its release manifest; stage the export again.")
    return len(file_hashes(root)), total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", default="site")
    args = parser.parse_args()
    try:
        count, size = validate(args.directory)
    except (InvalidSite, OSError, UnicodeError) as error:
        parser.exit(1, f"Preview validation failed: {error}\n")
    print(f"Validated {count} files, {size:,} bytes for {BASE_PATH}/")


if __name__ == "__main__":
    main()
