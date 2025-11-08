#!/usr/bin/env python3
"""
VFD Animation to MP4 Renderer
Renders cd5220 animations to video files
Auto-detects .py (execute) vs .jsonl (load frames from previous execution)
"""

import subprocess
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random
import math
import argparse

# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_FPS = 6
DEFAULT_DURATION = 10.0
CANVAS_WIDTH = 640
CANVAS_HEIGHT = 200
LEFT_MARGIN = 40
TOP_MARGIN = 45
CHAR_AREA_WIDTH = CANVAS_WIDTH - (LEFT_MARGIN * 2)
CHAR_WIDTH = CHAR_AREA_WIDTH / 20
LINE_SPACING = 70
FONT_SIZE = 28
FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'

# ============================================================================
# FRAME LOADING
# ============================================================================


def load_frames_from_jsonl(jsonl_path: Path):
    """Load frames from existing JSONL capture file"""
    with open(jsonl_path) as f:
        first_line = f.readline()
        meta = json.loads(first_line)

        if '_meta' not in meta:
            raise ValueError(f"Invalid JSONL: {jsonl_path}")

        frames = []
        for line in f:
            frame_data = json.loads(line)
            frames.append((frame_data['line1'], frame_data['line2']))

        return frames, meta['_meta']


def execute_animation(code: str, func_name: str, duration: float, fps: int):
    """Execute animation and capture frames using FrameCapture"""
    from cd5220 import CD5220, DiffAnimator
    from frame_capture import FrameCapture

    if code.startswith('ℹ') or code.startswith('✓') or code.startswith('✗'):
        raise ValueError("Corrupt file (emoji prefix)")

    code = code.replace('``````', '')

    display = CD5220.create_simulator_only(debug=False, render_console=False)
    animator = DiffAnimator(display, frame_rate=fps)
    capture = FrameCapture(animator, animation_id=func_name)

    namespace = {'DiffAnimator': DiffAnimator, 'random': random, 'math': math}
    exec(code, namespace)

    if func_name not in namespace:
        raise ValueError(f"Function {func_name} not found")

    anim_func = namespace[func_name]
    anim_func(capture.animator, duration=duration)

    return capture.get_frames()

# ============================================================================
# VIDEO RENDERING
# ============================================================================


