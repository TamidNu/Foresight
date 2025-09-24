"use client";
import type { Metadata } from "next";
import { League_Spartan } from 'next/font/google';
import Head from 'next/head';
import Navbar from "../../components/navbar";
import Footer from "../../components/footer";
import "./globals.css";
import { usePathname } from "next/navigation";

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
    <html lang="en" className={leagueSpartan.variable}>
      <Head>
        <link rel="icon" href="/favicon.ico" type="image/x-icon" />
        <title>Foresight</title>
      </Head>
      <body className={leagueSpartan.className}>
        {pathname !== "/" && <Navbar />}
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}