import marimo as mo
import pathlib
import random
import time
import sys

# Add current dir to path to import local modules
sys.path.append(str(pathlib.Path.cwd()))

from vfd_agent import generate_code, validate_syntax, validate_runtime
from cd5220 import CD5220, DiffAnimator

__generated_with = "0.9.0"
app = mo.App()


@app.cell
def __(mo):
    mo.md("# VFD Agent Studio")
    mo.md(
        "Interactive workbench for iterating on AI agent prompts and animation ideas."
    )
    return


@app.cell
def __(mo):
    prompt_file = pathlib.Path("prompt.txt")
    prompt_text = mo.ui.text_area(
        value=prompt_file.read_text(),
        label="Generation Prompt",
        full_width=True,
    )
    idea = mo.ui.text(value="a bouncing ball", label="Animation Idea")
    generate_button = mo.ui.button(label="✨ Generate Animation")
    return idea, generate_button, prompt_text


@app.cell
def __(generate_button, idea, mo, prompt_text):
    mo.md(f"**Status:** {mo.loading('pulse') if generate_button.loading else 'Idle'}")
    if generate_button.value > 0:
        # This block is reactive to the button click
        output_dir = pathlib.Path("generated_animations")
        output_dir.mkdir(exist_ok=True)
        func_name = f"anim_{int(time.time())}_{random.randint(1000,9999)}"

        code, gen_error, raw_response = generate_code(
            prompt=prompt_text.value,
            desc=idea.value,
            func_name=func_name,
            attempt=1,
            prev_errors=[],
            output_dir=output_dir,
        )
    else:
        # Default state before first click
        code, gen_error, raw_response, func_name = None, None, None, None

    return code, func_name, gen_error, raw_response


@app.cell
def __(code, gen_error, mo, raw_response):
    if code:
        # Display generated code
        return mo.md(f"### Generated Code\n```python\n{code}\n```")
    elif raw_response:
        # Display error and raw response on failure
        return mo.md(
            f"""
            ### Generation Failed
            **Error:** `{gen_error}`
            <details>
            <summary>Raw LLM Response</summary>
            <pre><code>{raw_response}</code></pre>
            </details>
            """
        )
    return


@app.cell
def __(DiffAnimator, code, func_name, mo, random, validate_runtime, validate_syntax):
    if not code:
        return

    # --- Validation Step ---
    mo.md("### Validation")
    syntax_ok, syntax_err = validate_syntax(code)
    if not syntax_ok:
        validation_status = mo.md(f"**Syntax:** ✗ FAILED: `{syntax_err}`")
        return validation_status, None, None

    syntax_status = mo.md(f"**Syntax:** ✓ OK")

    try:
        namespace = {
            "DiffAnimator": DiffAnimator,
            "random": random,
            "math": __import__("math"),
        }
        exec(code, namespace)
        callable_func = namespace[func_name]
    except Exception as e:
        compilation_status = mo.md(f"**Compilation:** ✗ FAILED: `{e}`")
        return mo.vstack([syntax_status, compilation_status]), None, None

    compilation_status = mo.md(f"**Compilation:** ✓ OK")

    runtime_ok, runtime_err, frame_capture = validate_runtime(
        callable_func, func_name
    )
    if not runtime_ok:
        runtime_status = mo.md(f"**Runtime:** ✗ FAILED: `{runtime_err}`")
    else:
        runtime_status = mo.md(f"**Runtime:** ✓ OK")

    validation_status = mo.vstack(
        [syntax_status, compilation_status, runtime_status]
    )

    return validation_status, frame_capture, callable_func


@app.cell
def __(frame_capture, mo):
    if not frame_capture:
        return

    # --- Preview Step ---
    mo.md("### Animation Preview")
    frames = frame_capture.get_frames()
    if not frames:
        return mo.md("**Warning:** Animation ran but produced no frames.")

    md_frames = [f"```\n{f['line1']}\n{f['line2']}\n```" for f in frames]

    frame_slider = mo.ui.slider(
        0, len(md_frames) - 1, label=f"Frame ({len(md_frames)} total)"
    )

    return mo.vstack([frame_slider, mo.md(md_frames[frame_slider.value])])
