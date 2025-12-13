# Antigravity Pipeline for Universal LPC Character Generator

A Python-based automation pipeline for manipulating and extending pixel art assets from the Universal LPC Spritesheet Character Generator.

## Overview

This project provides tools to:
- **Recolor** existing sprite sheets with custom palette swaps
- **Generate 8-directional views** using procedural transformations
- **Auto-inject** new assets into the web application's JSON definitions

Assets generated here are designed for use in an Unreal Engine HD-2D Soulslike game using a Paper Doll socket system.

## Project Structure

```
lpc/
├── forge_scripts/         # Python manipulation scripts
│   ├── antigravity.py    # Main sprite manipulation engine
│   └── update_definitions.py  # JSON auto-injector
├── lpc_generator/        # Cloned LPC generator (not tracked)
├── venv/                 # Python virtual environment
└── start_server.py       # Local development server
```

## Quick Start

1. **Setup environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install Pillow
   ```

2. **Clone LPC Generator:**
   ```bash
   git clone https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator lpc_generator
   ```

3. **Start local server:**
   ```bash
   python start_server.py
   ```

## Source

Based on: [Universal LPC Spritesheet Character Generator](https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator)
