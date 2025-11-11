import { request } from "../utils/apiClient";
import type { PricingResponse } from "../types/pricing";

export type QuoteParams = {
  hotel_id: number;
  room_type_code: string;
  from: string; // YYYY-MM-DD
  to: string;   // YYYY-MM-DD
};

export async function quote(params: QuoteParams): Promise<PricingResponse> {
  return request("/api/pricing/quote", {
    method: "POST",
    body: JSON.stringify(params),
  });
}