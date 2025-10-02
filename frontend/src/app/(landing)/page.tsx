import React from "react";
import Image from "next/image";
import Link from "next/link";
import Typewriter from "../../components/typewriter";
import {
  SignedIn,
  SignedOut,
  SignInButton,
} from "@clerk/nextjs";

export default function LandingPage() {
  return (
    <div className="flex flex-col items-center justify-center flex-1 bg-gradient-to-b from-white from-5% via-[#e4effc] via-20% to-[#b3d1f9] to-100% px-6">
      <section className="relative z-10 text-center max-w-3xl space-y-6 px-6">
        <div className="flex justify-center mb-4 opacity-0 animate-fade-up delay-100">
          <Image
            src="/favicon.ico"
            alt="Foresight Logo"
            width={220}
            height={220}
            priority
            className="drop-shadow-[0_10px_10px_rgba(0,0,0,0.3)]"
          />
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold text-[#013172] opacity-0 animate-fade-up delay-200 leading-tight whitespace-nowrap">
          welcome to foresight
        </h1>

        <Typewriter />

        <div className="opacity-0 animate-fade-up delay-600">
          <SignedIn>
            <Link href="/dashboard" passHref>
              <button
                className="bg-[#013172] text-white text-lg md:text-xl font-semibold px-8 md:px-10 py-3 md:py-4 rounded-full shadow-xl 
                          hover:bg-[#014495] hover:scale-105 transition-transform"
              >
                explore
              </button>
            </Link>
          </SignedIn>

          <SignedOut>
            <SignInButton mode="modal" forceRedirectUrl="/dashboard">
              <button
                className="bg-[#013172] text-white text-lg md:text-xl font-semibold px-8 md:px-10 py-3 md:py-4 rounded-full shadow-xl 
                          hover:bg-[#014495] hover:scale-105 transition-transform"
              >
                explore
              </button>
            </SignInButton>
          </SignedOut>
        </div>
      </section>
    </div>
  );
}
