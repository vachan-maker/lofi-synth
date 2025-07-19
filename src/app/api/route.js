// app/api/upload/route.js
import { NextResponse } from "next/server";
import { v2 as cloudinary } from 'cloudinary';
import { spawn } from 'child_process';
import { writeFile } from 'fs/promises';
import path from 'path';
import fs from 'fs';

cloudinary.config({
  cloud_name: 'dvsxwxcjq',
  api_key: process.env.API_KEY,
  api_secret: process.env.SECRET_KEY,
});

export async function POST(request) {
  try {
    const formData = await request.formData();
    const file = formData.get('file');

    if (!file) {
      return NextResponse.json({ error: "No file received." }, { status: 400 });
    }

    // Convert file to buffer and save locally for Python processing
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    
    // Save file temporarily for Python script
    const tempDir = path.join(process.cwd(), 'temp');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
    
    const tempFilename = `${Date.now()}-${file.name}`;
    const tempFilePath = path.join(tempDir, tempFilename);
    await writeFile(tempFilePath, buffer);

    // Upload to Cloudinary (optional, for storage)
    const uploadResult = await new Promise((resolve, reject) => {
      cloudinary.uploader.upload_stream(
        { resource_type: "auto", folder: "uploads" },
        (error, result) => {
          if (error) reject(error);
          else resolve(result);
        }
      ).end(buffer);
    });

    // Process with Python script
    const audioResult = await processPythonScript(tempFilePath);
    
    // Clean up temp file
    fs.unlinkSync(tempFilePath);

    return NextResponse.json({
      message: "Processing complete",
      imageUrl: uploadResult.secure_url,
      audioData: audioResult,
      success: true
    });

  } catch (error) {
    console.error("Processing error:", error);
    return NextResponse.json({ 
      error: "Processing failed", 
      details: error.message 
    }, { status: 500 });
  }
}

function processPythonScript(imagePath) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', [
      path.join(process.cwd(), 'scripts/generate_lofi.py'), 
      imagePath
    ]);
    
    let dataString = '';
    let errorString = '';
    
    pythonProcess.stdout.on('data', (data) => {
      dataString += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      errorString += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve(dataString.trim());
      } else {
        reject(new Error(`Python script failed: ${errorString}`));
      }
    });
    
    // Set timeout to prevent hanging
    setTimeout(() => {
      pythonProcess.kill();
      reject(new Error('Python script timeout'));
    }, 60000); // 60 second timeout
  });
}
