import { useUser as useClerkUser } from "@clerk/clerk-react";
import { useEffect, useState } from "react";

export function useUser() {
 const { user: clerkUser, isLoaded, isSignedIn } = useClerkUser();
  
  useEffect(() => {
    if (!isLoaded || !isSignedIn || !clerkUser) {
    return;
  }

    const userData = {
          id: clerkUser.id,
          email: clerkUser.primaryEmailAddress?.emailAddress || "",
          name: clerkUser.fullName || clerkUser.firstName || "Unknown User",
          phoneNumber: clerkUser.primaryPhoneNumber
        };
  })
}