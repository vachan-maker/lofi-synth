import { Music } from "lucide-react";
import { Icon } from "lucide-react";
import { motion } from "framer-motion";
export default function Hero() {
    return (
        <div className="min-h-1/2 transition-colors">
            <section className="container mx-auto px-8 py-20 text-center max-w-5xl">
                <motion.h1
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}

                    className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 bg-clip-text text-transparent leading-tight"
                    style={{ opacity: 1, transform: "none" }}
                >
                    Turn Any Song into
                    <div className="relative">
                        Chill Lo-Fi Magic
                       
                    </div>

                </motion.h1>
                <p className="text-3xl text-gray-600">Upload your track. Choose your vibe. Let AI remix it instantly.</p>
                <div className="flex flex-row justify-center px-4 mt-5">
                    <button className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-full text-white border-2 py-2 px-2 flex-1 flex flex-row items-center gap-4 justify-center"><Music color="white" />Upload Music</button>
                    <input type="text" placeholder="Describe your vibe!......." className="bg-white rounded-full flex-1/2 px-2 py-2"></input>


                </div>
                <p className="mt-10 text-gray-600">Powered by AI</p>
            </section>
        </div>
    );
}