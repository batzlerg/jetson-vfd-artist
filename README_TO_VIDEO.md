# to_video.py — VFD Animation Renderer

Convert generated animation Python files to MP4 videos with proper VFD-style formatting.

## Setup

```

chmod +x to_video.py

```

**Dependencies:**

- FFmpeg: `sudo apt-get install ffmpeg`
- Python 3.6+
- Pillow: `pip install Pillow` (usually already installed)
- cd5220 module (from local repo)


## Usage

### Render all new animations

```

./to_video.py

```

Skips existing videos in `generated_animations/videos/`. Safe to run repeatedly.

### Force re-render everything

```

./to_video.py --force

```


### Custom animation duration and frame rate

```

./to_video.py -d 15 --fps 8

```


### Render specific files only

```

./to_video.py anim_1234567890.py anim_9876543210.py

```


## Output

- **Location:** `generated_animations/videos/*.mp4`
- **Format:** 640×200px, H.264, yuv420p, 6 FPS (default)
- **Appearance:** Cyan text on black with balanced 40px side margins and 45px top margin
- **Frames:** Each animation becomes a short video matching its execution duration


## What happens

1. Loads each `.py` animation file from `generated_animations/`
2. Executes the animation function via a mock display that captures frames
3. Renders each frame as an image (monospace font, proper spacing)
4. Pipes raw RGB data directly to FFmpeg for MP4 encoding
5. Saves output to `videos/` with idempotent caching

## Troubleshooting

**FFmpeg not found:**

```

sudo apt-get install ffmpeg

```

**Font path error:**
Script looks for DejaVu Sans Mono Bold at `/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf`. Update `FONT_PATH` in the script if your system stores fonts elsewhere.

**Corrupt animation files (emojis/markdown):**
Script skips these safely and reports them. No action needed—they're filtered automatically.

**Videos not rendering:**
Check FFmpeg is working: `ffmpeg -version`

## Notes

- Idempotency: Existing MP4s are never overwritten unless `--force` is used
- Frame count varies with animation duration and FPS
- Character layout: 20 columns × 2 rows with proper monospace kerning
- Suitable for: Visual QA, dataset generation, training models on VFD aesthetics
jetson@jetson:~/jetson-vfd-artist\$

---

update the README. output the full final modified state as one preformatted block.

```markdown
# to_video.py — VFD Animation Renderer

Convert VFD animations to MP4 videos. Auto-detects `.py` (executes code) or `.jsonl` (uses captured frames).

## Setup

```

chmod +x to_video.py

```

**Dependencies:**
- FFmpeg: `sudo apt-get install ffmpeg`
- Python 3.7+
- Pillow: `pip install Pillow`
- cd5220 module (auto-installed via requirements.txt)

## Usage

### Render all animations in directory
```

./to_video.py generated_animations/

```
Processes all `.py` and `.jsonl` files. Skips existing videos unless `--force` used.

### Render from captured frames (fast)
```

./to_video.py generated_animations/frame_captures/

```
Uses JSONL files created by `vfd_agent.py --preview` during playback.

### Render specific file
```

./to_video.py generated_animations/anim_1234567890.py         \# execute code
./to_video.py frame_captures/anim_1234567890_playback.jsonl   \# use captured frames

```

### Force re-render with custom settings
```

./to_video.py generated_animations/ --force -d 15 --fps 8

```

## File Type Auto-Detection

The script automatically detects file type:
- **`.py` files**: Executes animation code and captures frames
- **`.jsonl` files**: Loads pre-captured frames (faster, no execution)

JSONL files are created when running:
```

VFD_DEVICE=simulator ./vfd_agent.py --preview      \# creates *_playback.jsonl
./vfd_agent.py --preview                           \# creates *_playback.jsonl with hardware

```

## Output

- **Location:** `generated_animations/videos/*.mp4`
- **Format:** 640×200px, H.264, yuv420p
- **Frame rate:** 6 FPS (default, configurable with `--fps`)
- **Appearance:** Cyan monospace text on black with 40px side margins

## Command Reference

```

./to_video.py <path>              \# Required: directory or file path
-d, --duration FLOAT            \# Duration for .py files (default: 10s)
--fps INT                       \# Frame rate for .py files (default: 6)
--force                         \# Re-render existing videos

```

## Workflow Examples

### Generate and render new animation
```

VFD_DEVICE=simulator ./vfd_agent.py --idea "test" --preview
./to_video.py generated_animations/frame_captures/anim_*.jsonl

```

### Batch render all generated code
```

./to_video.py generated_animations/

```

### Re-render specific animation with custom duration
```

./to_video.py generated_animations/anim_123.py --force -d 20 --fps 10

```

## Troubleshooting

**FFmpeg not found:**
```

sudo apt-get install ffmpeg

```

**Font path error:**
Script uses `/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf`. Edit `FONT_PATH` if your system differs.

**No frames captured from .py file:**
Animation may have errors. Check with:
```

VFD_DEVICE=simulator ./vfd_agent.py --idea "test animation" --preview

```

**JSONL parsing error:**
Ensure JSONL file has valid format (first line = metadata, subsequent lines = frames). Use `inspect_frame_captures.sh` to validate.

## Technical Details

### Frame Source Priority
1. `.jsonl` files: Loads frames from disk (no execution)
2. `.py` files: Executes animation via `FrameCapture` wrapper

### FPS Handling
- `.py` files: Uses `--fps` argument (default: 6)
- `.jsonl` files: Auto-calculates from metadata (total_frames / duration)

### Video Encoding
- Direct RGB24 pipe to FFmpeg (no intermediate files)
- CRF 18 (high quality)
- Compatible with all media players

## Integration

Works seamlessly with:
- `vfd_agent.py` - Generates animations and optional JSONL captures
- `frame_capture.py` - Shared frame capture mechanism
- `inspect_frame_captures.sh` - Validate JSONL before rendering

## See Also

- `README_VFD_AGENT.md` - Animation generation
- `README_FRAME_CAPTURE.md` - Frame capture system
