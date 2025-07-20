import { NextResponse } from "next/server";
import { Cloudinary } from "@cloudinary/url-gen";
export async function POST(request) {
    const formdata = await request.formData();
    const file = await formdata.file[0];

    const uploadFormData = new FormData()
}

const cld = new Cloudinary({
  cloud: {
    cloudName: 'dvsxwxcjq',
    apiKey:process.env.API_KEY,
    apiSecret:process.env.SECRET_KEY
  }
});