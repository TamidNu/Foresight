"use client";

import React, { useState } from "react";

interface MonthYearDropdownProps {
  month: number;
  year: number;
  onChange: (month: number, year: number) => void;
}

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

export default function MonthYearDropdown({ month, year, onChange }: MonthYearDropdownProps) {
  const [open, setOpen] = useState(false);

  const years = Array.from({ length: 11 }, (_, i) => year - 5 + i);

  const handleSelect = (m: number, y: number) => {
    onChange(m, y);
    setOpen(false);
  };

  return (
    <div className="relative inline-block">
      <button
        onClick={() => setOpen((o) => !o)}
        className="px-4 py-2 bg-white border border-gray-200 rounded-full text-sm font-medium text-gray-700
                  shadow-sm hover:border-[#013172]/40 focus:outline-none focus:ring-2 focus:ring-[#013172]/40
                  transition-all duration-200 flex items-center gap-2"
      >
        {MONTHS[month]} {year}
        <p>⏷</p>
      </button>

      {open && (
        <div
          className="absolute z-20 mt-2 flex bg-white border border-gray-200 hover:bg-gray rounded-xl shadow-lg overflow-hidden"
          onMouseLeave={() => setOpen(false)}
        >
          {/* Month column */}
          <div className="max-h-56 overflow-y-auto p-2 border-r border-gray-100">
            {MONTHS.map((m, i) => (
              <button
                key={m}
                onClick={() => handleSelect(i, year)}
                className={`block w-full text-left px-3 py-1.5 rounded-md text-sm transition-all ${
                  i === month
                    ? "bg-[#013172]/10 text-[#013172]"
                    : "text-gray-700 hover:bg-[#013172]/10 hover:text-[#013172]"
                }`}
              >
                {m}
              </button>
            ))}
          </div>

          {/* Year column */}
          <div className="max-h-56 overflow-y-auto p-2">
            {years.map((y) => (
              <button
                key={y}
                onClick={() => handleSelect(month, y)}
                className={`block w-full text-left px-3 py-1.5 rounded-md text-sm transition-all ${
                  y === year
                    ? "bg-[#013172]/10 text-[#013172]"
                    : "text-gray-700 hover:bg-[#013172]/10 hover:text-[#013172]"
                }`}
              >
                {y}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
