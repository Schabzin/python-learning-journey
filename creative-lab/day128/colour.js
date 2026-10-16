function hexToRgb(hex) {
    if (typeof hex !== "string" || !/^#[0-9a-fA-F]{6}$/.test(hex)) return null;
    return {
        r: parseInt(hex.slice(1, 3), 16),
        g: parseInt(hex.slice(3, 5), 16),
        b: parseInt(hex.slice(5, 7), 16)
    };
}

function channelToLinear(value) {
    const c = value / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function luminance(hex) {
    const rgb = hexToRgb(hex);
    if (rgb === null) return null;
    return 0.2126 * channelToLinear(rgb.r)
         + 0.7152 * channelToLinear(rgb.g)
         + 0.0722 * channelToLinear(rgb.b);
}

function contrastRatio(hexA, hexB) {
    const a = luminance(hexA);
    const b = luminance(hexB);
    if (a === null || b === null) return null;
    const lighter = Math.max(a, b);
    const darker = Math.min(a, b);
    return (lighter + 0.05) / (darker + 0.05);
}

function isReadable(textHex, backgroundHex, large = false) {
    const ratio = contrastRatio(textHex, backgroundHex);
    if (ratio === null) return false;
    return ratio >= (large ? 3 : 4.5);
}

if (typeof module !== "undefined") {
    module.exports = { hexToRgb, luminance, contrastRatio, isReadable };
}