"use client";
import type { Metadata } from "next";
import { League_Spartan } from 'next/font/google';
import Head from 'next/head';
import Navbar from "../../components/navbar";
import Footer from "../../components/footer";
import "./globals.css";
import { usePathname } from "next/navigation";

import {
  ClerkProvider,
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from '@clerk/nextjs'

const leagueSpartan = League_Spartan({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-league-spartan',
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  return (
    <ClerkProvider>
    <html lang="en" className={leagueSpartan.variable}>
      <Head>
        <title>Foresight</title>
        <link rel="icon" href="/favicon.ico" sizes="any" />
      </Head>
      <body className={`${leagueSpartan.className} flex flex-col min-h-screen`}>
        <SignedOut>
              <SignInButton />
              <SignUpButton></SignUpButton>
        </SignedOut>
        <Navbar />
        <main className="flex-1 flex">{children}</main>
        <Footer />
      </body>
    </html>
    </ClerkProvider>
  );
}