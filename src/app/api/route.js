// app/api/upload/route.js
import { NextResponse } from "next/server";
import { v2 as cloudinary } from 'cloudinary';
import { spawn } from 'child_process';
import { writeFile, unlink, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';

cloudinary.config({
  cloud_name: 'dvsxwxcjq',
  api_key: process.env.API_KEY,
  api_secret: process.env.SECRET_KEY,
});

const PYTHON_TIMEOUT = 60000; // 60 seconds
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export async function POST(request) {
  let tempFilePath = null;
  
  try {
    const formData = await request.formData();
    const file = formData.get('file');

    if (!file) {
      return NextResponse.json({ error: "No file received." }, { status: 400 });
    }

    // Validate file size
    const bytes = await file.arrayBuffer();
    if (bytes.byteLength > MAX_FILE_SIZE) {
      return NextResponse.json({ 
        error: `File too large. Maximum size is ${MAX_FILE_SIZE / 1024 / 1024}MB` 
      }, { status: 400 });
    }

    const buffer = Buffer.from(bytes);
    
    // Ensure temp directory exists
    const tempDir = path.join(process.cwd(), 'temp');
    if (!existsSync(tempDir)) {
      await mkdir(tempDir, { recursive: true });
    }
    
    // Save file temporarily for Python script
    const tempFilename = `${Date.now()}-${file.name.replace(/[^a-zA-Z0-9.-]/g, '_')}`;
    tempFilePath = path.join(tempDir, tempFilename);
    await writeFile(tempFilePath, buffer);

    // Upload to Cloudinary in parallel with Python processing
    const [uploadResult, audioResult] = await Promise.all([
      new Promise((resolve, reject) => {
        cloudinary.uploader.upload_stream(
          { resource_type: "auto", folder: "uploads" },
          (error, result) => {
            if (error) reject(error);
            else resolve(result);
          }
        ).end(buffer);
      }),
      processPythonScript(tempFilePath)
    ]);

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
  } finally {
    // Clean up temp file
    if (tempFilePath) {
      try {
        await unlink(tempFilePath);
      } catch (cleanupError) {
        console.error('Failed to cleanup temp file:', cleanupError);
      }
    }
  }
}

function processPythonScript(imagePath) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', [
      path.join(process.cwd(), 'lof/api/utils.py'), 
      imagePath
    ]);
    
    let dataString = '';
    let errorString = '';
    let timeoutId = null;
    
    pythonProcess.stdout.on('data', (data) => {
      dataString += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      errorString += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (timeoutId) clearTimeout(timeoutId);
      
      if (code === 0) {
        resolve(dataString.trim());
      } else {
        reject(new Error(`Python script failed with code ${code}: ${errorString}`));
      }
    });
    
    pythonProcess.on('error', (error) => {
      if (timeoutId) clearTimeout(timeoutId);
      reject(new Error(`Failed to start Python process: ${error.message}`));
    });
    
    // Set timeout to prevent hanging
    timeoutId = setTimeout(() => {
      pythonProcess.kill('SIGTERM');
      reject(new Error('Python script timeout'));
    }, PYTHON_TIMEOUT);
  });
}
