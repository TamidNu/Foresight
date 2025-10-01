"use client";

import { useUser, SignInButton, SignUpButton } from "@clerk/nextjs";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import {
  updateProfileImage,
  getFirstName,
  getLastName,
  getFullName,
  getHotelName,
  getPrimaryEmail,
  getPhoneNumber
} from "../../../api/user"; // adjust path as needed

export default function ProfilePage() {
  const { user } = useUser();
  const [uploading, setUploading] = useState(false);

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center w-screen h-screen space-y-4">
        <p className="text-center text-lg font-medium">
          Please sign in or create an account
        </p>
        <div className="flex space-x-4">
          <SignInButton>
            <button className="bg-[#013172] text-white px-6 py-2 rounded-full hover:bg-blue-800 transition-colors">
              Sign In
            </button>
          </SignInButton>
          <SignUpButton>
            <button className="bg-green-600 text-white px-6 py-2 rounded-full hover:bg-green-700 transition-colors">
              Sign Up
            </button>
          </SignUpButton>
        </div>
      </div>
    );
  }

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      await updateProfileImage(user, file);
    } catch (err) {
      console.error("Failed to update profile picture:", err);
    } finally {
      setUploading(false);
    }
  };

  const userFields: { label: string; value: string }[] = [
    { label: "First Name", value: getFirstName(user) },
    { label: "Last Name", value: getLastName(user) },
    { label: "Hotel Name", value: getHotelName(user) },
    { label: "Email", value: getPrimaryEmail(user) },
    { label: "Phone Number", value: getPhoneNumber(user) },
  ];

  return (
    <div className="flex items-center justify-center w-screen h-screen bg-gray-50">
  <div className="relative max-w-3xl p-6 bg-white shadow rounded-lg">

    {/* Banner label */}
    <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 bg-[#013172] text-white px-6 py-2 rounded-full text-lg font-semibold shadow-lg">
      Profile
    </div>

    {/* Profile Picture and Name */}
    <div className="flex items-center space-x-6 mb-6 mt-4">
      <div className="relative w-24 h-24">
        {user.imageUrl ? (
          <Image
            src={user.imageUrl}
            alt="Profile Picture"
            fill
            className="rounded-full border-2 border-gray-300 object-cover"
          />
        ) : (
          <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center text-gray-500">
            N/A
          </div>
        )}
      </div>

      <div>
        <h1 className="text-2xl font-semibold">{getFullName(user)}</h1>
      </div>
    </div>

    {/* User Info */}
    <div className="space-y-4 mt-4">
      {userFields.map((field) => (
        <div key={field.label}>
          <h2 className="font-medium text-gray-700">{field.label}</h2>
          <p>{field.value}</p>
        </div>
      ))}

      <div className="flex justify-center">
        <Link
          href="/profile/edit"
          className="mt-6 inline-block bg-[#013172] text-white px-6 py-3 rounded-full hover:bg-blue-800 transition-colors"
        >
          Edit
        </Link>
      </div>
    </div>
  </div>
</div>

  );
}
