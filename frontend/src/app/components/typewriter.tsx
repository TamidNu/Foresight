"use client";

import React, { useEffect, useState } from "react";

export default function Typewriter() {
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

  return (
    <p className="text-xl md:text-2xl text-[#000000] opacity-0 animate-fade-in delay-300 mt-2">
      {subtitle}
      <span
        className={`inline-block w-1 ml-1 bg-black ${
          showCursor ? "opacity-100" : "opacity-0"
        }`}
      ></span>
    </p>
  );
}