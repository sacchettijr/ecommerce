const phoneDigits = (value: string): string => value.replace(/\D/g, "");

const phone: string = import.meta.env.VITE_COMPANY_PHONE ?? "(69) 99303-3993";
const whatsapp: string =
    import.meta.env.VITE_COMPANY_WHATSAPP ?? "(69) 99303-3993";

export const company = {
    name: "E-Commerce",
    addressLine1:
        import.meta.env.VITE_COMPANY_ADDRESS_LINE1 ??
        "Avenida Princesa Isabel, 7070",
    addressLine2:
        import.meta.env.VITE_COMPANY_ADDRESS_LINE2 ??
        "Centro - Alvorada do Oeste, RO.",
    addressCep: import.meta.env.VITE_COMPANY_CEP ?? "76930-000",
    phone,
    phoneHref: `tel:+55${phoneDigits(phone)}`,
    whatsapp,
    whatsappHref: `https://wa.me/55${phoneDigits(whatsapp)}`,
    email: import.meta.env.VITE_COMPANY_EMAIL ?? "sacchettif13@gmail.com",
} as const;
