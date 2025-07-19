import { NextResponse } from "next/server";

export async function POST(request) {
    const formdata = await request.formData();
    const file = await formdata.file[0];

    const uploadFormData = new FormData()
}