"use client";

import { useUser } from "@clerk/nextjs";
import Image from "next/image";
import Link from "next/link";

export default function ProfilePage() {
  const { user } = useUser();

  if (!user) return <p className="text-center mt-12">Loading...</p>;

  return (
    <div className="max-w-3xl mx-auto mt-12 p-6 bg-white shadow rounded-lg">
      {/* Profile Picture and Name */}
      <div className="flex items-center space-x-6 mb-6">
        {user.imageUrl ? (
          <Image
            src={user.imageUrl}
            alt="Profile Picture"
            width={100}
            height={100}
            className="rounded-full border-2 border-gray-300"
          />
        ) : (
          <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center text-gray-500">
            N/A
          </div>
        )}

        <div>
          <h1 className="text-2xl font-semibold">{user.fullName || "No Name"}</h1>
          <p className="text-gray-500">{user.primaryEmailAddress?.emailAddress || "No email"}</p>
        </div>
      </div>

      {/* User Info */}
      <div className="space-y-4">
        <div>
          <h2 className="font-medium text-gray-700">First Name</h2>
          <p>{user.firstName || "-"}</p>
        </div>
        <div>
          <h2 className="font-medium text-gray-700">Last Name</h2>
          <p>{user.lastName || "-"}</p>
        </div>
        <div>
          <h2 className="font-medium text-gray-700">Email</h2>
          <p>{user.primaryEmailAddress?.emailAddress || "-"}</p>
        </div>
        <div>
          <h2 className="font-medium text-gray-700">Username</h2>
          <p>{user.username || "-"}</p>
        </div>
          <Link
           href="/profile/edit" className="mt-6 inline-block bg-[#013172] text-white px-6 py-3 rounded-full hover:bg-blue-800 transition-colors">
             Edit Profile
          </Link>
      </div>
    </div>
  );
}
