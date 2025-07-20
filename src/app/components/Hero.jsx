import { Music, ArrowRight } from "lucide-react";
import { Icon } from "lucide-react";
import { motion } from "framer-motion";
export default function Hero() {
    return (
        <div className="min-h-1/2 transition-colors">
            <section className="container mx-auto px-8 py-20 text-center max-w-5xl">
                <div class="top-60 left-5 w-20 h-10 bg-gradient-to-r from-pink-400 to-purple-400 rounded-md z-50 opacity-40 rotate-10 animate-bounce"></div>
                <div class="fixed bottom-10 right-5 w-20 h-10 bg-gradient-to-r from-pink-400 to-purple-400 rounded-md z-50 opacity-40 rotate-5 animate-bounce"></div>
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
                <form className="flex flex-row justify-center px-4 mt-5 gap-4">
                    <label
                        htmlFor="file-upload"
                        className="bg-gradient-to-r from-purple-400 to-pink-500 rounded-full text-white py-3 px-6 flex items-center justify-center cursor-pointer hover:scale-95 transition-transform"
                    >
                        Upload Audio
                    </label>
                    <input
                        id="file-upload"
                        type="file"
                        className="hidden"
                    />
                    <div className="relative flex-grow max-w-lg">
                        <input 
                            type="text" 
                            placeholder="Describe your vibe!......." 
                            className="bg-white rounded-full w-full pl-6 pr-16 py-3 text-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-400"
                        />
                        <button 
                            type="submit" 
                            className="cursor-pointer absolute top-1/2 right-2 transform -translate-y-1/2 w-10 h-10 flex items-center justify-center text-white bg-purple-500 rounded-full hover:bg-purple-600 transition-colors"
                        >
                            <ArrowRight className="w-6 h-6" />
                        </button>
                    </div>
                </form>
                <p className="mt-10 text-gray-600">Powered by AI</p>
            </section>
        </div>
    );
}