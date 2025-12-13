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
DIAGONAL_WIDTH_SQUASH = 0.75  # How much to compress width (0.0-1.0) - more squash for better diagonal
DIAGONAL_SHEAR_AMOUNT = 0.2   # How much to slant the image (0.0-0.3 recommended) - increased for more angle

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


def generate_diagonal(image, direction='ne', width_squash=DIAGONAL_WIDTH_SQUASH,
                     shear_amount=DIAGONAL_SHEAR_AMOUNT):
    """
    Generate a diagonal view from a cardinal direction sprite.
    Uses affine transformations to simulate 3/4 perspective.
    For LPC 4-row sprites, extracts appropriate row and transforms it.

    Args:
        image: PIL.Image (LPC format with 4 rows: S, W, N, E)
        direction: Target diagonal direction ('ne', 'nw', 'se', 'sw')
        width_squash: How much to compress width (default from tunable param)
        shear_amount: How much to slant (default from tunable param)

    Returns:
        PIL.Image: Transformed image (single row for diagonal direction)
    """
    width, height = image.size

    # Check if this is a 4-row LPC sprite sheet
    is_lpc_format = height % 4 == 0 and height >= 256

    if is_lpc_format:
        # LPC format: 4 rows (Row 0=S, Row 1=W, Row 2=N, Row 3=E)
        # Extract appropriate row based on diagonal direction
        # NE/SE use East (row 3), NW/SW use West (row 1)
        if direction in ['ne', 'se']:
            source_row = extract_sprite_row(image, 3)  # East/Right row
        else:  # 'nw', 'sw'
            source_row = extract_sprite_row(image, 1)  # West/Left row

        # Use the extracted row for transformation
        image_to_transform = source_row
    else:
        # Not LPC format, transform entire image
        image_to_transform = image

    # Calculate new dimensions
    transform_width, transform_height = image_to_transform.size
    new_width = int(transform_width * width_squash)

    # Resize width first (squash)
    squashed = image_to_transform.resize((new_width, transform_height), Image.NEAREST)

    # Apply shear transformation
    # Affine matrix: (a, b, c, d, e, f) where transformation is:
    # x' = a*x + b*y + c
    # y' = d*x + e*y + f

    # Determine shear direction based on target diagonal
    if direction in ['ne', 'se']:
        # Slant right
        transform_matrix = (1, shear_amount, 0, 0, 1, 0)
    else:  # 'nw', 'sw'
        # Slant left
        transform_matrix = (1, -shear_amount, new_width * shear_amount, 0, 1, 0)

    # Apply transformation with NEAREST neighbor (preserves hard pixel edges)
    sheared = squashed.transform(
        squashed.size,
        Image.AFFINE,
        transform_matrix,
        resample=Image.NEAREST
    )

    return sheared


def generate_blended_diagonal(image, direction='ne', width_squash=DIAGONAL_WIDTH_SQUASH,
                               shear_amount=DIAGONAL_SHEAR_AMOUNT, blend_ratio=0.6):
    """
    Generate a blended diagonal view by compositing two cardinal directions.
    Creates 8 truly unique directional sprites.
    Processes each frame individually to prevent edge frame loss.

    Args:
        image: PIL.Image (LPC format with 4 rows: S, W, N, E)
        direction: Target diagonal direction ('ne', 'nw', 'se', 'sw')
        width_squash: How much to compress width (default from tunable param)
        shear_amount: How much to slant (default from tunable param)
        blend_ratio: Primary/secondary blend ratio (0.0-1.0, default 0.6 = 60% primary, 40% secondary)

    Returns:
        PIL.Image: Blended diagonal sprite row with all frames preserved
    """
    width, height = image.size

    # Check if this is a 4-row LPC sprite sheet
    is_lpc_format = height % 4 == 0 and height >= 256

    if not is_lpc_format:
        # Fall back to simple diagonal if not LPC format
        return generate_diagonal(image, direction, width_squash, shear_amount)

    # Define row pairs for each diagonal
    # Format: (primary_row, secondary_row)
    row_mapping = {
        'ne': (3, 2),  # East + North
        'nw': (1, 2),  # West + North
        'se': (3, 0),  # East + South
        'sw': (1, 0)   # West + South
    }

    primary_row_idx, secondary_row_idx = row_mapping[direction]

    # Extract both rows
    primary_row = extract_sprite_row(image, primary_row_idx)
    secondary_row = extract_sprite_row(image, secondary_row_idx)

    # Determine frame size (typically 64x64 for LPC sprites)
    row_height = primary_row.height
    frame_size = row_height  # Assuming square frames
    num_frames = primary_row.width // frame_size

    # Create output canvas for all frames
    output_row = Image.new('RGBA', (primary_row.width, row_height), (0, 0, 0, 0))

    # Process each frame individually to prevent edge loss
    for frame_idx in range(num_frames):
        x_start = frame_idx * frame_size
        x_end = x_start + frame_size

        # Extract individual frames
        primary_frame = primary_row.crop((x_start, 0, x_end, row_height))
        secondary_frame = secondary_row.crop((x_start, 0, x_end, row_height))

        # Transform this frame
        new_width = int(frame_size * width_squash)

        # Primary transformation
        primary_squashed = primary_frame.resize((new_width, frame_size), Image.NEAREST)

        # Add vertical skew to distinguish up (NE/NW) from down (SE/SW) diagonals
        vertical_skew = 0.15

        if direction in ['ne', 'nw']:
            # Up diagonals: lean back/upward (negative vertical skew)
            if direction == 'ne':
                primary_matrix = (1, shear_amount, 0, -vertical_skew, 1, frame_size * vertical_skew)
            else:  # nw
                primary_matrix = (1, -shear_amount, new_width * shear_amount, -vertical_skew, 1, frame_size * vertical_skew)
        else:
            # Down diagonals: lean forward/downward (positive vertical skew)
            if direction == 'se':
                primary_matrix = (1, shear_amount, 0, vertical_skew, 1, 0)
            else:  # sw
                primary_matrix = (1, -shear_amount, new_width * shear_amount, vertical_skew, 1, 0)

        primary_transformed = primary_squashed.transform(
            primary_squashed.size,
            Image.AFFINE,
            primary_matrix,
            resample=Image.NEAREST
        )

        # Transform secondary frame
        secondary_squashed = secondary_frame.resize((new_width, frame_size), Image.NEAREST)

        if direction in ['ne', 'se']:
            secondary_matrix = (1, shear_amount * 0.5, 0, 0, 1, 0)
        else:
            secondary_matrix = (1, -shear_amount * 0.5, new_width * shear_amount * 0.5, 0, 1, 0)

        secondary_transformed = secondary_squashed.transform(
            secondary_squashed.size,
            Image.AFFINE,
            secondary_matrix,
            resample=Image.NEAREST
        )

        # Blend the two transformed frames
        blended_frame = Image.blend(secondary_transformed, primary_transformed, blend_ratio)

        # Center this frame in a frame_size x frame_size canvas
        frame_canvas = Image.new('RGBA', (frame_size, frame_size), (0, 0, 0, 0))
        blended_width = blended_frame.width
        x_offset = (frame_size - blended_width) // 2
        frame_canvas.paste(blended_frame, (x_offset, 0), blended_frame)

        # Paste this frame into the output row
        output_row.paste(frame_canvas, (x_start, 0), frame_canvas)

    return output_row


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
    print(f"   Params: width_squash={DIAGONAL_WIDTH_SQUASH}, shear={DIAGONAL_SHEAR_AMOUNT}")
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
