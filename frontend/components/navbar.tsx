import Link from "next/link";
import React from "react";
import Image from "next/image";

const Navbar = () => {
  return (
    <nav style={{ backgroundColor: "#013172" }} className="text-white p-4">
      <div className="w-full grid grid-cols-3 items-center">
        
        {/* Logo */}
        <div className="flex justify-start">
          <Link href="/">
            <Image
              src="/FORESIGHT-SMALL.png"
              alt="Foresight Logo"
              width={150}
              height={50}
              priority
              className="hover:opacity-70 transition-opacity duration-300"
            />
          </Link>
        </div>

        {/* Navigation Links */}
        <ul className="flex justify-center space-x-6">
          <li>
            <Link href="/" className="hover:text-gray-300">Home</Link>
          </li>
          <li>
            <Link href="/about" className="hover:text-gray-300">About</Link>
          </li>
          <li>
            <Link href="/dashboard" className="hover:text-gray-300">Dashboard</Link>
          </li>
          <li>
            <Link href="/calendar" className="hover:text-gray-300">Calendar</Link>
          </li>
          <li>
            <Link href="/reports" className="hover:text-gray-300">Reports</Link>
          </li>
          <li>
            <Link href="/intelligence" className="hover:text-gray-300">Intelligence</Link>
          </li>
        </ul>

        {/* Profile Picture */}
        <div className="flex justify-end">
          <div className="relative group cursor-pointer">
            <Link href="/profile" className="block">
              <div className="w-10 h-10 rounded-full border-2 border-white overflow-hidden bg-white">
                <Image
                  src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40'%3E%3Ccircle cx='20' cy='20' r='20' fill='white' /%3E%3C/svg%3E"
                  alt="Profile"
                  width={40}
                  height={40}
                  className="w-full h-full object-cover"
                />
              </div>
            </Link>
          </div>
        </div>

      </div>
    </nav>
  );
};

export default Navbar;
