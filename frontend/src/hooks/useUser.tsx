import { useUser as useClerkUser } from "@clerk/clerk-react";
import { useEffect, useState } from "react";

export interface User {
    firstName: string;
    lastName: string;
    email: string;
    phoneNumber: string;
    hotel: string;
}

export function useUser() {
    
}