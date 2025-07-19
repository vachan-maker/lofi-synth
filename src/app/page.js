
// page.js
'use client'; // Declare this as a Client Component
import { useEffect, useState } from 'react';
import Hero from "./components/Hero";
// Removed unused 'Image' and 'Header' imports
import Header from './components/Header';
import ReactRain from 'react-rain-animation';
import HowItWorks from './components/HowItWorks';
import ChooseYourVibe from './components/ChooseYourVibe';
import ImageUpload from './components/ImageUpload';
import WhyLofiSynth from './components/WhyLofiSynth';


export default function Home() {
  const [msg, setMsg] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);


  return (
    <>
    <Header/>
    <main>
      <Hero />
      <HowItWorks/>
      <ImageUpload/>
      <WhyLofiSynth/>
    </main>
    </>
  );
}
