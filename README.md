# jetson-vfd-artist

AI-powered animation generator for CD5220 VFD displays.

This project consists of three main components:
*   **VFD Animation Agent (`vfd_agent.py`):** Generates animations using AI.
*   **Frame Capture Inspector (`inspect_frame_captures.sh`):** A tool for examining and analyzing frame captures.
*   **VFD Animation Renderer (`to_video.py`):** Converts generated animations to MP4 videos.

## Prerequisites

- NVIDIA Jetson (tested on Nano, TX1/TX2, Xavier)
- CD5220 VFD display connected via USB
- Ollama installed with qwen2.5:3b model (or your preferred model)
- Python 3.7+
- FFmpeg (for video rendering): `sudo apt-get install ffmpeg`

## Install

```bash
# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install core dependencies
pip install -r requirements.txt
```

### For Interactive Development (Optional)

To use the interactive Marimo notebooks for development and analysis, install the additional dependencies:

```bash
pip install -r requirements-marimo.txt
```

## Quick Test

Verify your setup:

```


# Check hardware connection

ls /dev/ttyUSB*

# Test with simulator (no hardware needed)

VFD_DEVICE=simulator ./vfd_agent.py --idea "test" --preview

```

## Project Structure

```

jetson-vfd-artist/
├── vfd_agent.py              \# Main animation agent
├── to_video.py               \# Video renderer
├── inspect_frame_captures.sh \# Frame inspector
├── generated_animations/     \# Output directory
│   ├── frame_captures/      \# JSONL frame data
│   └── videos/              \# Rendered MP4s
└── prompt.txt               \# AI generation template

```

## VFD Animation Agent (`vfd_agent.py`)

A high-fidelity LLM-powered animation generation system for the CD5220 VFD customer display. The agent generates creative, spec-compliant ASCII animations through iterative AI collaboration with Ollama, featuring real-time runtime validation and continuous background generation.

### Overview

The agent operates in two distinct modes:

#### Continuous Generation Mode (Default)

*   Generates animations **infinitely** in the background
*   Maintains a **queue** of pre-generated animations (configurable size)
*   **Display never goes blank** - plays queued animations while new ones generate
*   Ideal for gallery/art installation scenarios where variety matters
*   Run: `./vfd_agent.py`

#### Single-Shot Mode (Custom Ideas)

*   Generates **exactly ONE animation** based on a custom idea
*   Loops that animation **forever** until interrupted
*   Useful for testing, refinement, or showcasing a specific concept
*   Run: `./vfd_agent.py --idea "fighting beavers"`

### Quick Start

#### Basic Usage

```


# Infinite random animations on hardware

./vfd_agent.py

# Custom animation idea (loops forever)

./vfd_agent.py --idea "seven ducks quacking"

# Test without hardware using simulator

VFD_DEVICE=simulator ./vfd_agent.py --idea "bouncing ball" --preview

# Verbose diagnostics

./vfd_agent.py --idea "exploding stars" -v --preview

# Adjust animation duration and frame rate

./vfd_agent.py -d 15 --fps 10 --idea "morphing shapes"

```

#### Command-Line Options

| Flag | Description | Example |
| :-- | :-- | :-- |
| `-d, --duration` | Animation duration in seconds (default: 10.0) | `-d 15` |
| `-f, --fps` | Frame rate in Hz (default: 6) | `-f 10` |
| `-p, --prompt` | Path to Ollama prompt template (default: prompt.txt) | `-p custom_prompt.txt` |
| `--idea` | Custom animation idea (single-shot mode) | `--idea "bouncing balls"` |
| `--preview` | Show console output alongside display | `--preview` |
| `-v, --verbose` | Verbose logging with validation details | `-v` |
| `--version` | Show version and exit | `--version` |

#### Environment Variables

| Variable | Description | Default |
| :-- | :-- | :-- |
| `VFD_DEVICE` | Display device path or `"simulator"` | `/dev/ttyUSB0` |
| `OLLAMA_API_BASE` | Ollama API endpoint | `http://localhost:11434` |
| `OLLAMA_MODEL` | Model to use for generation | `qwen2.5:3b` |
| `ANIMATION_DURATION` | Default animation duration | `10.0` |

