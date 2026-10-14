import type { SessionUser, UserAddress } from "../api/types.ts";

export function makeSessionUser(overrides: Partial<SessionUser> = {}): SessionUser {
    return {
        id: 1,
        name: "Jane Doe",
        email: "jane@example.com",
        date_birth: "1990-05-20",
        phone: "",
        created_at: "2026-01-10T12:00:00-04:00",
        is_staff: false,
        ...overrides,
    };
}

export function makeUserAddress(
    overrides: Partial<UserAddress> = {},
): UserAddress {
    return {
        id: 1,
        street: "Main Street",
        number: "100",
        complement: "",
        reference: "",
        district: "Downtown",
        postal_code: "00000-000",
        city: { id: 1, name: "Springfield" },
        state: { id: 1, name: "State", code: "ST" },
        country: { id: 1, name: "Country", iso_code: "CT" },
        primary: false,
        ...overrides,
    };
}
