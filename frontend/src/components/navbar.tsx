import Link from "next/link";
import Image from "next/image";
import { UserButton, SignInButton, SignUpButton } from "@clerk/nextjs";
import type { User } from "@clerk/nextjs/server";

interface NavbarProps {
  user: User | null;
}

export default function Navbar({ user }: NavbarProps) {
  return (
    <nav style={{ backgroundColor: "#013172" }} className="text-white p-4">
      <div className="w-full grid grid-cols-3 items-center">
        {/* Logo */}
        <div className="flex justify-start">
          <Link href="/">
            <Image
              src="/FORESIGHT-SMALL.png"
              alt="Foresight Logo"
              width={150}
              height={50}
              priority
              className="hover:opacity-70 transition-opacity duration-300"
            />
          </Link>
        </div>

        {/* Navigation Links */}
        <ul className="flex justify-center space-x-6">
          {/* Always accessible */}
          <li>
            <Link href="/about" className="hover:text-gray-300">
              About
            </Link>
          </li>

          {user ? (
            <>
              <li><Link href="/dashboard" className="hover:text-gray-300">Dashboard</Link></li>
              <li><Link href="/calendar" className="hover:text-gray-300">Calendar</Link></li>
              <li><Link href="/reports" className="hover:text-gray-300">Reports</Link></li>
              <li><Link href="/intelligence" className="hover:text-gray-300">Intelligence</Link></li>
            </>
          ) : (
            <>
              <li>
                <SignInButton mode="modal" forceRedirectUrl="/dashboard">
                  <button className="hover:text-gray-300">Dashboard</button>
                </SignInButton>
              </li>
              <li>
                <SignInButton mode="modal" forceRedirectUrl="/calendar">
                  <button className="hover:text-gray-300">Calendar</button>
                </SignInButton>
              </li>
              <li>
                <SignInButton mode="modal" forceRedirectUrl="/reports">
                  <button className="hover:text-gray-300">Reports</button>
                </SignInButton>
              </li>
            </>
          )}
        </ul>

        <div className="flex justify-end gap-x-6">
          {user ? (
            <UserButton
              userProfileMode="navigation"
              userProfileUrl="/profile"
              appearance={{
                elements: { avatarBox: { width: "40px", height: "40px" } },
              }}
            />
          ) : (
            <div className="flex gap-x-6">
              <SignInButton mode="modal" forceRedirectUrl="/dashboard">
                <button className="hover:text-gray-300 transition-colors">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal" forceRedirectUrl="/dashboard">
                <button className="hover:text-gray-300 transition-colors">
                  Sign Up
                </button>
              </SignUpButton>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
