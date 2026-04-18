# video-looper
Loop any video N times with a count overlay and optional timer — supports local files and YouTube URLs.
# Mantra Video Creator

A Python CLI tool to loop a video N times with a **count overlay** (e.g. `1 / 22`, `2 / 22`, …) and an optional running timer — perfect for mantra chanting sessions, meditation loops, or any repeating video content.

## What It Does

- Takes any `.mp4` video (or a **YouTube URL**) as input
- Loops it a configurable number of times (default: 22)
- Overlays a **counter** (`current / total`) in the center of the frame
- Optionally overlays a **continuous running timer**
- Concatenates all loops into a single output `.mp4`
- Customizable font size, color, and position (top / bottom)

### Example Output

A 3-minute mantra video looped 22 times → `66-minute output.mp4` with `1 / 22 … 22 / 22` displayed in gold text.

---

## Requirements

### System Dependencies

| Tool | Purpose | Install |
|------|---------|---------|
| `ffmpeg` | Video encoding & concatenation | `sudo apt install ffmpeg` |
| `ffprobe` | Get video duration (ships with ffmpeg) | (included with ffmpeg) |

### Python Dependencies

| Package | Purpose |
|---------|---------|
| `yt-dlp` | Download videos from YouTube (auto-installed if missing) |

> Python 3.8+ is required. No other pip packages needed — the script uses only the standard library plus `yt-dlp`.

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/video-looper.git
cd mantra-video-creator

# 2. Install system dependency
sudo apt install ffmpeg          # Ubuntu / Debian
# brew install ffmpeg            # macOS

# 3. (Optional) Install yt-dlp for YouTube support
pip install yt-dlp
```

---

## Usage

### Basic — loop a local video 22 times
```bash
python mantra_video_creator.py input.mp4 -o output_22x.mp4
```

### Loop with a running timer overlay
```bash
python mantra_video_creator.py input.mp4 -o output_22x.mp4 --timer
```

### Download from YouTube and loop 11 times
```bash
python mantra_video_creator.py "https://www.youtube.com/watch?v=YOUR_VIDEO_ID" \
  -o mantra_11x.mp4 --loops 11
```

### Custom font color, size, and position
```bash
python mantra_video_creator.py input.mp4 -o output.mp4 \
  --loops 108 --color white --font-size 60 --position bottom
```

---

## CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `input` | *(required)* | Input `.mp4` file path **or** a YouTube URL |
| `-o`, `--output` | `output_looped.mp4` | Path for the output file |
| `-l`, `--loops` | `22` | Number of times to loop the video |
| `--timer` | off | Show a continuous running timer on the video |
| `--font-size` | `72` | Font size of the counter overlay |
| `--color` | `gold` | Font color (any FFmpeg color name, e.g. `white`, `red`) |
| `--position` | `top` | Overlay position: `top` or `bottom` |

---

## How It Works

1. **Dependency check** — verifies `ffmpeg` and `ffprobe` are on `PATH`.
2. **Download** (if URL given) — uses `yt-dlp` to fetch the best quality ≤ 1080p MP4.
3. **Segment creation** — for each loop iteration, `ffmpeg` re-encodes the source with a `drawtext` filter showing `i / total` (and optionally a timer).
4. **Concatenation** — all segments are joined stream-copy with `ffmpeg -f concat`, so the final mux is fast and lossless.
5. **Cleanup** — temporary part files in `/tmp/mantra_parts/` are deleted automatically.

---

## Supported Platforms

- Linux (Ubuntu / Debian recommended)
- macOS (install ffmpeg via Homebrew)
- Windows (WSL2 recommended, or install ffmpeg manually)

---

## License

MIT
