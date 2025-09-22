"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import Footer from "./components/footer";
import Head from "next/head";

export default function LandingPage() {
  const [subtitle, setSubtitle] = useState("");
  const fullText = "unlock your revenue potential.";
  const [showCursor, setShowCursor] = useState(true);

  // Typewriter effect
  useEffect(() => {
    let index = 0;
    let typingForward = true;
    const typingSpeed = 100;
    const deletingSpeed = 100;
    const pauseTime = 1000;
    let interval: NodeJS.Timeout;

    const startTyping = () => {
      interval = setInterval(() => {
        if (typingForward) {
          setSubtitle(fullText.slice(0, index + 1));
          index++;
          if (index === fullText.length) {
            typingForward = false;
            clearInterval(interval);
            setTimeout(startTyping, pauseTime);
          }
        } else {
          setSubtitle(fullText.slice(0, index - 1));
          index--;
          if (index === 0) {
            typingForward = true;
          }
        }
      }, typingForward ? typingSpeed : deletingSpeed);
    };

    startTyping();
    return () => clearInterval(interval);
  }, []);

  // Blinking cursor
  useEffect(() => {
    const cursorInterval = setInterval(() => {
      setShowCursor((prev) => !prev);
    }, 500);
    return () => clearInterval(cursorInterval);
  }, []);

  const [showButton, setShowButton] = useState(false);

  // Show button after fade-in sequence
  useEffect(() => {
    const timeout = setTimeout(() => setShowButton(true), 1200);
    return () => clearTimeout(timeout);
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      <Head>
        <title>Foresight</title>         
        <link rel="icon" href="/FORESIGHT-FINAL.png" />  
      </Head>
      
      <main className="flex-grow flex flex-col items-center justify-center bg-gradient-to-b from-white from-5% via-[#e4effc] via-20% to-[#b3d1f9] to-100% px-6">
        <section className="relative z-10 text-center max-w-3xl space-y-6 px-6">
          
          <div className="flex justify-center mb-4 opacity-0 animate-fade-in delay-100">
            <Image
              src="/FORESIGHT-LARGE.png"
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

          <p className="text-xl md:text-2xl text-[#000000] opacity-0 animate-fade-in delay-300 mt-2">
            {subtitle}
            <span
              className={`inline-block w-1 ml-1 bg-black ${
                showCursor ? "opacity-100" : "opacity-0"
              }`}
            ></span>
          </p>

          {showButton && (
            <Link href="/about" passHref>
              <button className="bg-[#013172] text-white text-lg md:text-xl font-semibold px-8 md:px-10 py-3 md:py-4 rounded-full shadow-xl hover:bg-[#014495] hover:scale-105 transition-transform animate-fade-in">
                explore
              </button>
            </Link>
          )}
        </section>

        <style jsx>{`
          @keyframes fade-in {
            from {
              opacity: 0;
              transform: translateY(20px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          .animate-fade-in {
            animation: fade-in 0.8s forwards;
          }
          .delay-100 {
            animation-delay: 0.1s;
          }
          .delay-200 {
            animation-delay: 0.2s;
          }
          .delay-300 {
            animation-delay: 0.3s;
          }
          .delay-400 {
            animation-delay: 0.4s;
          }
        `}</style>
      </main>

    </div>
  );
}
