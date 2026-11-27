function toWhatsApp(raw) {
    const digits = String(raw).replace(/\D/g, "");
    if (digits.startsWith("27")) {
        if (digits.length !== 11) {
            throw new Error(`"${raw}" has ${digits.length} digits - a +27 number has 11`);
        }
        return digits;
    }
    if (digits.startsWith("0")) {
        if (digits.length !== 10) {
            throw new Error(`"${raw}" has ${digits.length} digits - a local number has 10`);
        }
        return "27" + digits.slice(1);
    }
    throw new Error(`"${raw}" must start with 0 or +27`);
}

module.exports = { toWhatsApp };