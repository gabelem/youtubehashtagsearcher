# YouTube Hashtag Generator

Python script that searches public YouTube videos and suggests hashtags related to the specified topic.

The tool uses `yt-dlp`, does not require a YouTube API key, and analyzes:

- videos related to the searched title;

- number of views;

- publication date;

- hashtags present in titles and descriptions;

- internal video tags;

- tag relevance in relation to the searched topic.

## Requirements

- Python 3.9 or higher

- Internet access xd

> Note: The original text says “Internet kkj,” which appears to be a typo or informal remark.

## Installation

Clone the project or download the files:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

Create and activate a virtual environment:

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
python gerador_hashtags_youtube.py "jerk drill type beat"
```

The program searches recent videos, calculates the most relevant hashtags, and displays the videos considered.

## Saving Hashtags in Markdown

To save only the hashtags to an `.md` file:

```bash
python gerador_hashtags_youtube.py \
  "jerk drill type beat" \
  --md hashtags.md
```

The file will contain a line similar to:

```
#jerkdrill #nydrill #hoodtraptypebeat
```

## Saving Complete Data as JSON

```bash
python gerador_hashtags_youtube.py \
  "jerk drill type beat" \
  --json resultado.json
```

The JSON contains the suggested hashtags, scores, frequency, and data from the analyzed videos.

## Main Options

| Option | Description | Default |
| --- | --- | --- |
| `--resultados` or `-n` | Number of videos to search | `20` |
| `--hashtags` or `-t` | Maximum number of hashtags | `15` |
| `--dias` | Consider videos published within the last N days | `365` |
| `--md` | Markdown file containing only the hashtags | — |
| `--json` | JSON file containing the complete data | — |

## Examples

Search for videos from the last 30 days and generate 10 hashtags:

```bash
python gerador_hashtags_youtube.py "digital marketing for beginners" --dias 30 --resultados 60 --hashtags 42 --md hashtags.md
```

Search using YouTube’s entire history:

```bash
python gerador_hashtags_youtube.py \
  "chocolate cake recipe" \
  --dias 0 \
  --md hashtags.md
```

Generate Markdown and JSON files at the same time:

```bash
python gerador_hashtags_youtube.py \
  "workout to gain muscle mass" \
  --md hashtags.md \
  --json resultado.json
```

## Notes

- The script uses YouTube’s public search through `yt-dlp`.

- Providing an API key is not necessary.

- The hashtags are suggestions based on the videos found; they do not guarantee an increase in views.

- YouTube may change its search system or limit automated queries.

- If the search does not return recent results, try increasing the value of `--dias` or using `--dias 0`.
