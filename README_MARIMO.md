# Using Marimo Notebooks for VFD Artist

This document provides instructions on how to use the Marimo notebooks for interactive development and analysis of the `jetson-vfd-artist` project.

## Installation

1.  Install the required dependencies:
    ```bash
    pip install -r requirements-marimo.txt
    ```

## Running the Notebooks

1.  Start the Marimo server from the root of the repository:
    ```bash
    marimo run notebooks/
    ```
2.  Open the provided URL in your web browser to see the list of available notebooks.

## Available Notebooks

### `agent_studio.py`

This is the primary notebook for AI agent development. It provides an interactive environment for iterating on prompts and animation ideas. You can use it to:

*   Load and edit the generation prompt in real-time.
*   Provide a custom animation idea.
*   Trigger the AI to generate animation code.
*   View the generated code and validate it for syntax and runtime errors.
*   Preview the resulting animation frame-by-frame.

### `vfd_playground.py`

This notebook provides a simple, direct interface for controlling the VFD display. You can use it to:

*   Connect to a VFD display or use the simulator.
*   Send text to the display's two lines in real-time.

### `metrics_dashboard.py`

This notebook provides an interactive dashboard for visualizing data from `analyze.py` and `code_metrics.py`. You can use it to:

*   View a summary of animation generations.
*   Analyze the performance of different animation patterns.
*   View recent generation failures.
*   Track the success rate trend.
*   View bookmarked and downvoted animations.
