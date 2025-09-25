export default function Footer() {
  return (
    <footer className="w-full bg-[#013172] text-white py-4 px-6">
      <div className="grid grid-cols-1 md:grid-cols-3 items-center text-sm">
        
        {/* Left slogan */}
        <div className="flex justify-center md:justify-start mb-2 md:mb-0">
          <p>stop reacting to demand. start predicting it.</p>
        </div>

        {/* Center copyright */}
        <div className="flex justify-center mb-2 md:mb-0">
          <p>© 2025 foresight. All rights reserved.</p>
        </div>

        {/* Right links */}
        <div className="flex justify-center md:justify-end space-x-6">
          <a href="/about" className="hover:underline">
            About
          </a>
          <a href="/contact" className="hover:underline">
            Contact
          </a>
        </div>
      </div>
    </footer>
  );
}
