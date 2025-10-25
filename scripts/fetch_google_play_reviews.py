"""Utility script to export Google Play reviews.

This script uses the `google-play-scraper` package maintained at
https://github.com/JoMingyu/google-play-scraper to retrieve reviews for a
particular application.  The package is not part of the default `pipecat`
dependencies, so make sure it is installed before running the script::

    pip install google-play-scraper

Example usage to fetch all reviews for the "ai.rumik.ira.twa" application and
store them in ``reviews.json``::

    python scripts/fetch_google_play_reviews.py \
        --app-id ai.rumik.ira.twa \
        --language en \
        --country in \
        --output reviews.json

The resulting file can then be processed by downstream tooling.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any, Sequence


def _ensure_dependency() -> None:
    """Ensure that ``google_play_scraper`` is available.

    The repository cannot declare ``google-play-scraper`` as a default
    dependency, so we perform a lightweight runtime check and raise an
    informative error when the package is missing.
    """

    if importlib.util.find_spec("google_play_scraper") is None:
        message = (
            "google-play-scraper is required for this script. Install it with "
            "`pip install google-play-scraper`."
        )
        raise ModuleNotFoundError(message)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Google Play reviews.")
    parser.add_argument(
        "--app-id",
        required=True,
        help="Application identifier from the Google Play store (e.g. ai.rumik.ira.twa)",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Two letter language code (default: %(default)s)",
    )
    parser.add_argument(
        "--country",
        default="us",
        help="Two letter country code (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON file to store the retrieved reviews.",
    )
    return parser.parse_args(argv)


def _fetch_reviews(app_id: str, language: str, country: str) -> list[dict[str, Any]]:
    from google_play_scraper import Sort, reviews_all

    return reviews_all(
        app_id,
        lang=language,
        country=country,
        sort=Sort.NEWEST,
    )


def main(argv: Sequence[str] | None = None) -> int:
    _ensure_dependency()
    args = _parse_args(argv)
    reviews = _fetch_reviews(args.app_id, args.language, args.country)

    print(
        "Fetched %s reviews for app %s (language=%s, country=%s)."
        % (len(reviews), args.app_id, args.language, args.country)
    )

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(reviews, indent=2, ensure_ascii=False))
        print(f"Saved reviews to {args.output.resolve()}")
    else:
        print(json.dumps(reviews, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
