import { Upload, Wand2, Download } from "lucide-react";
import { motion } from "framer-motion";
export default function HowItWorks() {
    return (
        <div className="py-20">
            <h1 className="text-center text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 bg-clip-text text-transparent leading-tight mb-12">
                How it Works
            </h1>
            <div className="flex flex-col md:flex-row items-start justify-center gap-24">
                {/* Card 1: Upload */}
                <motion.div className="flex flex-col items-center justify-center text-center max-w-xs" initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0 }}
                    whileInView={true}>
                    <div className="flex items-center justify-center bg-gradient-to-br from-purple-200 to-pink-200 w-24 h-24 rounded-2xl mb-4">
                        <Upload color="#a123fa" size={40} />
                    </div>
                    <p className="font-bold text-xl mt-4">1. Upload Audio</p>
                    <p className="text-gray-600">Drop any music file or paste a link from YouTube, Spotify, etc.</p>
                </motion.div>

                {/* Card 2: AI Remix */}
                <motion.div className="flex flex-col items-center justify-center text-center max-w-xs" initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    whileInView={true}>
                    <div className="flex items-center justify-center bg-gradient-to-br from-purple-200 to-pink-200 w-24 h-24 rounded-2xl mb-4">
                        <Wand2 color="#a123fa" size={40} />
                    </div>
                    <p className="font-bold text-xl mt-4">2. Choose a Mood</p>
                    <p className="text-gray-600">Pick a preset or describe your vibe</p>
                </motion.div>

                {/* Card 3: Download */}
                <motion.div className="flex flex-col items-center justify-center text-center max-w-xs" initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                    whileInView={true}>
                    <div className="flex items-center justify-center bg-gradient-to-br from-purple-200 to-pink-200 w-24 h-24 rounded-2xl mb-4">
                        <Download color="#a123fa" size={40} />
                    </div>
                    <p className="font-bold text-xl mt-4">3. Get Instant Lo-Fi Remix</p>
                    <p className="text-gray-600">AI transforms it in seconds.</p>
                </motion.div>
            </div>
        </div>
    );
}