import React from "react";
import type { Metadata } from "next";

const nameTextClass = "mt-2 text-lg font-medium";
const roleTextClass = "text-sm text-gray-600";

export const metadata: Metadata = { title: "About" };

function About() {
  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center px-4 py-12">
      <h1 className="text-4xl font-bold mb-8">About</h1>
      <p className="text-center text-lg mb-12 max-w-2xl">
         description of foresight
      </p>

        <h1 className="text-4xl font-bold mb-8">Meet the Team</h1>
      {/* Top row: 5 people */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-8 mb-8">
        <Person img="/team1.jpg" name="Adit Karode" role="VP of Tech Consulting" />
        <Person img="/team2.jpg" name="Jeff Krapf" role="Director of Tech Consulting" />
        <Person img="/team3.jpg" name="Rishi Dilip" role="Project Manager" />
        <Person img="/team4.jpg" name="Naman Rusia" role="Tech Lead" />
        <Person img="/team5.jpg" name="Madhav Nair" role="Developer" />
      </div>

      {/* Bottom row: 5 people */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-8">
        <Person img="/team6.jpg" name="Aditya Patwal" role="Developer" />
        <Person img="/team7.jpg" name="Brianna Quin" role="Developer" />
        <Person img="/team8.jpg" name="Bhuvan Hospet" role="Developer" />
        <Person img="/team9.jpg" name="Anya Krishnamony" role="Developer" />
        <Person img="/team10.jpg" name="Ioanna Damianov" role="Developer" />
      </div>
    </main>
  );
}

// Reusable Person component
function Person({
  img,
  name,
  role,
}: {
  img: string;
  name: string;
  role: string;
}) {
  return (
    <div className="flex flex-col items-center w-[12rem]">
      <div className="w-full h-48 bg-gray-300 rounded-lg overflow-hidden flex items-center justify-center">
        <img src={img} alt={name} className="w-full h-full object-cover" />
      </div>
      <span className={nameTextClass}>{name}</span>
      <span className={roleTextClass}>{role}</span>
    </div>
  );
}

export default About;
