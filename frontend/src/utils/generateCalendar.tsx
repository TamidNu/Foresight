import { startOfMonth, endOfMonth, eachDayOfInterval, getDay, format } from "date-fns";
import { IDay, ICalendar } from "../types/calendar";

/**
 * Generate a calendar for a given month and year.
 * Weeks are 2D arrays with placeholders at start/end.
 */
export function generateCalendar(month: number, year: number): ICalendar {
  const firstDayOfMonth = startOfMonth(new Date(year, month));
  const lastDayOfMonth = endOfMonth(firstDayOfMonth);

  const allDays = eachDayOfInterval({ start: firstDayOfMonth, end: lastDayOfMonth });

  const days: IDay[][] = [];
  let week: IDay[] = [];

  // Add placeholders for days before the first day of the month
  for (let i = 0; i < getDay(firstDayOfMonth); i++) {
    week.push({ date: null, numMonthDay: null, weekday: null });
  }

  // Fill in actual days
  allDays.forEach((day) => {
    week.push({
      date: day,
      numMonthDay: day.getDate(),
      weekday: format(day, "EEE"), // "Sun", "Mon", etc.
    });

    // If week is full, push to weeks array
    if (week.length === 7) {
      days.push(week);
      week = [];
    }
  });

  // Add placeholders to complete the last week if needed
  while (week.length > 0 && week.length < 7) {
    week.push({ date: null, numMonthDay: null, weekday: null });
  }
  if (week.length > 0) days.push(week);

  return { month, year, days };
}
