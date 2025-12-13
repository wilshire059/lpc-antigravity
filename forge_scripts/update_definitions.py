#!/usr/bin/env python3
"""
JSON Injector - Auto-import new assets into LPC Generator definitions
Scans sprite sheets and automatically adds missing entries to JSON definitions.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
import argparse

# Default paths
DEFAULT_SPRITESHEET_DIR = "lpc_generator/spritesheets"
DEFAULT_DEFINITIONS_DIR = "lpc_generator/sheet_definitions"
BACKUP_DIR = "backups/json_definitions"


def create_backup(file_path):
    """
    Create a timestamped backup of a JSON file before modification.

    Args:
        file_path: Path to the file to backup

    Returns:
        Path to backup file
    """
    backup_dir = Path(BACKUP_DIR)
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{Path(file_path).stem}_{timestamp}.json"
    backup_path = backup_dir / backup_name

    shutil.copy2(file_path, backup_path)
    print(f"  [BACKUP] Created: {backup_path}")

    return backup_path


def load_json(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def save_json(file_path, data):
    """Save data to a JSON file with pretty formatting."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Updated: {file_path}")
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False


def scan_spritesheet_directory(spritesheet_dir):
    """
    Scan the spritesheet directory and return a structured inventory.

    Returns:
        dict: {
            'category/item_name': {
                'male': 'path/to/male.png',
                'female': 'path/to/female.png',
                'universal': 'path/to/universal.png'
            }
        }
    """
    spritesheet_path = Path(spritesheet_dir)

    if not spritesheet_path.exists():
        print(f"Error: Spritesheet directory '{spritesheet_dir}' not found.")
        return {}

    inventory = {}

    # Walk through the spritesheet directory
    # Expected structure: spritesheets/[category]/[item_name]/[gender].png
    for category_dir in spritesheet_path.iterdir():
        if not category_dir.is_dir():
            continue

        category = category_dir.name

        # Skip special directories
        if category.startswith('.') or category.startswith('_'):
            continue

        # Look for item folders within category
        for item_dir in category_dir.iterdir():
            if not item_dir.is_dir():
                continue

            item_name = item_dir.name
            key = f"{category}/{item_name}"

            if key not in inventory:
                inventory[key] = {}

            # Look for gender-specific or universal sprites
            for sprite_file in item_dir.glob("*.png"):
                gender = sprite_file.stem.lower()  # 'male', 'female', 'universal'

                # Determine gender
                if gender in ['male', 'female', 'universal']:
                    relative_path = sprite_file.relative_to(spritesheet_path.parent)
                    inventory[key][gender] = str(relative_path).replace('\\', '/')

    return inventory


def scan_definitions(definitions_dir):
    """
    Scan existing JSON definitions to see what's already registered.

    Returns:
        dict: {
            'category': {
                'item_name_gender': True
            }
        }
    """
    definitions_path = Path(definitions_dir)

    if not definitions_path.exists():
        print(f"Error: Definitions directory '{definitions_dir}' not found.")
        return {}

    registered = {}

    # Scan all JSON files in definitions directory
    for json_file in definitions_path.glob("*.json"):
        category = json_file.stem

        data = load_json(json_file)
        if data is None:
            continue

        registered[category] = {}

        # Parse existing entries
        for entry in data:
            if isinstance(entry, dict) and 'name' in entry and 'file' in entry:
                # Create a unique key from file path
                file_path = entry.get('file', '')
                registered[category][file_path] = True

    return registered


def generate_display_name(item_folder_name):
    """
    Convert a folder name to a human-readable display name.
    Example: 'chainmail_green' -> 'Chainmail Green'
    """
    return item_folder_name.replace('_', ' ').title()


def inject_missing_entries(spritesheet_dir, definitions_dir, dry_run=False):
    """
    Scan for missing entries and inject them into the appropriate JSON files.

    Args:
        spritesheet_dir: Path to spritesheets directory
        definitions_dir: Path to sheet_definitions directory
        dry_run: If True, only print what would be done without making changes
    """
    print("\n[SCAN] Scanning sprite sheets and definitions...")

    # Scan what we have
    inventory = scan_spritesheet_directory(spritesheet_dir)
    registered = scan_definitions(definitions_dir)

    if not inventory:
        print("No sprites found to process.")
        return

    print(f"   Found {len(inventory)} item(s) in spritesheet directory")

    # Find missing entries
    missing_entries = {}

    for key, genders in inventory.items():
        category, item_name = key.split('/', 1)

        if category not in registered:
            registered[category] = {}

        for gender, file_path in genders.items():
            # Check if this file path is already registered
            if file_path not in registered[category]:
                if category not in missing_entries:
                    missing_entries[category] = []

                missing_entries[category].append({
                    'name': generate_display_name(item_name),
                    'file': file_path,
                    'layer': category,
                    'gender': gender
                })

    if not missing_entries:
        print("\n[OK] All sprites are already registered in definitions!")
        return

    # Report what will be added
    print(f"\n[FOUND] {sum(len(v) for v in missing_entries.values())} missing entry/entries:")
    for category, entries in missing_entries.items():
        print(f"\n   {category}: {len(entries)} new entry/entries")
        for entry in entries:
            print(f"      - {entry['name']} ({entry['gender']})")

    if dry_run:
        print("\n[DRY RUN] No changes made.")
        return

    # Inject entries
    print("\n[INJECT] Adding missing entries to JSON definitions...")

    for category, entries in missing_entries.items():
        json_file = Path(definitions_dir) / f"{category}.json"

        # Load existing data
        if json_file.exists():
            create_backup(json_file)
            data = load_json(json_file)
            if data is None:
                print(f"   [WARNING] Skipping {category} due to load error")
                continue
        else:
            print(f"   [INFO] Creating new definition file: {json_file}")
            data = []

        # Append new entries
        data.extend(entries)

        # Save
        save_json(json_file, data)

    print("\n[SUCCESS] JSON injection complete!")


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Auto-inject new sprites into LPC Generator JSON definitions'
    )

    parser.add_argument('--spritesheets', default=DEFAULT_SPRITESHEET_DIR,
                       help='Path to spritesheets directory')
    parser.add_argument('--definitions', default=DEFAULT_DEFINITIONS_DIR,
                       help='Path to sheet_definitions directory')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without modifying files')

    args = parser.parse_args()

    inject_missing_entries(args.spritesheets, args.definitions, args.dry_run)


if __name__ == "__main__":
    main()
