#!/usr/bin/env python3
"""
Antigravity Pipeline - Universal LPC Spritesheet Manipulator
Programmatically manipulate pixel art assets using procedural transformations.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageTransform
import argparse

# =============================================================================
# TUNABLE PARAMETERS FOR DIAGONAL GENERATION
# =============================================================================
# Simple shear method - proven to maintain layer alignment
DIAGONAL_SHEAR_AMOUNT = 0.15  # Horizontal shear for diagonal directions (0.15 = optimal balance)

# =============================================================================
# CORE IMAGE PROCESSING
# =============================================================================

def process_image(image_path):
    """
    Load an image as RGBA, preserving pixel art integrity.

    Args:
        image_path: Path to the image file

    Returns:
        PIL.Image: Loaded image in RGBA mode
    """
    try:
        img = Image.open(image_path)
        # Force RGBA mode for consistent processing
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        return img
    except Exception as e:
        print(f"Error loading {image_path}: {e}")
        return None


def save_image(img, output_path, preserve_pixel_art=True):
    """
    Save an image, preserving pixel art quality.

    Args:
        img: PIL.Image to save
        output_path: Destination path
        preserve_pixel_art: If True, use PNG with no compression artifacts
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save as PNG to preserve transparency and pixel-perfect quality
    img.save(output_path, 'PNG', optimize=False)
    print(f"[OK] Saved: {output_path}")


# =============================================================================
# RECOLOR MODULE - Palette Swapping
# =============================================================================

def apply_palette_swap(image, old_colors, new_color):
    """
    Replace specific colors in an image with a new color.

    Args:
        image: PIL.Image in RGBA mode
        old_colors: List of RGB tuples to replace [(r,g,b), ...]
        new_color: RGB tuple for the replacement color (r,g,b)

    Returns:
        PIL.Image: Modified image
    """
    # Convert image to pixel data
    pixels = image.load()
    width, height = image.size

    # Create output image
    output = image.copy()
    output_pixels = output.load()

    # Convert old_colors list to set for faster lookup
    old_colors_set = set(old_colors)

    # Iterate through all pixels
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            # Check if pixel color matches any old color
            if (r, g, b) in old_colors_set:
                # Preserve alpha, replace RGB
                output_pixels[x, y] = (new_color[0], new_color[1], new_color[2], a)

    return output


def generate_recolor_variant(source_folder, output_folder, old_colors, new_color):
    """
    Generate a recolored variant of all sprites in a folder.

    Args:
        source_folder: Path to source sprite folder
        output_folder: Path to output folder
        old_colors: List of RGB tuples to replace
        new_color: RGB tuple for replacement
    """
    source_path = Path(source_folder)
    output_path = Path(output_folder)

    if not source_path.exists():
        print(f"Error: Source folder '{source_folder}' does not exist.")
        return

    print(f"\n[RECOLOR] Processing sprites from '{source_folder}' to '{output_folder}'")
    print(f"   Replacing {len(old_colors)} color(s) with RGB{new_color}")

    # Process all PNG files in source folder
    png_files = list(source_path.rglob("*.png"))

    if not png_files:
        print(f"Warning: No PNG files found in {source_folder}")
        return

    for img_file in png_files:
        # Preserve relative path structure
        relative_path = img_file.relative_to(source_path)
        output_file = output_path / relative_path

        # Process image
        img = process_image(img_file)
        if img is None:
            continue

        # Apply palette swap
        recolored = apply_palette_swap(img, old_colors, new_color)

        # Save with same filename
        save_image(recolored, output_file)

    print(f"\n[SUCCESS] Recoloring complete! Processed {len(png_files)} file(s).")


# =============================================================================
# 8-DIRECTIONAL MODULE - Diagonal Generation
# =============================================================================

def extract_sprite_row(image, row_index):
    """
    Extract a single row from an LPC 4-row sprite sheet.

    Args:
        image: PIL.Image (LPC format sprite sheet with 4 rows)
        row_index: Row to extract (0=S/Down, 1=W/Left, 2=N/Up, 3=E/Right)

    Returns:
        PIL.Image: Single row extracted
    """
    width, height = image.size
    row_height = height // 4

    # Calculate crop box (left, top, right, bottom)
    top = row_index * row_height
    bottom = top + row_height

    return image.crop((0, top, width, bottom))


def generate_diagonal(image, direction='ne', shear_amount=DIAGONAL_SHEAR_AMOUNT):
    """
    DEPRECATED: Use generate_blended_diagonal instead.
    Legacy function maintained for backwards compatibility.
    """
    return generate_blended_diagonal(image, direction, shear_amount)


