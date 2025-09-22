import Link from "next/link";
import React from "react";

const Navbar = () => {
  return (
    <nav style={{ backgroundColor: "#013172" }} className="text-white p-4">
      <div className="container mx-auto flex items-center justify-between relative">
        <div className="flex-shrink-0">
          <Link href="/" className="text-xl">
            MyLogo
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
