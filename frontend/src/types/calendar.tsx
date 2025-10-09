import { IDay } from "./day";

export interface ICalendar {
    month: string; // primitive type
    days: IDay[][];
}
