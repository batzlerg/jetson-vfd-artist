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
    output = None
    if code:
        # Display generated code
        output = mo.md(f"### Generated Code\n```python\n{code}\n```")
    elif raw_response:
        # Display error and raw response on failure
        output = mo.md(
            f"""
            ### Generation Failed
            **Error:** `{gen_error}`
            <details>
            <summary>Raw LLM Response</summary>
            <pre><code>{raw_response}</code></pre>
            </details>
            """
        )
    output


@app.cell
def __(DiffAnimator, code, func_name, mo, random, validate_runtime, validate_syntax):
    validation_status = None
    frame_capture = None
    callable_func = None

    if code:
        header = mo.md("### Validation")
        syntax_ok, syntax_err = validate_syntax(code)
        syntax_status = mo.md(f"**Syntax:** {'✓ OK' if syntax_ok else f'✗ FAILED: `{syntax_err}`'}")

        if syntax_ok:
            try:
                namespace = {
                    "DiffAnimator": DiffAnimator,
                    "random": random,
                    "math": __import__("math"),
                }
                exec(code, namespace)
                callable_func = namespace.get(func_name)
                compilation_status = mo.md(f"**Compilation:** {'✓ OK' if callable_func else '✗ FAILED: Function not found'}")
            except Exception as e:
                callable_func = None
                compilation_status = mo.md(f"**Compilation:** ✗ FAILED: `{e}`")

            if callable_func:
                runtime_ok, runtime_err, captured_frames = validate_runtime(
                    callable_func, func_name
                )
                if runtime_ok:
                    runtime_status = mo.md(f"**Runtime:** ✓ OK")
                    frame_capture = captured_frames
                else:
                    runtime_status = mo.md(f"**Runtime:** ✗ FAILED: `{runtime_err}`")
                validation_status = mo.vstack([header, syntax_status, compilation_status, runtime_status])
            else:
                 validation_status = mo.vstack([header, syntax_status, compilation_status])
        else:
            validation_status = mo.vstack([header, syntax_status])

    (validation_status, frame_capture, callable_func)


@app.cell
def __(frame_capture, mo):
    preview_output = None
    if frame_capture:
        header = mo.md("### Animation Preview")
        frames = frame_capture.get_frames()
        if not frames:
            preview_output = mo.vstack([header, mo.md("**Warning:** Animation ran but produced no frames.")])
        else:
            md_frames = [f"```\n{f['line1']}\n{f['line2']}\n```" for f in frames]
            frame_slider = mo.ui.slider(
                0, max(0, len(md_frames) - 1), label=f"Frame ({len(md_frames)} total)"
            )
            # A check to prevent IndexError if md_frames is empty
            selected_frame = mo.md(md_frames[frame_slider.value]) if md_frames else mo.md("")
            preview_output = mo.vstack([header, frame_slider, selected_frame])
    preview_output