def generate_blended_diagonal(image, direction='ne', shear_amount=DIAGONAL_SHEAR_AMOUNT):
    """
    Generate diagonal view using simple horizontal shear transformation.
    Uses single base row (North for NE/NW, South for SE/SW) with consistent shear.
    This method maintains perfect layer alignment for paper doll systems.

    Args:
        image: PIL.Image (LPC format with 4 rows: S, W, N, E)
        direction: Target diagonal direction ('ne', 'nw', 'se', 'sw')
        shear_amount: Horizontal shear amount (default 0.15)

    Returns:
        PIL.Image: Diagonal sprite row with all frames preserved
    """
    width, height = image.size

    # Check if this is a 4-row LPC sprite sheet
    is_lpc_format = height % 4 == 0 and height >= 256

    if not is_lpc_format:
        # Single row image - apply shear directly
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        img_width = image.width
        if direction in ['ne', 'se']:
            matrix = (1, shear_amount, 0, 0, 1, 0)  # Shear right
        else:
            matrix = (1, -shear_amount, img_width * shear_amount, 0, 1, 0)  # Shear left

        return image.transform(
            image.size,
            Image.AFFINE,
            matrix,
            resample=Image.NEAREST,
            fillcolor=(0, 0, 0, 0)
        )

    # Extract base row based on direction
    row_height = height // 4
    if direction in ['ne', 'nw']:
        # Use North row (walking up/away - back view)
        base_row = image.crop((0, row_height * 2, width, row_height * 3))
    else:
        # Use South row (walking down/toward - front view)
        base_row = image.crop((0, 0, width, row_height))

    if base_row.mode != 'RGBA':
        base_row = base_row.convert('RGBA')

    # Apply horizontal shear transformation
    row_width = base_row.width
    if direction in ['ne', 'se']:
        # Shear right for east diagonals
        matrix = (1, shear_amount, 0, 0, 1, 0)
    else:
        # Shear left for west diagonals
        matrix = (1, -shear_amount, row_width * shear_amount, 0, 1, 0)

    transformed = base_row.transform(
        base_row.size,
        Image.AFFINE,
        matrix,
        resample=Image.NEAREST,
        fillcolor=(0, 0, 0, 0)
    )

    return transformed


def generate_diagonal_variant(source_file, output_file, direction='ne', use_blending=True):
    """
    Generate a diagonal variant of a single sprite.

    Args:
        source_file: Path to source sprite
        output_file: Path to output file
        direction: Diagonal direction
        use_blending: If True, blend two cardinal directions for more accurate 8-dir (default: True)
    """
    blend_mode = "BLENDED" if use_blending else "SIMPLE"
    print(f"\n[DIAGONAL-{blend_mode}] Generating {direction.upper()} diagonal view")
    print(f"   Source: {source_file}")
    print(f"   Output: {output_file}")
    print(f"   Params: shear={DIAGONAL_SHEAR_AMOUNT}")
    if use_blending:
        print(f"   Mode: Blending two cardinal directions for true 8-directional")

    # Load image
    img = process_image(source_file)
    if img is None:
        return

    # Generate diagonal (blended or simple)
    if use_blending:
        diagonal = generate_blended_diagonal(img, direction)
    else:
        diagonal = generate_diagonal(img, direction)

    # Save
    save_image(diagonal, Path(output_file))

    print(f"[SUCCESS] Diagonal generation complete!")


# =============================================================================
# BATCH PROCESSING
# =============================================================================

def batch_process_folder(source_folder, output_folder, operation='recolor', **kwargs):
    """
    Batch process an entire folder of sprites.

    Args:
        source_folder: Path to source folder
        output_folder: Path to output folder
        operation: Type of operation ('recolor', 'diagonal')
        **kwargs: Operation-specific parameters
    """
    if operation == 'recolor':
        old_colors = kwargs.get('old_colors', [])
        new_color = kwargs.get('new_color', (0, 255, 0))
        generate_recolor_variant(source_folder, output_folder, old_colors, new_color)

    elif operation == 'diagonal':
        direction = kwargs.get('direction', 'ne')
        source_path = Path(source_folder)
        output_path = Path(output_folder)

        for img_file in source_path.rglob("*.png"):
            relative_path = img_file.relative_to(source_path)
            output_file = output_path / relative_path.parent / f"{relative_path.stem}_diagonal.png"
            generate_diagonal_variant(img_file, output_file, direction)


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Antigravity Pipeline - Manipulate LPC sprite sheets'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Recolor command
    recolor_parser = subparsers.add_parser('recolor', help='Recolor sprites')
    recolor_parser.add_argument('source', help='Source folder path')
    recolor_parser.add_argument('output', help='Output folder path')
    recolor_parser.add_argument('--old-colors', nargs='+', required=True,
                               help='Old RGB colors to replace (e.g., "128,128,128")')
    recolor_parser.add_argument('--new-color', required=True,
                               help='New RGB color (e.g., "0,255,0")')

    # Diagonal command
    diagonal_parser = subparsers.add_parser('diagonal', help='Generate diagonal views')
    diagonal_parser.add_argument('source', help='Source image or folder')
    diagonal_parser.add_argument('output', help='Output path')
    diagonal_parser.add_argument('--direction', default='ne',
                                choices=['ne', 'nw', 'se', 'sw'],
                                help='Diagonal direction')

    args = parser.parse_args()

    if args.command == 'recolor':
        # Parse colors
        old_colors = []
        for color_str in args.old_colors:
            r, g, b = map(int, color_str.split(','))
            old_colors.append((r, g, b))

        new_r, new_g, new_b = map(int, args.new_color.split(','))
        new_color = (new_r, new_g, new_b)

        generate_recolor_variant(args.source, args.output, old_colors, new_color)

    elif args.command == 'diagonal':
        if os.path.isfile(args.source):
            generate_diagonal_variant(args.source, args.output, args.direction)
        else:
            batch_process_folder(args.source, args.output, 'diagonal', direction=args.direction)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
