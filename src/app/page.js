'use client';
import { useEffect, useState } from 'react';
import Image from "next/image";
import Hero from "./components/Hero";
import Header from "./components/Header";
export default function Home() {
  const [msg, setMsg] = useState('');
  useEffect(() => {
    fetch('http://localhost:8000/api/hello/')
      .then(res => res.json())
      .then(data => setMsg(data.message));
  }, []);
  return (
    <>
  <Header/>
  <Hero/>
  </>
  );
}

