import { Cloud } from "lucide-react"
export default function ImageUpload() {
    return (
        <>
            <div className="py-20">
                <h1 className="text-center text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 bg-clip-text text-transparent leading-tight mb-12">Turn Your Images into Lofi Beats</h1>
                <div className="flex flex-col items-center justify-center">
                    <Cloud color="#ed3ba8" size={90} className="mb-15"/>
                    <div>
                        <form action="/upload" method="POST">
                <label
                    for="file-upload"
                    className="inline-block cursor-pointer bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold py-2 px-4 rounded-lg shadow-md hover:scale-95"
                >
                    Upload an Image
                </label>
                <input
                    id="file-upload"
                    type="file"
                    className="hidden"
                />
                <button type="submit" className="cursor-pointer bg-gradient-to-r from-blue-400 to-pink-500 text-white font-semibold py-2 px-4 rounded-lg shadow-md hover:scale-95 ml-5">Let's Go!</button>
                </form>
                </div>
                </div>
            </div>
        </>
    )
}