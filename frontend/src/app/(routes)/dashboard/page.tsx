"use client";

import React from "react";

function Dashboard() {
  const textColor = "text-[#013172]"; 
  const borderColor = "border-[#D1D5DB]"; 
  const fontClass = "font-sans";

  return (
    <div className={`flex flex-1 ${textColor} ${fontClass}`}>
      <aside className={`w-72 bg-white border-r ${borderColor} p-4 space-y-4`}>
        <div>
          <p className="text-med mb-2">Date</p>
          <h2 className="font-bold">Property Name</h2>
          <p className="text-med text-[#4981d6] mb-2">Name</p>
        </div>
        <div>
          <p className="font-semibold">Occupancy (Next 7 Days)</p>
          <p className="text-xl text-[#4981d6] mb-2">00%</p>
        </div>
        <div>
          <p className="font-semibold">Revenue (MTD)</p>
        </div>
        <div>
          <p className="font-semibold">Active Alerts</p>
          <div className="bg-yellow-100 border-l-4 border-yellow-500 p-2 mb-2">
            <p className="text-sm">Event</p>
          </div>
          <div className="bg-red-100 border-l-4 border-red-500 p-2">
            <p className="text-sm">Event</p>
          </div>
        </div>
      </aside>
      <main className="flex-1 p-6 space-y-6">
        <h1 className="text-xl font-bold">Revenue Command Center</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className={`bg-[#e8f1ff] border border-[#aecaf5] rounded shadow`}>
            <div className="p-4">
              <p className="text-med text-gray-500">Incremental Revenue</p>
            </div>
          </div>
          <div className={`bg-[#e8f1ff] border border-[#aecaf5] rounded shadow`}>
            <div className="p-4">
              <p className="text-med text-gray-500">Intelligence Signals</p>
            </div>
          </div>
        </div>
        <div className={`bg-white border ${borderColor} rounded shadow`}>
          <div className="p-4">
            <p className="font-semibold">Revenue Performance</p>
            <div className="h-48 bg-gray-100 flex items-center justify-center text-gray-400">
              Chart
            </div>
          </div>
        </div>
        <div className={`bg-white border ${borderColor} rounded shadow`}>
          <div className="p-4">
            <p className="font-semibold">Demand Forecast (Next 30 Days)</p>
            <div className="h-32 bg-gray-100 flex items-center justify-center text-gray-400">
              Calendar
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
