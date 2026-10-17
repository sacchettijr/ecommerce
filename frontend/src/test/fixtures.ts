import type {
    Product,
    PublicWishlistItem,
    SessionUser,
    UserAddress,
    WishlistItem,
} from "../api/types.ts";

export function makeProduct(overrides: Partial<Product> = {}): Product {
    return {
        id: 1,
        name: "Blue Mug",
        slug: "blue-mug",
        price: "19.90",
        thumbnail: null,
        ...overrides,
    };
}

export function makeWishlistItem(
    overrides: Partial<WishlistItem> = {},
): WishlistItem {
    return {
        id: 1,
        product: makeProduct(),
        added_at: "2026-01-10T12:00:00-04:00",
        position: 0,
        private: false,
        ...overrides,
    };
}

export function makePublicWishlistItem(
    overrides: Partial<PublicWishlistItem> = {},
): PublicWishlistItem {
    return {
        id: 1,
        product: makeProduct(),
        added_at: "2026-01-10T12:00:00-04:00",
        position: 0,
        ...overrides,
    };
}

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
