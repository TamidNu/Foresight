import type { Metadata } from "next";
import { League_Spartan } from "next/font/google";
import Navbar from "../components/navbar";
import Footer from "../components/footer";
import AuthWrapper from "../components/auth-wrapper";
import "./globals.css";
import { currentUser } from "@clerk/nextjs/server";

const leagueSpartan = League_Spartan({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-league-spartan",
});

export const metadata: Metadata = {
  title: {
    default: "Foresight",
    template: "%s | Foresight",
  },
  description:
    "Foresight is a revenue intelligence platform for hotels. Stop reacting to demand—start predicting it. Maximize revenue with AI-powered pricing that adapts to events, flights, and weather.",

  keywords: [
    "hotel revenue management",
    "AI pricing",
    "hospitality tech",
    "revenue intelligence",
    "dynamic pricing",
    "hotel booking optimization",
    "event-driven pricing",
    "boutique hotels",
  ],

  authors: [{ name: "Foresight Team" }],

  icons: {
    icon: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },

  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://foresight-tamid.vercel.app", // replace with your actual domain
    siteName: "Foresight",
    title: "Foresight – Unlock Your Revenue Potential",
    description:
      "Hotels miss out on 10–20% revenue due to mispriced rooms. Foresight’s AI-powered revenue intelligence connects to your PMS, analyzes demand drivers, and maximizes room rates.",
    images: [
      {
        url: "frontend/public/FORESIGHT-SMALL.png", // replace with branded preview image
        width: 1200,
        height: 630,
        alt: "Foresight Revenue Intelligence Dashboard",
      },
    ],
  },

  metadataBase: new URL("https://foresight-tamid.vercel.app"),
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await currentUser(); // 👈 Fetch user server-side

  return (
    <html lang="en" className={leagueSpartan.variable}>
      <body className={`${leagueSpartan.className} flex flex-col min-h-screen`}>
        <AuthWrapper>
          {/* Pass user to Navbar */}
          <Navbar user={user} />
          <main className="flex-1 flex">{children}</main>
          <Footer />
        </AuthWrapper>
      </body>
    </html>
  );
}
