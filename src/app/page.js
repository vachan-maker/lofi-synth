'use client';
import { useEffect, useState } from 'react';
import Image from "next/image";
import Hero from "./components/Hero";
import Header from "./components/Header";
export default function Home() {
  const [msg, setMsg] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('Fetching data from Django API...');
    fetch('http://localhost:8000/api/hello/')
      .then(res => {
        console.log('Response status:', res.status);
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        console.log('Data received:', data);
        setMsg(data.message);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching data:', err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <>
      <Header/>
      <Hero/>
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>Django API Response:</h2>
        {loading && <p>Loading...</p>}
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
        {msg && <p style={{ color: 'green', fontSize: '18px' }}>{msg}</p>}
      </div>
    </>
  );
}

