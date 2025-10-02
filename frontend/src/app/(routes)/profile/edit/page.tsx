"use client";

import { useUser } from "@clerk/nextjs";
import { useState } from "react";
import {
  updateProfileInfo,
  updateProfileImage,
  getFirstName,
  getLastName,
  getHotelName,
  getFullName,
  getPhoneNumber
} from "../../../../api/user"; // adjust path as needed
import Image from "next/image";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function EditProfilePage() {
  const { user } = useUser();
  const router = useRouter();
  const [firstName, setFirstName] = useState(user?.firstName || "");
  const [lastName, setLastName] = useState(user?.lastName || "");
  const [hotel, setHotel] = useState(getHotelName(user));
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);

  if (!user) return <p className="text-center mt-12">Loading...</p>;

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      setUploading(true);
      await updateProfileImage(user, file);
    } catch (err) {
      console.error("Failed to update profile image:", err);
    } finally {
      setUploading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      await updateProfileInfo(user, { firstName, lastName, hotel });
      router.push("/profile");
    } catch (err) {
      console.error("Failed to save profile changes:", err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex items-center justify-center w-screen min-h-screen bg-gray-50">
      <div className="relative max-w-3xl  p-6 bg-white shadow rounded-lg">

        {/* Centered banner */}
        <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 bg-[#013172] text-white px-6 py-2 rounded-full text-lg font-semibold shadow-lg">
          Edit Profile
        </div>

      {/* Profile Picture + Name */}
<div className="flex justify-center mb-6 mt-4">
  <div className="flex items-center space-x-6">
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

      <input
        type="file"
        id="profile-upload"
        className="hidden"
        accept="image/*"
        onChange={handleFileChange}
      />

      <label
        htmlFor="profile-upload"
        className="absolute bottom-0 right-0 bg-[#013172] text-white text-xs px-2 py-1 rounded-full cursor-pointer hover:bg-blue-800"
      >
        {uploading ? "..." : "Edit"}
      </label>
    </div>

    <p className="text-2xl font-semibold">{getFullName(user)}</p>
  </div>
</div>



        {/* Edit Form */}
        <form className="space-y-4 mt-4 flex flex-col items-center" onSubmit={handleSave}>
  <div className="flex flex-col items-center">
    <label className="block font-medium text-gray-700 mb-1 w-full max-w-md">
      First Name
    </label>
    <input
      type="text"
      value={firstName}
      onChange={(e) => setFirstName(e.target.value)}
      className="mt-1 p-2 w-[200px] max-w-md border rounded"
    />
  </div>

  <div className="flex flex-col items-center">
    <label className="block font-medium text-gray-700 mb-1 w-full max-w-md">
      Last Name
    </label>
    <input
      type="text"
      value={lastName}
      onChange={(e) => setLastName(e.target.value)}
      className="mt-1 p-2 w-[200px] max-w-md border rounded"
    />
  </div>

  <div className="flex flex-col items-center">
    <label className="block font-medium text-gray-700 mb-1 w-full max-w-md">
      Hotel Name
    </label>
    <input
      type="text"
      value={hotel}
      onChange={(e) => setHotel(e.target.value)}
      className="mt-1 p-2 w-[200px] max-w-md border rounded"
    />
  </div>


  {/* Buttons */}
  <div className="flex justify-center space-x-4 mt-6">
    <button
      type="submit"
      className="bg-[#013172] text-white px-6 py-3 rounded-full hover:bg-blue-800 transition-colors"
      disabled={saving}
    >
      {saving ? "Saving..." : "Save Changes"}
    </button>

    <Link
      href="/profile"
      className="bg-gray-300 text-gray-700 px-6 py-3 rounded-full hover:bg-gray-400 transition-colors"
    >
      Cancel
    </Link>
  </div>
</form>

      </div>
    </div>
  );
}
