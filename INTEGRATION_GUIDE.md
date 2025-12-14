# Diagonal Generation Integration Guide

## Overview
This guide explains how to integrate diagonal sprite generation (NE, SE, NW, SW) into the existing Universal LPC Sprite Generator.

## Current System Architecture

The LPC generator currently:
- Shows animations (walk, thrust, slash, etc.) with 4 cardinal directions built-in
- Each animation type has 4 rows: South (0), West (1), North (2), East (3)
- Uses Mithril.js framework for UI
- Canvas-based rendering system

## Integration Approach

### Option 1: Generate Diagonals During Export (Recommended)
**Best for**: Minimal UI changes, works with existing workflow

1. **Import diagonal-generator.js** in main.js:
```javascript
import { generateAll8Directions } from './diagonal-generator.js';
```

2. **Modify Export Function** to include diagonals:
```javascript
// When generating spritesheet for export
function generateExportSpritesheet(animation) {
    // ... existing code to get base spritesheet ...

    // Generate 8-direction version (adds 4 diagonal rows)
    const all8Dirs = generateAll8Directions(baseSpritesheetCanvas);

    // Create new canvas with 8 rows instead of 4
    const exportCanvas = document.createElement('canvas');
    exportCanvas.width = all8Dirs.n.width;
    exportCanvas.height = all8Dirs.n.height * 8; // 8 rows
    const ctx = exportCanvas.getContext('2d');

    // Draw all 8 directions in order
    const rowOrder = ['s', 'w', 'n', 'e', 'se', 'sw', 'ne', 'nw'];
    rowOrder.forEach((dir, index) => {
        ctx.drawImage(all8Dirs[dir], 0, index * all8Dirs[dir].height);
    });

    return exportCanvas;
}
```

3. **Add Export Option**:
```javascript
// In export UI
{
    type: 'checkbox',
    label: 'Include Diagonal Directions (NE, SE, NW, SW)',
    checked: true,
    onChange: (value) => state.exportDiagonals = value
}
```

### Option 2: Live Preview with Direction Selector
**Best for**: Interactive character preview

1. **Add Direction State** to constants.js:
```javascript
export const DIRECTIONS = [
    { value: 'n', label: 'North', row: 2 },
    { value: 'ne', label: 'NE', row: null, diagonal: true },
    { value: 'e', label: 'East', row: 3 },
    { value: 'se', label: 'SE', row: null, diagonal: true },
    { value: 's', label: 'South', row: 0 },
    { value: 'sw', label: 'SW', row: null, diagonal: true },
    { value: 'w', label: 'West', row: 1 },
    { value: 'nw', label: 'NW', row: null, diagonal: true }
];
```

2. **Add Direction Selector UI** in AnimationPreview.js:
```javascript
// In AnimationPreview component view
m("div.direction-selector", [
    m("label", "Direction:"),
    m("div.buttons.has-addons",
        DIRECTIONS.map(dir =>
            m("button.button" + (state.previewDirection === dir.value ? ".is-selected" : ""),
                {
                    onclick: () => {
                        state.previewDirection = dir.value;
                        updatePreviewDirection(dir);
                    }
                },
                dir.label
            )
        )
    )
])
```

3. **Update Preview Rendering**:
```javascript
function updatePreviewDirection(direction) {
    if (direction.diagonal) {
        // Generate diagonal on-the-fly
        const baseSheet = getBaseSpritesheetCanvas();
        const diagonal = generateDiagonal(baseSheet, direction.value);
        renderPreviewFromCanvas(diagonal);
    } else {
        // Use existing row
        renderPreviewFromRow(direction.row);
    }
}
```

### Option 3: Hybrid Approach (Best UX)
**Combines both**: Live preview + enhanced export

1. Add direction selector for preview (Option 2)
2. Automatically include diagonals in exports (Option 1)
3. Cache generated diagonals to avoid re-computation

## File Structure

```
lpc_generator/
├── sources/
│   ├── diagonal-generator.js         (NEW - core diagonal logic)
│   ├── main.js                        (MODIFY - import diagonal generator)
│   ├── state/
│   │   └── constants.js               (MODIFY - add DIRECTIONS constant)
│   ├── components/
│   │   └── preview/
│   │       └── AnimationPreview.js    (MODIFY - add direction selector)
│   └── canvas/
│       ├── preview-canvas.js          (MODIFY - handle diagonal rendering)
│       └── export.js                  (MODIFY - include diagonals in export)
```

## CSS Additions

```css
/* Direction selector styling */
.direction-selector {
    margin: 1rem 0;
    text-align: center;
}

.direction-selector .buttons {
    justify-content: center;
}

.direction-selector .button {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
}

.direction-selector .button.is-selected {
    background-color: #4CAF50;
    color: white;
}
```

## Export Format Options

### Standard Export (Current)
```
Sprite Sheet: 576 × 1024 pixels
Rows: 4 (S, W, N, E) × 4 animations = 16 rows total
```

### Enhanced Export (With Diagonals)
```
Sprite Sheet: 576 × 2048 pixels
Rows: 8 (S, W, N, E, SE, SW, NE, NW) × 4 animations = 32 rows total
```

Or:

### Optional Diagonal Export
```
Two files:
1. base_character.png (4 directions)
2. base_character_diagonals.png (4 diagonal directions only)
```

## Performance Considerations

1. **Lazy Generation**: Only generate diagonals when needed (preview or export)
2. **Caching**: Store generated diagonals in memory to avoid recomputation
3. **Web Workers**: For large batch exports, use Web Workers for generation
4. **Progressive Loading**: Generate one direction at a time with progress indicator

## Testing Checklist

- [ ] Test with all animation types (walk, thrust, slash, etc.)
- [ ] Test with all layer types (17 categories validated)
- [ ] Verify dimensions remain consistent (576×64 per row)
- [ ] Test export with various combinations of layers
- [ ] Verify diagonal alignment in composite characters
- [ ] Test on different browsers (Chrome, Firefox, Safari)
- [ ] Mobile responsiveness for direction selector
- [ ] Performance test with maximum layers (8+ layers)

## Backward Compatibility

The diagonal generation is **fully backward compatible**:
- Existing exports work unchanged
- Diagonal generation is opt-in
- Original 4-direction mode remains default
- No breaking changes to existing API

## Next Steps

1. Choose integration approach (Option 1, 2, or 3)
2. Test diagonal-generator.js in isolation (use test_diagonal_js.html)
3. Implement chosen approach
4. Add UI controls
5. Test thoroughly
6. Update user documentation
7. Deploy

## Support

For issues or questions:
- Python implementation: `forge_scripts/antigravity.py`
- JavaScript port: `forge_scripts/diagonal-generator.js`
- Test page: `test_diagonal_js.html`
- This guide: `INTEGRATION_GUIDE.md`
