// Store currency is always USD, independent of the UI language. This is a
// presentation-only format: it does not convert the underlying numeric value.
const currency = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
});

export function formatPrice(value: number): string {
    return currency.format(value);
}
