import Link from "next/link"
export default function Header() {
    return (
        <header className="w-full py-6 px-12 flex justify-between">
        <Link href="/"><p className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">Lofi Synth</p></Link>
        <Link href="/login"><button className=" bg-gradient-to-r from-purple-500 to-pink-500 text-white py-2 px-6 rounded-full cursor-pointer hover:scale-95">Login</button></Link>
        </header>
    )
}