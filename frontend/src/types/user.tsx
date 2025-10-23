import { IHotel } from "./hotel"; 

export interface IUser {
    firstName: string;
    lastName: string;
    email: string;
    phoneNumber: string;
    hotel: IHotel;
}