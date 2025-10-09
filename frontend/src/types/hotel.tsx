import { ICalendar } from "./calendar";

export interface IHotel {
    name: String;
    location: String;
    revenue: number;
    occupancy: number;
    calendar: ICalendar;
    // TODO: implement
}