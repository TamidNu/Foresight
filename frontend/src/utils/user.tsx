// src/api/user.ts

/**
 * Helpers for accessing Clerk user data safely
 */

export function getFirstName(
    user: ReturnType<typeof import("@clerk/nextjs").useUser>['user']
  ): string {
    return user?.firstName || "-";
  }
  
  export function getLastName(
    user: ReturnType<typeof import("@clerk/nextjs").useUser>['user']
  ): string {
    return user?.lastName || "-";
  }
  
  export function getFullName(
    user: ReturnType<typeof import("@clerk/nextjs").useUser>['user']
  ): string {
    return user?.fullName || "-";
  }
  
  export function getPrimaryEmail(
    user: ReturnType<typeof import("@clerk/nextjs").useUser>['user']
  ): string {
    return user?.primaryEmailAddress?.emailAddress || "-";
  }

  export function getPhoneNumber(
    user: ReturnType<typeof import("@clerk/nextjs").useUser>['user']
  ): string {
    const d = (user?.primaryPhoneNumber?.phoneNumber || "").replace(/\D/g, "");
    return d.length === 11 ? `+${d[0]} (${d.slice(1,4)}) ${d.slice(4,7)}-${d.slice(7)}` : user?.primaryPhoneNumber?.phoneNumber || "-";
  }
  
  
  export function getHotelName(
    user: ReturnType<typeof import("@clerk/nextjs").useUser>['user']
  ): string {
    return "Test"; // default value for frontend-only
  }
  
  
  /**
   * Update profile image
   */
  export async function updateProfileImage(
    user: ReturnType<typeof import("@clerk/nextjs").useUser>['user'],
    file: File
  ): Promise<void> {
    if (!user) throw new Error("No user found");
    await user.setProfileImage({ file });
    await user.reload();
  }
  
  /**
   * Update profile info (firstName, lastName, hotel)
   */
  export async function updateProfileInfo(
    user: ReturnType<typeof import("@clerk/nextjs").useUser>['user'],
    data: {
      firstName?: string;
      lastName?: string;
      hotel?: string;
      phoneNumber?: string;
    }
  ): Promise<void> {
    if (!user) throw new Error("No user found");
  
    // Update name fields
    if (data.firstName) await user.update({ firstName: data.firstName });
    if (data.lastName) await user.update({ lastName: data.lastName });
  
  
    await user.reload();
  }
  
  
  
  
  