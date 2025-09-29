"use client";

import { useUser } from "@clerk/nextjs";

export default function EditProfilePage() {
  const { user } = useUser();

  if (!user) return <p className="text-center mt-12">Loading...</p>;

  return (
    <div className="max-w-3xl mx-auto mt-12 p-6 bg-white shadow rounded-lg">
      {/* Page Title */}
      <h1 className="text-2xl font-semibold mb-6">Edit Profile</h1>

      {/* Profile Picture */}
      <div className="flex items-center space-x-6 mb-6">
        {user.imageUrl ? (
          <img
            src={user.imageUrl}
            alt="Profile Picture"
            className="w-24 h-24 rounded-full border-2 border-gray-300 object-cover"
          />
        ) : (
          <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center text-gray-500">
            N/A
          </div>
        )}
        <div>
          <p className="font-medium text-gray-700">{user.fullName || "No Name"}</p>
          <p className="text-gray-500">{user.primaryEmailAddress?.emailAddress || "No email"}</p>
        </div>
      </div>

      {/* Edit Form */}
      <form className="space-y-4">
        <div>
          <label className="block font-medium text-gray-700">First Name</label>
          <input
            type="text"
            defaultValue={user.firstName || ""}
            className="mt-1 p-2 w-full border rounded"
          />
        </div>

        <div>
          <label className="block font-medium text-gray-700">Last Name</label>
          <input
            type="text"
            defaultValue={user.lastName || ""}
            className="mt-1 p-2 w-full border rounded"
          />
        </div>

        <div>
          <label className="block font-medium text-gray-700">Username</label>
          <input
            type="text"
            defaultValue={user.username || ""}
            className="mt-1 p-2 w-full border rounded"
          />
        </div>

        <div>
          <label className="block font-medium text-gray-700">Email</label>
          <input
            type="email"
            defaultValue={user.primaryEmailAddress?.emailAddress || ""}
            className="mt-1 p-2 w-full border rounded"
          />
        </div>

        <button
          type="submit"
          className="mt-4 bg-[#013172] text-white px-6 py-3 rounded-full hover:bg-blue-800 transition-colors"
        >
          Save Changes
        </button>
      </form>
    </div>
  );
}
