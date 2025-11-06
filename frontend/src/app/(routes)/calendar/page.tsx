"use client";

import CalendarComponent from "../../../components/calendar"
import React from "react";
import { ICalendar, IDay } from "@/types/calendar";
import { generateCalendar } from "@/utils/generateCalendar";


export default function Calendar() {
  const textColor = "text-[#013172]"; 
  const borderColor = "border-[#D1D5DB]"; 


  return (
    <main className={`flex flex-1 ${textColor}`}>
      <CalendarComponent/>
    </main>
  );
}

