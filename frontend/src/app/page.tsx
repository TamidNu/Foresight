import React from "react";
import Image from "next/image";
import type { Metadata } from "next";
import Typewriter from "./components/typewriter";
import AnimatedButton from "./components/animated-button";

export const metadata: Metadata = {
  title: "Foresight",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function LandingPage() {
  return (
    <div className="flex flex-col items-center justify-center flex-1 bg-gradient-to-b from-white from-5% via-[#e4effc] via-20% to-[#b3d1f9] to-100% px-6">
      <section className="relative z-10 text-center max-w-3xl space-y-6 px-6">
        <div className="flex justify-center mb-4 opacity-0 animate-fade-in delay-100">
          <Image
            src="/favicon.ico"
            alt="Foresight Logo"
            width={220}
            height={220}
            priority
            className="drop-shadow-[0_10px_10px_rgba(0,0,0,0.3)]"
          />
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold text-[#013172] opacity-0 animate-fade-in delay-200 leading-tight whitespace-nowrap">
          welcome to foresight
        </h1>

        <Typewriter />
        <AnimatedButton />
      </section>
    </div>
  );
}
