import type { User } from "@clerk/nextjs/server"; // adjust import if needed

export type UserPayload = {
  clerk_user_id: string;
  first_name: string;
  last_name: string;
  email: string;
  // optionally add image_url?: string
};

/**
 * Build the payload object to send to the backend
 */
export function buildUserPayload(user: User): UserPayload {
  return {
    clerk_user_id: user.id,
    first_name: (user.firstName ?? "").trim(),
    last_name: (user.lastName ?? "").trim(),
    email: (user.primaryEmailAddress?.emailAddress ?? "").trim().toLowerCase(),
  };
}

/**
 * Sign up a user and log success/error
 */
export async function handleUserSignup(user: any): Promise<Response> {
  const payload = buildUserPayload(user);

  console.log("[dashboard] server render:", {
    hasUser: true,
    clerkId: user.id,
    email: payload.email,
  });

  try {
    const response = await fetch("http://localhost:8000/api/users/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if ([200, 201, 409].includes(response.status)) {
      console.log("[user signup] success:", payload);
    } else {
      console.error("[user signup] failed:", response.status, response.statusText);
    }

    return response;
  } catch (err) {
    console.error("[user signup] error:", err);
    throw err;
  }
}
