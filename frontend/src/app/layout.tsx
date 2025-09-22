"use client";
import type { Metadata } from "next";
import { League_Spartan } from 'next/font/google';
import Navbar from "./components/navbar";
import Footer from "./components/footer";
import "./globals.css";
import { usePathname } from "next/navigation";

const leagueSpartan = League_Spartan({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'], // Choose weights you need
  variable: '--font-league-spartan',
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  
  return (
    <html lang="en" className={leagueSpartan.variable}>
      <body className={leagueSpartan.className}>
        {pathname !== "/" && <Navbar />}
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}