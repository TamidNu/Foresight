"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

export default function AnimatedButton() {
  const [showButton, setShowButton] = useState(false);

  // Show button after fade-in sequence
  useEffect(() => {
    const timeout = setTimeout(() => setShowButton(true), 1200);
    return () => clearTimeout(timeout);
  }, []);

  if (!showButton) return null;

  return (
    <Link href="/dashboard" passHref>
      <button className="bg-[#013172] text-white text-lg md:text-xl font-semibold px-8 md:px-10 py-3 md:py-4 rounded-full shadow-xl hover:bg-[#014495] hover:scale-105 transition-transform animate-fade-in">
        explore
      </button>
    </Link>
  );
}