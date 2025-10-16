import { useUser as useClerkUser } from "@clerk/clerk-react";
import { useEffect, useState } from "react";
// import { userService } from "../services/userService";
// import { user } from "../types/user";

export function useUser() {
 const { user: clerkUser, isLoaded, isSignedIn } = useClerkUser();
  
  useEffect(() => {
    if (!isLoaded || !isSignedIn || !clerkUser) {
    return;
  }

    // steps:
    // - if the user isn't loaded, isn't signed in, or clerk hasn't provided user info -> returns early to prevent errors
    // - try to fetch the user from the backend
    // - if user doesn't exist, create a user
    // - return all associated values
    // 

  })
}