/**
 * LPC Diagonal Sprite Generator
 * JavaScript port of the Python antigravity.py diagonal generation system
 *
 * Generates NE, SE, NW, SW diagonal views from 4-direction LPC sprite sheets
 * using simple horizontal shear transformation (0.15 shear amount).
 *
 * Compatible with all LPC sprite sheet formats and maintains perfect layer alignment
 * for paper doll character systems.
 */

const DIAGONAL_SHEAR_AMOUNT = 0.15;

/**
 * Generate a diagonal sprite row from an LPC 4-row sprite sheet
 *
 * @param {HTMLCanvasElement|HTMLImageElement} sourceImage - Source LPC sprite (4 rows: S, W, N, E)
 * @param {string} direction - Target diagonal direction ('ne', 'nw', 'se', 'sw')
 * @param {number} shearAmount - Horizontal shear amount (default 0.15)
 * @returns {HTMLCanvasElement} Canvas containing the diagonal sprite row
 */
function generateDiagonal(sourceImage, direction, shearAmount = DIAGONAL_SHEAR_AMOUNT) {
    // Create canvas for source image
    const sourceCanvas = document.createElement('canvas');
    const sourceCtx = sourceCanvas.getContext('2d');

    // Handle both Image and Canvas inputs
    const img = sourceImage instanceof HTMLCanvasElement ? sourceImage : sourceImage;
    const width = img.width;
    const height = img.height;

    sourceCanvas.width = width;
    sourceCanvas.height = height;
    sourceCtx.drawImage(img, 0, 0);

    // Check if this is a 4-row LPC sprite sheet
    const isLPCFormat = height % 4 === 0 && height >= 256;

    if (!isLPCFormat) {
        console.warn('Not a standard LPC 4-row format, applying transformation to entire image');
        return applyShearTransform(sourceCanvas, direction, shearAmount);
    }

    // Extract the base row based on direction
    const rowHeight = height / 4;
    let baseRow;

    if (direction === 'ne' || direction === 'nw') {
        // Use North row (row 2) for northeast/northwest
        baseRow = extractRow(sourceCanvas, 2);
    } else {
        // Use South row (row 0) for southeast/southwest
        baseRow = extractRow(sourceCanvas, 0);
    }

    // Apply shear transformation
    return applyShearTransform(baseRow, direction, shearAmount);
}

/**
 * Extract a single row from a 4-row LPC sprite sheet
 *
 * @param {HTMLCanvasElement} sourceCanvas - Source sprite sheet
 * @param {number} rowIndex - Row index (0=S, 1=W, 2=N, 3=E)
 * @returns {HTMLCanvasElement} Canvas containing the extracted row
 */
function extractRow(sourceCanvas, rowIndex) {
    const width = sourceCanvas.width;
    const height = sourceCanvas.height;
    const rowHeight = height / 4;

    const rowCanvas = document.createElement('canvas');
    rowCanvas.width = width;
    rowCanvas.height = rowHeight;

    const ctx = rowCanvas.getContext('2d');
    ctx.drawImage(
        sourceCanvas,
        0, rowIndex * rowHeight,  // source x, y
        width, rowHeight,          // source width, height
        0, 0,                      // dest x, y
        width, rowHeight           // dest width, height
    );

    return rowCanvas;
}

/**
 * Apply horizontal shear transformation to create diagonal view
 *
 * @param {HTMLCanvasElement} sourceCanvas - Source sprite row
 * @param {string} direction - Direction ('ne', 'nw', 'se', 'sw')
 * @param {number} shearAmount - Shear amount
 * @returns {HTMLCanvasElement} Transformed canvas
 */
function applyShearTransform(sourceCanvas, direction, shearAmount) {
    const width = sourceCanvas.width;
    const height = sourceCanvas.height;

    // Create output canvas
    const outputCanvas = document.createElement('canvas');
    outputCanvas.width = width;
    outputCanvas.height = height;

    const ctx = outputCanvas.getContext('2d');

    // Set transformation matrix for horizontal shear
    // Matrix format: ctx.transform(a, b, c, d, e, f)
    // where: x' = a*x + c*y + e, y' = b*x + d*y + f

    if (direction === 'ne' || direction === 'se') {
        // Shear right (positive shear)
        ctx.transform(1, shearAmount, 0, 1, 0, 0);
    } else {
        // Shear left (negative shear) with offset to keep sprite in frame
        const offset = width * shearAmount;
        ctx.transform(1, -shearAmount, 0, 1, offset, 0);
    }

    // Draw the source image with transformation applied
    // Use 'nearest' image smoothing for pixel art
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(sourceCanvas, 0, 0);

    return outputCanvas;
}

/**
 * Generate all 4 diagonal directions for an LPC sprite sheet
 *
 * @param {HTMLCanvasElement|HTMLImageElement} sourceImage - Source LPC sprite
 * @param {number} shearAmount - Shear amount (default 0.15)
 * @returns {Object} Object with keys 'ne', 'nw', 'se', 'sw' containing canvases
 */
function generateAllDiagonals(sourceImage, shearAmount = DIAGONAL_SHEAR_AMOUNT) {
    return {
        ne: generateDiagonal(sourceImage, 'ne', shearAmount),
        nw: generateDiagonal(sourceImage, 'nw', shearAmount),
        se: generateDiagonal(sourceImage, 'se', shearAmount),
        sw: generateDiagonal(sourceImage, 'sw', shearAmount)
    };
}

/**
 * Generate all 8 directions (4 cardinal + 4 diagonal) for an LPC sprite sheet
 *
 * @param {HTMLCanvasElement|HTMLImageElement} sourceImage - Source LPC sprite
 * @param {number} shearAmount - Shear amount for diagonals (default 0.15)
 * @returns {Object} Object with keys for all 8 directions
 */
function generateAll8Directions(sourceImage, shearAmount = DIAGONAL_SHEAR_AMOUNT) {
    const sourceCanvas = document.createElement('canvas');
    const sourceCtx = sourceCanvas.getContext('2d');

    const img = sourceImage instanceof HTMLCanvasElement ? sourceImage : sourceImage;
    sourceCanvas.width = img.width;
    sourceCanvas.height = img.height;
    sourceCtx.drawImage(img, 0, 0);

    const rowHeight = sourceCanvas.height / 4;

    return {
        // Cardinal directions (extract directly)
        n: extractRow(sourceCanvas, 2),  // North
        e: extractRow(sourceCanvas, 3),  // East
        s: extractRow(sourceCanvas, 0),  // South
        w: extractRow(sourceCanvas, 1),  // West

        // Diagonal directions (generated)
        ne: generateDiagonal(sourceImage, 'ne', shearAmount),
        nw: generateDiagonal(sourceImage, 'nw', shearAmount),
        se: generateDiagonal(sourceImage, 'se', shearAmount),
        sw: generateDiagonal(sourceImage, 'sw', shearAmount)
    };
}

// Export for use in modules or Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        generateDiagonal,
        generateAllDiagonals,
        generateAll8Directions,
        DIAGONAL_SHEAR_AMOUNT
    };
}

// Also make available as global for direct browser use
if (typeof window !== 'undefined') {
    window.LPCDiagonalGenerator = {
        generateDiagonal,
        generateAllDiagonals,
        generateAll8Directions,
        DIAGONAL_SHEAR_AMOUNT
    };
}
