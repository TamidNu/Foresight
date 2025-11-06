"use client";

import React, { useState } from "react";
import { ICalendar } from "@/types/calendar";
import { generateCalendar } from "@/utils/generateCalendar";
import MonthYearDropdown from "./month-year-drop";

export default function Calendar() {
  const textColor = "text-[#013172]";
  const today = new Date();
  const [month, setMonth] = useState(today.getMonth());
  const [year, setYear] = useState(today.getFullYear());

  const handlePrev = () => {
    if (month === 0) {
      setMonth(11);
      setYear((y) => y - 1);
    } else {
      setMonth((m) => m - 1);
    }
  };

  const handleNext = () => {
    if (month === 11) {
      setMonth(0);
      setYear((y) => y + 1);
    } else {
      setMonth((m) => m + 1);
    }
  };

  const handleToday = () => {
    const now = new Date();
    setMonth(now.getMonth());
    setYear(now.getFullYear());
  };

  return (
    <main className={`flex flex-col flex-1 justify-start items-center py-8 ${textColor}`}>
      <CalendarComponent
        month={month}
        year={year}
        onPrev={handlePrev}
        onNext={handleNext}
        onToday={handleToday}
        setMonth={setMonth}
        setYear={setYear}
      />
    </main>
  );
}

interface CalendarProps {
  month: number;
  year: number;
  onPrev: () => void;
  onNext: () => void;
  onToday: () => void;
  setMonth: React.Dispatch<React.SetStateAction<number>>;
  setYear: React.Dispatch<React.SetStateAction<number>>;
}

function CalendarComponent({
  month,
  year,
  onPrev,
  onNext,
  onToday,
  setMonth,
  setYear,
}: CalendarProps) {
  const calendar: ICalendar = generateCalendar(month, year);
  const today = new Date();

  const monthLabel = new Date(year, month, 1).toLocaleString("en-US", {
    month: "long",
    year: "numeric",
  });

  return (
    <div className="w-full max-w-6xl bg-white border border-gray-300 rounded-lg shadow-sm p-4 mt-6">
      {/* Header */}
      <div className="grid grid-cols-3 items-center mb-4">
        {/* Left: Custom dropdown */}
        <div className="flex justify-start">
          <MonthYearDropdown
            month={month}
            year={year}
            onChange={(m, y) => {
              setMonth(m);
              setYear(y);
            }}
          />
        </div>

        {/* Center: Month Label */}
        <h2 className="text-3xl font-semibold text-gray-800 text-center">
          {monthLabel}
        </h2>

        {/* Right: Navigation buttons */}
        <div className="flex gap-2 justify-end items-center">
          <button
            onClick={onPrev}
            className="px-3 py-1 rounded-full bg-gray-100 text-sm text-gray-700 hover:bg-gray-200 transition"
          >
            Prev
          </button>

          <button
            onClick={onToday}
            className="px-3 py-1 rounded-full bg-gray-100 text-sm text-gray-700 hover:bg-gray-200 transition"
          >
            Today
          </button>

          <button
            onClick={onNext}
            className="px-3 py-1 rounded-full bg-gray-100 text-sm text-gray-700 hover:bg-gray-200 transition"
          >
            Next
          </button>
        </div>
      </div>

      {/* Weekday Row */}
      <div className="grid grid-cols-7 text-center text-lg font-medium text-gray-600 border-b border-gray-200">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
          <div key={day} className="py-2 px-4">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="mt-4 max-h-[620px] overflow-y-auto">
        <div className="grid grid-cols-7 gap-x-2 gap-y-4">
          {calendar.days.flat().map((day, dayIdx) => {
            const isToday =
              day.numMonthDay === today.getDate() &&
              month === today.getMonth() &&
              year === today.getFullYear();

            return (
              <div
                key={dayIdx}
                className={`flex items-center justify-center text-lg sm:text-xl font-semibold rounded border transition
                  ${
                    isToday
                      ? "border-[#013172] bg-[#eaf1ff] text-[#013172]"
                      : "border-gray-200 bg-gray-50 hover:bg-gray-100 text-gray-800"
                  }`}
                style={{ height: "90px" }}
              >
                {day.numMonthDay || ""}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
