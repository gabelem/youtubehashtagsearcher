#!/usr/bin/env python3
"""Trending YouTube hashtag searcher. YES... this was vibecoded @-@

The search uses YouTube's public search engine through yt-dlp.
Installation: python -m pip install -U yt-dlp
Example: python youtube_hashtag_generator.py "chocolate cake recipe" -n 20 -t 15
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from typing import Any

try:
    import yt_dlp
except ImportError:
    print(
        "Missing dependency. Install it with: python -m pip install -U yt-dlp",
        file=sys.stderr,
    )
    raise SystemExit(2)


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "for",
    "from", "has", "have", "he", "her", "here", "his", "how", "i", "in",
    "into", "is", "it", "its", "me", "more", "my", "no", "not", "of", "on",
    "or", "our", "ours", "she", "so", "some", "that", "the", "their", "theirs",
    "them", "there", "these", "they", "this", "those", "to", "too", "under",
    "was", "we", "were", "what", "when", "where", "which", "who", "why", "with",
    "you", "your", "yours", "video", "videos", "official", "ft", "feat", "part",
}


@dataclass
class Video:
    title: str
    url: str
    channel: str
    views: int
    duration: int | None
    upload_date: str | None
    hashtags: list[str]
    explicit_hashtags: list[str]
    internal_tags: list[str]


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower()


def relevant_tokens(text: str) -> list[str]:
    normalized = clean_text(text)
    words = re.findall(r"[a-z0-9][a-z0-9_'-]*", normalized)
    return [
        word.strip("_'-") for word in words
        if len(word.strip("_'-")) >= 3
        and word not in STOPWORDS
    ]


def hashtag(token: str) -> str:
    # Keep compound words in a single hashtag: #studytips.
    token = re.sub(r"[^a-zA-Z0-9_]", "", clean_text(token))
    # Fix the truncated form that appeared when an internal tag was treated
    # as if it already contained the # character.
    token = {
        "erkdrill": "jerkdrill",
        "erkdrilltypebeat": "jerkdrilltypebeat",
    }.get(token, token)
    return f"#{token}" if token else ""


def extract_hashtags(text: str) -> list[str]:
    """Extract visible hashtags from a title/description and normalize their spelling."""
    found = re.findall(r"#[\wÀ-ÿ]+", text or "", flags=re.UNICODE)
    result = []
    for item in found:
        normalized = hashtag(item[1:])
        if normalized and normalized not in result:
            result.append(normalized)
    return result


def search(title: str, count: int, days: int = 365) -> list[Video]:
    options = {
        "quiet": True,
        "skip_download": True,
        # False allows the video's description, tags, and hashtags to be obtained, in addition to its title.
        "extract_flat": False,
        "noplaylist": True,
        "ignoreerrors": True,
        "no_warnings": True,
    }
    # Search for more items when a date filter is used because some of the
    # results returned by YouTube may fall outside the selected period.
    search_count = count if days == 0 else max(count * 3, count)
    query = f"ytsearch{search_count}:{title}"
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            data: dict[str, Any] = ydl.extract_info(query, download=False) or {}
    except Exception as error:
        raise RuntimeError(f"Unable to query YouTube: {error}") from error

    videos: list[Video] = []
    for item in data.get("entries") or []:
        if not item:
            continue
        url = item.get("webpage_url") or item.get("url") or ""
        if not url and item.get("id"):
            url = f"https://www.youtube.com/watch?v={item['id']}"
        explicit_hashtags = extract_hashtags(item.get("title") or "")
        explicit_hashtags += [
            tag for tag in extract_hashtags(item.get("description") or "")
            if tag not in explicit_hashtags
        ]
        internal_tags = [
            hashtag(str(tag)) for tag in (item.get("tags") or [])
            if hashtag(str(tag)) and hashtag(str(tag)) not in explicit_hashtags
        ]
        hashtags = explicit_hashtags + [
            tag for tag in internal_tags if tag not in explicit_hashtags
        ]
        videos.append(Video(
            title=item.get("title") or "",
            url=url,
            channel=item.get("channel") or item.get("uploader") or "",
            views=int(item.get("view_count") or 0),
            duration=item.get("duration"),
            upload_date=item.get("upload_date"),
            hashtags=hashtags,
            explicit_hashtags=explicit_hashtags,
            internal_tags=internal_tags,
        ))
    if days > 0:
        cutoff = date.today() - timedelta(days=days)
        recent: list[Video] = []
        for video in videos:
            if not video.upload_date:
                continue
            try:
                published = datetime.strptime(video.upload_date, "%Y%m%d").date()
            except ValueError:
                continue
            if published >= cutoff:
                recent.append(video)
        videos = recent

    return sorted(videos, key=lambda video: video.views, reverse=True)[:count]


def generate_hashtags(title: str, videos: list[Video], limit: int) -> list[tuple[str, float, int]]:
    # The filter uses only the collected corpus: the query, titles, and hashtags
    # from the results themselves. There is no offline database of generic terms.
    context = set(relevant_tokens(title))
    context.update(
        term for video in videos for term in relevant_tokens(video.title)
    )
    context = {term for term in context if len(term) >= 4}

    def has_evidence(tag: str) -> bool:
        term = tag[1:]
        compact_title = re.sub(r"[^a-z0-9]", "", clean_text(title))
        if term in compact_title:
            return True
        # Accept compound hashtags when their components appear in the
        # titles/query; reject tags copied from an unrelated topic.
        return any(word in term for word in context)

    frequency = Counter()
    score = defaultdict(float)
    for position, video in enumerate(videos):
        weight = (video.views + 1) ** 0.5 / (position + 1) ** 0.35
        # Highest priority: hashtags published by the creators themselves.
        for tag in set(video.explicit_hashtags):
            term = tag[1:]
            if len(term) < 3 or term in STOPWORDS or not has_evidence(tag):
                continue
            frequency[term] += 1
            score[term] += weight * 2.20

        # Secondary priority: internal tags, still subject to the context filter.
        for tag in set(video.internal_tags):
            term = tag[1:]
            if len(term) < 3 or term in STOPWORDS or not has_evidence(tag):
                continue
            frequency[term] += 1
            score[term] += weight * 1.40

    ordered = sorted(
        score,
        key=lambda term: (score[term], frequency[term], len(term)),
        reverse=True,
    )
    return [
        (hashtag(term), score[term], frequency[term])
        for term in ordered[:limit]
        if hashtag(term)
    ]


def format_views(value: int) -> str:
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate YouTube hashtags from the most-viewed videos."
    )
    parser.add_argument("title", help="Video title or topic")
    parser.add_argument(
        "-n", "--results", type=int, default=20,
        help="Number of videos to search (default: 20)",
    )
    parser.add_argument(
        "-t", "--hashtags", type=int, default=15,
        help="Maximum number of hashtags (default: 15)",
    )
    parser.add_argument(
        "--days", type=int, default=365,
        help="Consider videos published within the last N days; use 0 for all history (default: 365)",
    )
    parser.add_argument(
        "--json", dest="json_file",
        help="Save results and hashtags to a JSON file",
    )
    parser.add_argument(
        "--md", dest="md_file",
        help="Save only the hashtags on a single line in a Markdown file",
    )
    args = parser.parse_args()

    if args.results < 1 or args.hashtags < 1 or args.days < 0:
        parser.error("--results and --hashtags must be greater than zero; --days cannot be negative")

    try:
        videos = search(args.title, args.results, args.days)
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    if not videos:
        print("No videos found. Try a more specific title.", file=sys.stderr)
        return 1

    result = generate_hashtags(args.title, videos, args.hashtags)
    print("\nSuggested hashtags:\n")
    print(" ".join(tag for tag, _, _ in result))
    hashtag_count = sum(len(video.hashtags) for video in videos)
    period = "all history" if args.days == 0 else f"the last {args.days} days"
    print(
        f"\nData source: {len(videos)} public videos from {period}, {hashtag_count} "
        "hashtags found in titles, descriptions, and tags, ranked by views.\n"
    )
    print("Videos considered:")
    for index, video in enumerate(videos, 1):
        print(f"{index:2}. {format_views(video.views):>9} | {video.title} — {video.channel}")

    if args.json_file:
        payload = {
            "query": args.title,
            "days_filter": args.days,
            "hashtags": [
                {"hashtag": tag, "score": round(score, 4), "frequency": frequency}
                for tag, score, frequency in result
            ],
            "videos": [asdict(video) for video in videos],
        }
        with open(args.json_file, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        print(f"\nJSON saved to: {args.json_file}")

    if args.md_file:
        # Keep the literal hashtags so they can be copied and pasted directly.
        with open(args.md_file, "w", encoding="utf-8") as file:
            file.write(" ".join(tag for tag, _, _ in result) + "\n")
        print(f"\nMarkdown saved to: {args.md_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
