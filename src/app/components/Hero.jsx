export default function Hero() {
  return (
    <div className="min-h-screen transition-colors">
        <section className="container mx-auto px-8 py-20 text-center">
      <h1
        className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 bg-clip-text text-transparent leading-tight"
        style={{ opacity: 1, transform: "none" }}
      >
        Turn Any Song into
        <div className="relative">
          Chill Lo-Fi Magic
          <div
            className="absolute -bottom-2 left-0 right-0 h-1 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full"
            style={{ transform: "none" }}
          ></div>
        </div>
        
      </h1>
      <p className="text-3xl text-gray-400">Upload your track. Choose your vibe. Let AI remix it instantly.</p>
      </section>
    </div>
  );
}