def render_frames_to_video(frames, output_path: Path, fps: int):
    """Render frames to MP4 using FFmpeg pipe"""

    if not frames:
        raise ValueError("No frames to render")

    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'rgb24',
        '-s', f'{CANVAS_WIDTH}x{CANVAS_HEIGHT}',
        '-r', str(fps),
        '-i', '-',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-crf', '18',
        '-loglevel', 'error',
        str(output_path)
    ]

    proc = subprocess.Popen(
        ffmpeg_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    try:
        for line1, line2 in frames:
            img = Image.new(
                'RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), color='black')
            draw = ImageDraw.Draw(img)

            for i, char in enumerate(line1):
                x = int(LEFT_MARGIN + (i * CHAR_WIDTH))
                draw.text((x, TOP_MARGIN), char, fill='#00FFFF', font=font)

            for i, char in enumerate(line2):
                x = int(LEFT_MARGIN + (i * CHAR_WIDTH))
                draw.text((x, TOP_MARGIN + LINE_SPACING),
                          char, fill='#00FFFF', font=font)

            try:
                proc.stdin.write(img.tobytes())
            except BrokenPipeError:
                break

        try:
            proc.stdin.close()
        except BaseException:
            pass

        proc.wait(timeout=30)

        if proc.returncode != 0:
            stderr = proc.stderr.read().decode() if proc.stderr else ''
            raise RuntimeError(
                f"FFmpeg failed (code {proc.returncode}): {stderr}")

    except Exception as e:
        try:
            proc.kill()
        except BaseException:
            pass
        raise

# ============================================================================
# MAIN
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description='Render VFD animations to MP4')
    parser.add_argument(
        '-d',
        '--duration',
        type=float,
        default=DEFAULT_DURATION)
    parser.add_argument('--fps', type=int, default=DEFAULT_FPS)
    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-render existing videos')
    parser.add_argument(
        'files',
        nargs='*',
        help='Animation files (.py or .jsonl) - auto-detects type')

    args = parser.parse_args()

    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ ffmpeg not found. Install: sudo apt-get install ffmpeg")
        sys.exit(1)

    if not Path(FONT_PATH).exists():
        print(f"✗ Font not found: {FONT_PATH}")
        sys.exit(1)

    print(f"ℹ Using font: {FONT_PATH}")
    print(
        f"ℹ Canvas: {CANVAS_WIDTH}x{CANVAS_HEIGHT}px with {LEFT_MARGIN}px side margins")

    gen_dir = Path('generated_animations')
    if not gen_dir.exists():
        print(f"✗ Directory not found: {gen_dir}")
        sys.exit(1)

    videos_dir = gen_dir / 'videos'
    videos_dir.mkdir(exist_ok=True)

    # Auto-detect source files
    if args.files:
        source_files = []
        for filename in args.files:
            # Check multiple locations
            candidates = [
                Path(filename),
                gen_dir / filename,
                gen_dir / 'frame_captures' / filename,
            ]
            for candidate in candidates:
                if candidate.exists():
                    source_files.append(candidate)
                    break
            else:
                print(f"✗ File not found: {filename}")
                sys.exit(1)
    else:
        # Default: all .py files
        source_files = sorted(gen_dir.glob('anim_*.py'))

    print(f"ℹ Found {len(source_files)} files to render")

    success = 0
    skipped = 0
    failed = 0

    for source_file in source_files:
        # Auto-detect file type by extension
        is_jsonl = source_file.suffix == '.jsonl'

        if is_jsonl:
            # JSONL mode: load pre-captured frames
            anim_id = source_file.stem.replace(
                '_validation',
                '').replace(
                '_playback',
                '').replace(
                '_replay',
                '')
            video_path = videos_dir / f"{anim_id}.mp4"

            if video_path.exists() and not args.force:
                skipped += 1
                continue

            print(f"ℹ Rendering {anim_id} from JSONL...")

            try:
                frames, metadata = load_frames_from_jsonl(source_file)

                if not frames:
                    print(f"✗ No frames in JSONL")
                    failed += 1
                    continue

                # Calculate FPS from metadata if available
                fps = args.fps
                if 'total_frames' in metadata and 'duration' in metadata:
                    actual_duration = metadata['duration']
                    if actual_duration > 0:
                        calculated_fps = metadata['total_frames'] / \
                            actual_duration
                        if calculated_fps > 1:
                            fps = int(calculated_fps)

                render_frames_to_video(frames, video_path, fps)
                print(
                    f"✓ Saved {video_path} ({len(frames)} frames @ {fps}fps)")
                success += 1

            except Exception as e:
                print(f"✗ Failed: {e}")
                failed += 1

        else:
            # Python mode: execute animation code
            func_name = source_file.stem
            video_path = videos_dir / f"{func_name}.mp4"

            if video_path.exists() and not args.force:
                skipped += 1
                continue

            print(f"ℹ Rendering {func_name} by executing...")

            try:
                code = source_file.read_text()
                frames = execute_animation(
                    code, func_name, args.duration, args.fps)

                if not frames:
                    print(f"✗ No frames captured")
                    failed += 1
                    continue

                render_frames_to_video(frames, video_path, args.fps)
                print(f"✓ Saved {video_path} ({len(frames)} frames)")
                success += 1

            except Exception as e:
                print(f"✗ Failed: {e}")
                failed += 1

    print(
        f"\n✓ Success: {success} | ⊘ Skipped: {skipped} | ✗ Failed: {failed}")


if __name__ == '__main__':
    main()
