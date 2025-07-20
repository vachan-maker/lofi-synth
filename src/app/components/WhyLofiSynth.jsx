import { Lightbulb } from "lucide-react"
import { motion } from "framer-motion"
export default function WhyLofiSynth() {
    const reasons = [
        'No music skills needed',
        'Ideal for vlogging,studying and streaming',
        'Easy to use',
        'Powered by Suno & Google Gemini'
    ]
    return (
        <>
        <div className="py-20">
            <h1 className="text-center text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 bg-clip-text text-transparent leading-tight mb-12">
                Why Lofi Synth?
            </h1>
            <div className="grid grid-cols-2 gap-15 max-w-4xl my-0 mx-auto">
                {reasons.map((reason, index) => (
                    <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    whileInView={true}
 className="bg-[#fafaff] flex flex-row p-6 rounded-xl gap-8 shadow-lg items-center" key={index}>
                        <div className="bg-purple-500 w-10 h-10 rounded-full flex items-center justify-center">
                        <Lightbulb size={32} color="white"/></div>
                        {reason}
                    </motion.div>
                ))}
            </div>
        </div>
        </>
    )
}