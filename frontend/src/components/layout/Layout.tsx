import { Outlet } from "react-router";

import { Footer } from "./Footer.tsx";
import { Navbar } from "./Navbar.tsx";

export function Layout() {
    return (
        <div className="flex min-h-screen flex-col bg-white text-gray-900">
            <Navbar />
            <main className="flex-1">
                <Outlet />
            </main>
            <Footer />
        </div>
    );
}
