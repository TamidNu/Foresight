export interface ICalendar {
    month: number;
    days: IDay[][];
    year: number;
}

export interface IDay {
    date: Date | null;
    weekday: string | null;
    numMonthDay: number | null;
    demand?: number;
}
