# YouTube Hashtag Generator

A Python tool that searches public YouTube videos and suggests relevant hashtags for a topic or video title.

The tool uses [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) and does not require a YouTube API key.

## Features

- Searches public YouTube videos related to a topic.

- Analyzes video titles, descriptions, views, upload dates, visible hashtags, and internal tags.

- Prioritizes hashtags used directly by video creators.

- Filters hashtags based on their relevance to the search topic.

- Supports filtering videos by publication date.

- Displays the videos used to generate the suggestions.

- Exports results as Markdown or JSON.

## Requirements

- Python 3.9 or newer

- Internet connection

## Installation

Clone the repository or download the project files:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

Create and activate a virtual environment.

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

Install the dependency:

```bash
python -m pip install --upgrade pip
python -m pip install -U yt-dlp
```

## Basic Usage

```bash
python youtube_hashtag_generator.py "jerk drill type beat"
```

By default, the program searches up to 20 videos from the last 365 days and generates up to 15 hashtags.

## Command-Line Options

| Option | Description | Default |
| --- | --- | --- |
| `-n`, `--results` | Number of videos to search | `20` |
| `-t`, `--hashtags` | Maximum number of hashtags to generate | `15` |
| `--days` | Consider videos published within the last N days | `365` |
| `--md FILE` | Save only the hashtags to a Markdown file | — |
| `--json FILE` | Save the complete results to a JSON file | — |

Use `--days 0` to search across YouTube's entire available history.

## Examples

### Search for recent videos

Search videos from the last 30 days and generate up to 10 hashtags:

```bash
python youtube_hashtag_generator.py \
  "digital marketing for beginners" \
  --days 30 \
  --results 60 \
  --hashtags 10
```

### Save hashtags to Markdown

```bash
python youtube_hashtag_generator.py \
  "jerk drill type beat" \
  --md hashtags.md
```

The generated file contains one line, for example:

```
#jerkdrill #nydrill #hoodtraptypebeat
```

### Save complete results to JSON

```bash
python youtube_hashtag_generator.py \
  "jerk drill type beat" \
  --json results.json
```

The JSON file includes:

- The original search query

- The date filter

- Suggested hashtags

- Hashtag scores

- Hashtag frequency

- Data for the analyzed videos

### Generate Markdown and JSON simultaneously

```bash
python youtube_hashtag_generator.py \
  "workout to gain muscle mass" \
  --md hashtags.md \
  --json results.json
```

### Search all available history

```bash
python youtube_hashtag_generator.py \
  "chocolate cake recipe" \
  --days 0
```

## Output

The terminal displays the suggested hashtags and the videos considered, ranked by view count. For example:

```
Suggested hashtags:

#chocolatecakerecipe #easycake #baking

Data source: 20 public videos from the last 365 days, 42 hashtags found in titles, descriptions, and tags, ranked by views.

Videos considered:
 1.     1.2M | Easy Chocolate Cake Recipe — Example Channel
```

## How Hashtags Are Ranked

The ranking considers:

1. Whether the hashtag was explicitly used by the creator in the title or description.

1. Whether the hashtag appears in the video's internal tags.

1. The number of videos containing the hashtag.

1. The number of views on the videos containing the hashtag.

1. The hashtag's relevance to the search query and video titles.

1. The position of each video in the search results.

Creator-provided hashtags receive a higher score than internal video tags.

## Notes and Limitations

- The script uses YouTube's public search through `yt-dlp`.

- A YouTube API key is not required.

- Hashtags are suggestions based on the videos found; they do not guarantee more views.

- YouTube may change its search system or limit automated queries.

- Search results depend on YouTube's current availability and ranking system.

- If no recent videos are found, increase the value of `--days` or use `--days 0`.

- The tool does not download videos; it only collects public metadata.

## Project Files

```
youtube_hashtag_generator.py  Main Python script
README.md                     Project documentation
```

## License

Add your preferred license here before publishing the project. For example, you may use the [MIT License](https://opensource.org/license/mit/).
