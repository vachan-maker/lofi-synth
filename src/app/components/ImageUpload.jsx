"use client";
import { Cloud, Upload, X, Download } from "lucide-react";
import { useState, useRef } from 'react';

export default function ImageUpload() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState(null);
    const [isDragOver, setIsDragOver] = useState(false);
    const [result, setResult] = useState(null);
    const fileInputRef = useRef(null);

    const handleFileSelect = (file) => {
        if (file && file.type.startsWith('image/')) {
            setSelectedFile(file);
            setError(null);
            setResult(null); // Clear previous results
        } else {
            setError('Please select a valid image file');
        }
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        handleFileSelect(file);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragOver(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragOver(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragOver(false);
        const file = e.dataTransfer.files[0];
        handleFileSelect(file);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!selectedFile) {
            setError('Please select a file');
            return;
        }

        setIsUploading(true);
        setError(null);
        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('http://localhost:8000/api/upload/', {
                method: 'POST',
                body: formData,
            });

            // Debug: Check what we're actually getting
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                console.log('Received non-JSON response:', text);
                throw new Error('Server returned invalid response');
            }

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Processing failed');
            }

            console.log('Processing successful:', result);
            setResult(result);

        } catch (err) {
            console.error('Error:', err);
            setError(err.message);
        } finally {
            setIsUploading(false);
        }
    };

    const handleDownload = async () => {
        if (!result?.audioData) {
            setError('No audio data available for download');
            return;
        }

        try {
            // Parse the audio result to extract download info
            const audioInfo = JSON.parse(result.audioData);
            
            if (audioInfo.audioUrl) {
                // Direct download from URL
                const link = document.createElement('a');
                link.href = audioInfo.audioUrl;
                link.download = 'generated-lofi-music.mp3';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                setError('Audio download URL not available');
            }
        } catch (error) {
            console.error('Download error:', error);
            setError('Failed to download audio file');
        }
    };

    return (
        <div className="py-20">
            <h1 className="text-center text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 bg-clip-text text-transparent leading-tight mb-12">
                Turn Your Images into Lofi Beats
            </h1>
            <div className="flex flex-col items-center justify-center max-w-md mx-auto">
                
                <form onSubmit={handleSubmit} className="w-full">
                    <div
                        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                            isDragOver ? 'border-purple-400 bg-purple-50' : 'border-gray-300'
                        }`}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                    >
                        <Cloud color="#ed3ba8" size={60} className="mx-auto mb-4"/>
                        
                        {selectedFile ? (
                            <div className="mb-4">
                                <p className="text-green-600 font-medium">{selectedFile.name}</p>
                                <p className="text-sm text-gray-500">
                                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                                <button
                                    type="button"
                                    onClick={() => {
                                        setSelectedFile(null);
                                        setResult(null);
                                    }}
                                    className="mt-2 text-red-500 hover:text-red-700"
                                >
                                    <X size={20} />
                                </button>
                            </div>
                        ) : (
                            <div className="mb-4">
                                <p className="text-gray-600 mb-2">Drag & drop an image here</p>
                                <p className="text-sm text-gray-400">or</p>
                            </div>
                        )}

                        <input
                            ref={fileInputRef}
                            type="file"
                            className="hidden"
                            accept="image/*"
                            onChange={handleFileChange}
                        />
                        
                        <button
                            type="button"
                            onClick={() => fileInputRef.current?.click()}
                            className="bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold py-2 px-4 rounded-lg shadow-md hover:scale-95 mb-4"
                        >
                            Choose File
                        </button>
                    </div>

                    <button 
                        type="submit" 
                        disabled={isUploading || !selectedFile}
                        className="w-full mt-4 cursor-pointer bg-gradient-to-r from-blue-400 to-pink-500 text-white font-semibold py-3 px-4 rounded-lg shadow-md hover:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isUploading ? 'Processing... ⏳' : "Generate Lofi Beat 🎵"}
                    </button>
                </form>
                
                {/* Success State */}
                {result && (
                    <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg w-full">
                        <h3 className="text-lg font-semibold text-green-800 mb-2">
                            🎵 Your Lofi Beat is Ready!
                        </h3>
                        <p className="text-sm text-green-700 mb-4">
                            Processing completed successfully
                        </p>
                        <button
                            onClick={handleDownload}
                            className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-2 px-4 rounded-lg shadow-md hover:scale-95 flex items-center justify-center gap-2"
                        >
                            <Download size={20} />
                            Download Audio
                        </button>
                    </div>
                )}
                
                {error && (
                    <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded w-full">
                        {error}
                    </div>
                )}
            </div>
        </div>
    );
}
