// app/reports/page.tsx
import React from "react";
import { currentUser } from "@clerk/nextjs/server";

export default async function ReportsPage() {
  const user = await currentUser();

  if (!user) {
    // If not signed in, redirect or show message
    return (
      <main className="flex flex-col items-center justify-center min-h-screen">
        <p className="text-gray-600 text-lg">
          Please sign in to access reports.
        </p>
      </main>
    );
  }

  return (
    <div className="flex flex-col items-center px-4 py-12 bg-gray-50 w-full">
      <h1 className="text-4xl font-bold mb-8">Overnight Intelligence Report</h1>
      <p className="text-center text-lg mb-12 max-w-4xl">
        This page will eventually display analytics, demand trends, and AI-driven revenue reports.
      </p>
    </div>
  );
}
