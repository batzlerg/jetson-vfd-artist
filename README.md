# Jetson VFD Artist

AI-powered animation generator for CD5220 VFD displays.

## Install

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Continuous mode
./vfd_agent.py

# Single animation
./vfd_agent.py --idea "bouncing balls"

# Simulator (no hardware)
VFD_DEVICE=simulator ./vfd_agent.py --preview
```

See `README_VFD_AGENT.md` for full documentation.
