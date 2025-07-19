import { motion } from "framer-motion"
import { Upload } from 'lucide-react';


export default function ChooseYourVibe() {
    return (
        <>
        <div className="py-20">
            <h1 className="text-center text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 bg-clip-text text-transparent leading-tight mb-12">Choose Your Vibe</h1>
        </div>
        <div className="flex flex-col md:flex-row items-start justify-center gap-24">
            <motion.div className="flex flex-col items-center justify-center text-center max-w-xs" initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0 }}
                    whileInView={true}>
                        <div className="flex items-center justify-center bg-gradient-to-br from-purple-200 to-pink-200 w-24 h-24 rounded-2xl mb-4">
                        <Upload color="#a123fa" size={40} />
                    </div>

            </motion.div>
        </div>
        </>
    )
}