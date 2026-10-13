# YouTube Hashtag Generator

A Python command-line tool that searches public YouTube videos and suggests hashtags related to a title or topic.

The script uses [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) to query YouTube's public search. It does **not** require a YouTube API key and does not download video files.

## Requirements

- Python 3.9 or newer

- An internet connection

- The `yt-dlp` Python package

## Installation

Clone the repository or download `youtube_hashtag_generator.py`:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

Create and activate a virtual environment if desired.

### Linux or macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install `yt-dlp`:

```bash
python -m pip install --upgrade pip
python -m pip install -U yt-dlp
```

## Basic Usage

```bash
python youtube_hashtag_generator.py "jerk drill type beat"
```

The default behavior is:

- Search for 20 videos after applying the date filter.

- Consider videos published within the last 365 days.

- Generate up to 15 hashtags.

- Print the suggested hashtags and the videos considered in the terminal.

## Command-Line Syntax

```
python youtube_hashtag_generator.py TITLE [OPTIONS]
```

### Arguments and options

| Option | Description | Default |
| --- | --- | --- |
| `TITLE` | Required video title or search topic | — |
| `-n`, `--results` | Number of videos returned after date filtering | `20` |
| `-t`, `--hashtags` | Maximum number of hashtags to return | `15` |
| `--days` | Keep videos published within the last N days | `365` |
| `--md FILE` | Save only the suggested hashtags to a Markdown file | Not saved |
| `--json FILE` | Save the complete result to a JSON file | Not saved |

The values for `--results` and `--hashtags` must be greater than zero. The value for `--days` cannot be negative.

## Date Filtering

By default, the script keeps videos whose `upload_date` is within the last 365 days. Videos without a valid upload date are excluded when date filtering is enabled.

Use `--days 0` to disable date filtering:

```bash
python youtube_hashtag_generator.py \
  "chocolate cake recipe" \
  --days 0
```

`--days 0` does **not** request every video ever uploaded to YouTube. It only prevents the script from applying its local date filter to the search results returned by YouTube.

When `--days` is greater than zero, the script requests three times the requested number of search results to compensate for videos that may later be excluded by the date filter. It still returns no more than the value specified by `--results`.

## Examples

### Search recent videos

```bash
python youtube_hashtag_generator.py \
  "digital marketing for beginners" \
  --days 30 \
  --results 60 \
  --hashtags 10
```

This requests up to 180 YouTube search results, filters them to the last 30 days, and displays at most 60 videos. It then suggests at most 10 hashtags.

### Save only the hashtags to Markdown

```bash
python youtube_hashtag_generator.py \
  "jerk drill type beat" \
  --md hashtags.md
```

The Markdown file contains one line with space-separated hashtags, for example:

```
#jerkdrill #nydrill #hoodtraptypebeat
```

### Save complete results to JSON

```bash
python youtube_hashtag_generator.py \
  "jerk drill type beat" \
  --json results.json
```

### Generate Markdown and JSON at the same time

```bash
python youtube_hashtag_generator.py \
  "workout to gain muscle mass" \
  --md hashtags.md \
  --json results.json
```

## What the Script Analyzes

For each returned video, the script collects:

- Title

- YouTube URL

- Channel or uploader name

- View count

- Duration, when available

- Upload date, when available

- Hashtags found in the title and description

- Internal tags returned by YouTube, when available

Hashtags found in titles and descriptions are treated as **explicit hashtags**. Internal video tags are normalized into hashtag format and kept separately. Tags already present among the explicit hashtags are not added again.

## How Hashtags Are Selected

The script builds a context from:

- The search title or topic

- Relevant words found in the returned video titles

It then evaluates explicit hashtags and internal tags. A hashtag is considered only when it has evidence connected to the search title or collected video-title context. Generic stopwords and very short terms are ignored.

The score for each accepted hashtag is calculated from:

- Video view count

- The video's position in the returned results

- Whether the hashtag was explicitly used by the creator

Explicit hashtags receive a higher weight than internal tags. Frequency is used as a tie-breaker after the score, followed by term length. The final list is limited by `--hashtags`.

The script provides suggestions only. It does not guarantee higher views or better YouTube rankings.

## Terminal Output

After a successful search, the script prints:

1. The suggested hashtags.

1. The number of videos used.

1. The active date period or the message `all history` when `--days 0` is used.

1. The number of collected hashtags.

1. A list of the videos considered, sorted by view count.

View counts are abbreviated in the terminal as follows:

- `K` for thousands

- `M` for millions

- `B` for billions

## Markdown Output

When `--md FILE` is provided, the script writes one line containing the generated hashtags separated by spaces:

```
#hashtagone #hashtagsomething #anotherhashtag
```

The file is written using UTF-8 encoding. If the script finds no qualifying hashtags, the file can contain an empty line.

## JSON Output

When `--json FILE` is provided, the script writes a UTF-8 JSON document with indentation. Its top-level fields are:

```json
{
  "query": "jerk drill type beat",
  "days_filter": 365,
  "hashtags": [
    {
      "hashtag": "#jerkdrill",
      "score": 123.4567,
      "frequency": 3
    }
  ],
  "videos": []
}
```

Each object in `videos` contains these fields:

```
title
url
channel
views
duration
upload_date
hashtags
explicit_hashtags
internal_tags
```

## Errors and Limitations

- If `yt-dlp` is not installed, the script prints an installation command and exits.

- If YouTube cannot be queried, the script prints the error and exits with a failure status.

- If no videos remain after searching and date filtering, the script asks you to try a more specific title and exits with a failure status.

- YouTube may change its public search behavior or limit automated queries.

- Search results, metadata availability, tags, view counts, and upload dates depend on what YouTube returns through `yt-dlp`.

- Videos without a valid upload date are skipped when `--days` is greater than zero.

- The script only reads public metadata; it does not download videos.

## Project Files

```
youtube_hashtag_generator.py  Main Python script
README.md                     Project documentation
```
