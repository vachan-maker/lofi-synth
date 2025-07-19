
// page.js
'use client'; // Declare this as a Client Component
import { useEffect, useState } from 'react';
import Hero from "./components/Hero";
// Removed unused 'Image' and 'Header' imports
import Header from './components/Header';
import ReactRain from 'react-rain-animation';
import HowItWorks from './components/HowItWorks';


export default function Home() {
  const [msg, setMsg] = useState('Loading...'); // Set an initial loading message

  useEffect(() => {
    fetch('http://localhost:8000/api/hello/')
      .then(res => res.json())
      .then(data => setMsg(data.message))
      .catch(err => {
        console.error("Failed to fetch message:", err);
        setMsg("Failed to load message."); // Set an error message
      });
  }, []);

  return (
    <>
    <Header/>
    <main>
      <Hero />
      <HowItWorks/>
    </main>
    </>
  );
}
