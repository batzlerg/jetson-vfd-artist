import marimo as mo

__generated_with = "0.9.0"
app = mo.App()


@app.cell
def __():
    import marimo as mo
    try:
        from cd5220 import CD5220, DiffAnimator
    except ImportError:
        mo.md("Could not import `cd5220`. Please install it with `pip install git+https://github.com/batzlerg/cd5220.git@jetson-ai-artist`")
        raise
    return CD5220, DiffAnimator, mo


@app.cell
def __(mo):
    # Interactive display connection
    port = mo.ui.text(value="/dev/ttyUSB0", label="Serial Port")
    use_simulator = mo.ui.switch(label="Use Simulator")
    return port, use_simulator


@app.cell
def __(CD5220, DiffAnimator, use_simulator, port, mo):
    if use_simulator.value:
        display = CD5220.create_simulator_only(render_console=True)
        animator = DiffAnimator(display)
        mo.md("VFD Simulator Initialized")
    else:
        try:
            # Baudrate is fixed at 9600
            display = CD5220(port.value, 9600)
            animator = DiffAnimator(display)
            display.clear()
            mo.md(f"Connected to VFD at `{port.value}`")
        except Exception as e:
            animator = None
            mo.md(f"**Error connecting to display:** {e}")

    return display, animator


@app.cell
def __(mo):
    # Live text editor for display content
    line1 = mo.ui.text(value="Hello Marimo!", label="Line 1")
    line2 = mo.ui.text(value="From VFD Artist", label="Line 2")
    return line1, line2

@app.cell
def __(animator, line1, line2):
    if animator:
        animator.write_frame(line1.value.ljust(20)[:20], line2.value.ljust(20)[:20])
    return
