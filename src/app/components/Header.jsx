"use client";
import Link from "next/link";
import { useAuth } from "../context/AuthContext";

export default function Header() {
    const { user, logOut, loading } = useAuth();

    return (
        <header className="w-full py-6 px-12 flex justify-between items-center">
            <Link href="/">
                <p className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                    Lofi Synth
                </p>
            </Link>

            <div suppressHydrationWarning>
                {loading ? (
                    <div className="text-white">Loading...</div>
                ) : user ? (
                    <div className="flex items-center gap-4">
                        <p className="text-white font-semibold">Welcome, {user.username}!</p>
                        <button
                            onClick={logOut}
                            className="bg-gray-600 text-white py-2 px-6 rounded-full cursor-pointer shadow-md hover:bg-gray-700 transition-colors"
                        >
                            Logout
                        </button>
                    </div>
                ) : (
                    <Link href="/login">
                        <button className="bg-gradient-to-r from-purple-500 to-pink-500 text-white py-2 px-6 rounded-full cursor-pointer shadow-md hover:scale-95 transition-transform">
                            Login
                        </button>
                    </Link>
                )}
            </div>
        </header>
    );
}
