import React from "react";
import { Upload, Wand2, Download } from "lucide-react";
import { motion } from "framer-motion";

const cardData = [
    {
        icon: Upload,
        title: "1. Upload Audio",
        description: "Drop any music file or paste a link from YouTube, Spotify, etc.",
        delay: 0
    },
    {
        icon: Wand2,
        title: "2. Choose a Mood",
        description: "Pick a preset or describe your vibe",
        delay: 0.2
    },
    {
        icon: Download,
        title: "3. Get Instant Lo-Fi Remix",
        description: "AI transforms it in seconds.",
        delay: 0.4
    }
];

const Card = React.memo(({ icon: Icon, title, description, delay }) => (
    <motion.div 
        className="flex flex-col items-center justify-center text-center max-w-xs" 
        initial={{ opacity: 0, y: 50 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.8, delay }}
    >
        <div className="flex items-center justify-center bg-gradient-to-br from-purple-200 to-pink-200 w-24 h-24 rounded-2xl mb-4">
            <Icon color="#a123fa" size={40} />
        </div>
        <p className="font-bold text-xl mt-4">{title}</p>
        <p className="text-gray-600">{description}</p>
    </motion.div>
));

Card.displayName = 'Card';

function HowItWorks() {
    return (
        <div className="py-20">
            <h1 className="text-center text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 bg-clip-text text-transparent leading-tight mb-12">
                How it Works
            </h1>
            <div className="flex flex-col md:flex-row items-start justify-center gap-24">
                {cardData.map((card, index) => (
                    <Card key={index} {...card} />
                ))}
            </div>
        </div>
    );
}

export default React.memo(HowItWorks);