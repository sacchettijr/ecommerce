export interface Paginated<T> {
    count: number;
    total_pages: number;
    current_page: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

export interface Product {
    id: number;
    name: string;
    slug: string;
    price: string;
    thumbnail: string | null;
    active: boolean;
}

export interface ProductCategory {
    id: number;
    name: string;
    slug: string;
}

export interface ProductImage {
    id: number;
    image: string;
}

export interface ProductDetail {
    id: number;
    name: string;
    slug: string;
    category: ProductCategory;
    description: string | null;
    price: string;
    images: ProductImage[];
}

export interface ContactPayload {
    name: string;
    email: string;
    phone: string;
    message: string;
}

export interface AddressLocation {
    id: number;
    name: string;
}

export interface AddressState extends AddressLocation {
    code: string;
}

export interface AddressCountry extends AddressLocation {
    iso_code: string;
}

export interface UserAddress {
    id: number;
    street: string;
    number: string;
    // Sempre string, nunca null — campos opcionais no backend (blank=True) serializam como "".
    complement: string;
    reference: string;
    district: string;
    postal_code: string;
    city: AddressLocation;
    state: AddressState;
    country: AddressCountry;
    primary: boolean;
}

export interface WishlistItem {
    id: number;
    product: Product;
    added_at: string;
    position: number;
    private: boolean;
}

export interface PublicWishlistItem {
    id: number;
    product: Product;
    added_at: string;
    position: number;
}

export interface PublicWishlist {
    public_id: string;
    items: PublicWishlistItem[];
}

export interface CartItem {
    id: number;
    product: Product;
    quantity: number;
    unit_price: string;
    line_total: string;
}

export interface CartSummary {
    items: CartItem[];
    subtotal: string;
    discount_total: string;
    total: string;
}

export interface SessionUser {
    id: number;
    name: string;
    email: string;
    date_birth: string;
    // String vazia quando não informado (PhoneNumberField normaliza, nunca é null).
    phone: string;
    // ISO 8601 com offset; pode ser null em registros muito antigos (campo nullable no backend).
    created_at: string | null;
    // A segurança real continua no Django: isto só decide se a opção "Acesso ao admin"
    // aparece no menu, nunca se o usuário pode de fato acessar o admin.
    is_staff: boolean;
}
