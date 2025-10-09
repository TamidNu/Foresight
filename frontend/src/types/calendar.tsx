import { IDay } from "./day";

export interface ICalendar {
    month: String;
    days: IDay[][];
}