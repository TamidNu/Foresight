import Link from "next/link";
import React from "react";
import Image from "next/image";

const Navbar = () => {
  return (
    <nav style={{ backgroundColor: "#013172" }} className="text-white p-4">
      <div className="container mx-auto flex items-center justify-between relative">
        <div className="flex-shrink-0 -ml-4"> {/* Added -ml-4 to move left */}
          <Link href="/">
            <Image
              src="/FORESIGHT-SMALL.png"
              alt="Foresight Logo"
              width={150} // Increased from 120
              height={50}  // Increased from 40 (maintain aspect ratio)
              priority
              className="hover:opacity-70 transition-opacity duration-300"
            />
          </Link>
        </div>
        <ul className="absolute left-1/2 transform -translate-x-1/2 flex space-x-6">
          <li>
            <Link href="/" className="hover:text-gray-300">Home</Link>
          </li>
          <li>
            <Link href="/dashboard" className="hover:text-gray-300">Dashboard</Link>
          </li>
          <li>
            <Link href="/about" className="hover:text-gray-300">About</Link>
          </li>
        </ul>
        <div className="flex-shrink-0">
          <Link href="/profile" className="hover:text-gray-300">
            Profile
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;