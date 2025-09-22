import React from "react";
import type { Metadata } from "next";

const nameTextClass = "mt-2 text-lg font-medium";
const roleTextClass = "text-sm text-gray-600";

export const metadata: Metadata = { title: "About" };

function About() {
  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center px-4 py-12">
      <h1 className="text-4xl font-bold mb-8">What is foresight?</h1>
      <p className="text-center text-lg mb-12 max-w-2xl">
      Foresight is a revenue intelligence platform that helps hotels unlock their full revenue potential through AI-powered demand prediction. We solve a critical industry problem: hotels miss out on 10-20% of potential revenue due to mispriced rooms, costing a typical 150-room hotel between $600k-$1.3M annually.
      <br />
      <br /> Our AI system detects demand signals 10-14 days before customers book by analyzing events, weather patterns, flight data, and social media through advanced web scraping and machine learning algorithms. This allows revenue managers to make proactive pricing decisions rather than reactive adjustments throughout the day.
      <br />
      <br /> Founded by Sally Pigott and Juliette Nicault, two hospitality finance experts with deep industry experience, Foresight transforms the manual, guesswork-based pricing process into an intelligent, automated system. We don't just offer revenue management – we provide revenue intelligence that helps hotels optimize pricing in real-time while maintaining human oversight and control.
      Stop reacting to demand. Start predicting it.
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
        <Person img="/team7.jpg" name="Brianna Quinn" role="Developer" />
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
