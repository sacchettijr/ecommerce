// Ignores any letter the user types into a phone field — digits, spaces and symbols
// (+, -, parentheses) stay untouched; the backend's PhoneNumberField validates the actual format.
export function sanitizePhoneInput(value: string): string {
    return value.replace(/\p{L}/gu, "");
}
