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

export interface SessionUser {
    id: number;
    name: string;
    email: string;
    // A segurança real continua no Django: isto só decide se a opção "Acesso ao admin"
    // aparece no menu, nunca se o usuário pode de fato acessar o admin.
    is_staff: boolean;
}
