"use client";

import React from "react";
import { ICalendar, IDay } from "../types/calendar";
import { generateCalendar } from "@/utils/generateCalendar";

interface CalendarProps {
  month: number;
  year: number;
}

export default function CalendarComponent({ month, year }: CalendarProps) {
  //  const textColor = "text-[#013172]"; [#D1D5DB]
  const borderColor = "border-3 border-blue-500"; 

  const calendar: ICalendar = generateCalendar(month, year);

  // temporary -> to test how changing demand changes color 
  //calendar.days[2][2].demand= 0.5

  const monthLabel = new Date(year, month, 1).toLocaleString("en-US", {
    month: "long",
    year: "numeric",
  });

  return (
    <div className="w-full min-h-screen bg-gray-100 flex flex-col items-center p-4">
      {/* Header */}
      <div className="w-full max-w-6xl bg-white border border-gray-300 rounded-lg shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <button className="px-3 py-1 rounded bg-gray-100 text-sm text-gray-700">
            Prev
          </button>
          <h2 className="text-3xl font-semibold text-gray-800 text-center flex-1">
            {monthLabel}
          </h2>
          <button className="px-3 py-1 rounded bg-gray-100 text-sm text-gray-700">
            Next
          </button>
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
        <div className="mt-4">
          {calendar.days.map((week, weekIdx) => (
            <div key={weekIdx} className="grid grid-cols-7 gap-2">
              {week.map((day, dayIdx) => (
                <div
                  key={dayIdx}
                  className={`py-6 text-lg sm:text-xl font-semibold text-center rounded 
                    ${getDemandColor(day.demand)} ${isToday(day.date) ? borderColor : "border border-gray-200"}`}>
                  {day.numMonthDay || ""}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function getDemandColor(demand?: number) {
  if (demand === undefined) return "bg-white"; // placeholder or no demand

  if (demand < 0.25) return "bg-green-300";       // low demand
  if (demand < 0.5) return "bg-yellow-300";      // medium-low
  if (demand < 0.75) return "bg-orange-400";     // medium-high
  return "bg-red-500";                            // high demand
}

function isToday(date?: Date | null) {
  if (!date) return false;

  const today = new Date();
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  );
}
