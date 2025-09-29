import type { Metadata } from "next";
import { League_Spartan } from "next/font/google";
import Navbar from "../../components/navbar";
import Footer from "../../components/footer";
import AuthWrapper from "../../components/auth-wrapper";
import "./globals.css";

const leagueSpartan = League_Spartan({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-league-spartan",
});

export const metadata: Metadata = {
  title: "Foresight",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={leagueSpartan.variable}>
      <body className={`${leagueSpartan.className} flex flex-col min-h-screen`}>
        {/* AuthWrapper provides ClerkProvider to everything inside */}
        <AuthWrapper>
          <Navbar />
          <main className="flex-1 flex">{children}</main>
          <Footer />
        </AuthWrapper>
      </body>
    </html>
  );
}