### Testing Without Hardware

Set `VFD_DEVICE=simulator` to run without a physical display:

```


# Simulator only (no console output)

VFD_DEVICE=simulator ./vfd_agent.py --idea "test animation"

# Simulator with console preview

VFD_DEVICE=simulator ./vfd_agent.py --preview --idea "test animation"

# Continuous mode with simulator

VFD_DEVICE=simulator ./vfd_agent.py --preview

```

The `--preview` flag shows console output and works with both hardware and simulator modes.

## Interactive Development with Marimo

For a powerful interactive development experience, this project includes several Marimo notebooks. These notebooks provide a web-based UI for iterating on AI prompts, analyzing results, and directly controlling the VFD hardware.

### Running the Notebooks

1.  **Install Dependencies:** Make sure you have installed the optional Marimo dependencies as described in the `Install` section.
2.  **Start the Server:** Run the following command from the root of the project:
    ```bash
    marimo edit notebooks/
    ```
3.  **Open in Browser:** Open the URL provided by the command (usually `http://localhost:2718`) in your web browser. This will open the Marimo editor, where you can see and run the project's notebooks.

### Available Notebooks

*   **`agent_studio.py`**: The primary tool for AI development. Use it to edit prompts, generate animation code, validate it, and preview the results frame-by-frame in a simulator. This is the recommended workflow for creating new animations.
*   **`vfd_playground.py`**: A simple interface for direct hardware control. Use it to test the VFD connection or display simple text.
*   **`metrics_dashboard.py`**: A dashboard for visualizing project metrics, such as generation success rates, animation complexity, and more.

## Frame Capture Inspector (`inspect_frame_captures.sh`)

`inspect_frame_captures.sh` is a diagnostic tool for examining and analyzing frame captures generated by the VFD animation system. It provides visibility into what animations actually display on screen and validates that they meet quality standards.

### Quick Start

```


# Make script executable

chmod +x inspect_frame_captures.sh

# Show summary of all captured frames

./inspect_frame_captures.sh

# Show latest capture with full details

./inspect_frame_captures.sh --latest

# Inspect specific capture

./inspect_frame_captures.sh anim_1762307195_1789.jsonl

# Export to readable text file

./inspect_frame_captures.sh --export-text anim_1762307195_1789.jsonl output.txt

```

### Advanced Usage

For detailed troubleshooting, custom statistics, and integration techniques, see the inline documentation in `inspect_frame_captures.sh`.

## VFD Animation Renderer (`to_video.py`)

Convert VFD animations to MP4 videos. Auto-detects `.py` (executes code) or `.jsonl` (uses captured frames).

### Setup

```

chmod +x to_video.py

```

**Dependencies:**
*   FFmpeg: `sudo apt-get install ffmpeg`
*   Python 3.7+
*   Pillow: `pip install Pillow`
*   cd5220 module (auto-installed via requirements.txt)

### Usage

#### Render all animations in directory

```

./to_video.py generated_animations/

```

Processes all `.py` and `.jsonl` files. Skips existing videos unless `--force` used.

#### Render from captured frames (fast)

```

./to_video.py generated_animations/frame_captures/

```

Uses JSONL files created by `vfd_agent.py --preview` during playback.

#### Render specific file

```

./to_video.py generated_animations/anim_1234567890.py         \# execute code
./to_video.py frame_captures/anim_1234567890_playback.jsonl   \# use captured frames

```

#### Force re-render with custom settings

```

./to_video.py generated_animations/ --force -d 15 --fps 8

```

### Output

- **Location:** `generated_animations/videos/*.mp4`
- **Format:** 640×200px, H.264, yuv420p
- **Frame rate:** 6 FPS (default, configurable with `--fps`)
- **Appearance:** Cyan monospace text on black with 40px side margins

## Documentation

For detailed information on architecture, troubleshooting, and advanced usage, see inline documentation in each script.
