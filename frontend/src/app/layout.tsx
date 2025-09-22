"use client";

import type { Metadata } from "next";
import Navbar from "./components/navbar";
import "./globals.css";
import { usePathname } from "next/navigation";

export default function RootLayout({
children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();

  return (
    <html lang="en">
      <body>
        {pathname !== "/" && <Navbar />}
        <main>{children}</main>
      </body>
    </html>
  );
}
