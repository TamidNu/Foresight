import React from "react";
import type { Metadata } from "next";


export const metadata: Metadata = {
  title: "Profile"
};

function Profile() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4 py-8 bg-gray-50">
      <h1 className="text-4xl font-bold mb-6">Profile</h1>
    </div>
  );
}

export default Profile;