// src/app/page.js
'use client'; // This is a Client Component

import Header from './components/Header';
import Hero from "./components/Hero";
import HowItWorks from './components/HowItWorks';
import ChooseYourVibe from './components/ChooseYourVibe';
import ImageUpload from './components/ImageUpload';
import ReactRain from 'react-rain-animation';
import { Upload } from 'lucide-react';

export default function Home() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <HowItWorks />
        <ChooseYourVibe />
        <ImageUpload />
      </main>
    </>
  );
}