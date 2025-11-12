import { request } from "../utils/apiClient";
import type { PricingResponse } from "../types/pricing";

export type QuoteParams = {
  hotel_id: number;
  room_type_code: string;
  from_: string; // YYYY-MM-DD
  to: string;   // YYYY-MM-DD
};

export function getDefaultQuoteParams(): QuoteParams {
  const today = new Date();
  const to = new Date();
  to.setDate(today.getDate() + 30);

  const format = (d: Date) => d.toISOString().slice(0, 10);

  return {
    hotel_id: 1,
    room_type_code: "DLX-QUEEN",
    from_: format(today),
    to: format(to),
  };
}

export async function quote(params: QuoteParams): Promise<PricingResponse> {
  return request("/api/pricing/quote", {
    method: "POST",
    body: JSON.stringify(params),
  });
}