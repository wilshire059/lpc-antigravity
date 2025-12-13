# Antigravity Pipeline - Execution Guide

Complete guide for running the LPC Character Generator manipulation pipeline.

## Quick Start

### 1. Activate Virtual Environment

**Windows (Git Bash):**
```bash
source venv/Scripts/activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Start the Local Server

```bash
python start_server.py
```

Then visit: **http://localhost:8000/**

To stop the server, press `Ctrl+C`.

---

## Antigravity.py - Core Manipulation Engine

### Recolor Operations

#### Example 1: Create Green Plate Armor

Convert gray plate armor to green:

```bash
python forge_scripts/antigravity.py recolor \
  lpc_generator/spritesheets/torso/plate \
  lpc_generator/spritesheets/torso/plate_green \
  --old-colors "128,128,128" "96,96,96" "160,160,160" \
  --new-color "0,200,0"
```

#### Example 2: Create Red Leather Armor

```bash
python forge_scripts/antigravity.py recolor \
  lpc_generator/spritesheets/torso/leather \
  lpc_generator/spritesheets/torso/leather_red \
  --old-colors "139,69,19" \
  --new-color "200,0,0"
```

#### Recolor Syntax

```bash
python forge_scripts/antigravity.py recolor SOURCE OUTPUT \
  --old-colors "R,G,B" ["R,G,B" ...] \
  --new-color "R,G,B"
```

**Parameters:**
- `SOURCE`: Path to source sprite folder
- `OUTPUT`: Path to output folder (will be created)
- `--old-colors`: One or more RGB colors to replace (space-separated)
- `--new-color`: The replacement RGB color

---

### Diagonal View Generation

#### Example 1: Generate NE Diagonal of Base Body

```bash
python forge_scripts/antigravity.py diagonal \
  lpc_generator/spritesheets/body/male/light.png \
  lpc_generator/spritesheets/body/male/light_ne.png \
  --direction ne
```

#### Example 2: Batch Generate Diagonals for Entire Folder

```bash
python forge_scripts/antigravity.py diagonal \
  lpc_generator/spritesheets/body/male \
  lpc_generator/spritesheets/body/male_diagonals \
  --direction ne
```

#### Diagonal Syntax

```bash
python forge_scripts/antigravity.py diagonal SOURCE OUTPUT \
  --direction [ne|nw|se|sw]
```

**Parameters:**
- `SOURCE`: Single file or folder path
- `OUTPUT`: Output file or folder path
- `--direction`: Diagonal direction (ne=northeast, nw=northwest, se=southeast, sw=southwest)

**Tuning Parameters:**

To adjust the diagonal transformation quality, edit `forge_scripts/antigravity.py`:

```python
DIAGONAL_WIDTH_SQUASH = 0.85  # Adjust width compression (0.0-1.0)
DIAGONAL_SHEAR_AMOUNT = 0.1   # Adjust slant amount (0.0-0.3)
```

---

## Update Definitions - JSON Auto-Injector

### Scan and Inject New Sprites

After creating new sprite variants, automatically register them in the web app:

#### Dry Run (Preview Only)

```bash
python forge_scripts/update_definitions.py --dry-run
```

#### Execute Injection

```bash
python forge_scripts/update_definitions.py
```

#### Custom Paths

```bash
python forge_scripts/update_definitions.py \
  --spritesheets lpc_generator/spritesheets \
  --definitions lpc_generator/sheet_definitions
```

**What it does:**
- Scans `lpc_generator/spritesheets/` for new folders
- Compares against existing `sheet_definitions/*.json` files
- Auto-generates JSON entries for missing items
- Creates timestamped backups before modifying files

**Backups Location:** `backups/json_definitions/`

---

## Complete Workflow Example

### Create and Deploy a New Armor Variant

**Step 1:** Create a recolored variant
```bash
python forge_scripts/antigravity.py recolor \
  lpc_generator/spritesheets/torso/chainmail \
  lpc_generator/spritesheets/torso/chainmail_cursed \
  --old-colors "192,192,192" \
  --new-color "128,0,128"
```

**Step 2:** Inject into JSON definitions
```bash
python forge_scripts/update_definitions.py
```

**Step 3:** Start the server and test
```bash
python start_server.py
```

**Step 4:** Visit http://localhost:8000/ and look for "Chainmail Cursed" in the torso layer!

---

## Advanced: Batch Operations

### Create Multiple Color Variants

```bash
# Green variant
python forge_scripts/antigravity.py recolor \
  lpc_generator/spritesheets/torso/plate \
  lpc_generator/spritesheets/torso/plate_green \
  --old-colors "128,128,128" \
  --new-color "0,200,0"

# Blue variant
python forge_scripts/antigravity.py recolor \
  lpc_generator/spritesheets/torso/plate \
  lpc_generator/spritesheets/torso/plate_blue \
  --old-colors "128,128,128" \
  --new-color "0,100,255"

# Red variant
python forge_scripts/antigravity.py recolor \
  lpc_generator/spritesheets/torso/plate \
  lpc_generator/spritesheets/torso/plate_red \
  --old-colors "128,128,128" \
  --new-color "255,50,50"

# Inject all at once
python forge_scripts/update_definitions.py
```

---

## Troubleshooting

### "Module 'PIL' not found"

Make sure you've activated the virtual environment:
```bash
source venv/Scripts/activate  # Windows Git Bash
pip install Pillow
```

### "Source folder does not exist"

Check that the `lpc_generator` folder exists and contains the spritesheets:
```bash
ls lpc_generator/spritesheets/
```

### JSON injection not working

Run in dry-run mode to see what would be added:
```bash
python forge_scripts/update_definitions.py --dry-run
```

### Server won't start

Make sure port 8000 is not already in use:
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

---

## Color Picking Tips

To find RGB values for recoloring:
1. Open the original sprite in an image editor (GIMP, Photoshop, etc.)
2. Use the color picker tool on the area you want to recolor
3. Note the RGB values (each 0-255)
4. Use multiple `--old-colors` for gradients or shading

**Example:** Armor with 3 shades of gray:
```bash
--old-colors "96,96,96" "128,128,128" "160,160,160"
```

---

## Project Structure Reference

```
lpc/
├── lpc_generator/          # Cloned LPC generator (not tracked in git)
│   ├── spritesheets/       # Source sprite assets
│   └── sheet_definitions/  # JSON configuration files
├── forge_scripts/          # Your manipulation tools
│   ├── antigravity.py     # Main sprite engine
│   └── update_definitions.py  # JSON injector
├── venv/                   # Python virtual environment
├── backups/                # JSON backups (auto-generated)
├── start_server.py         # Local dev server
└── EXECUTION_GUIDE.md      # This file
```

---

## Next Steps

- Experiment with different color combinations
- Try generating diagonal views for animation frames
- Explore the LPC generator's spritesheet structure
- Build custom character presets using your new assets

**For Unreal Engine integration:** Export generated sprites and configure them in your Paper Doll socket system.
