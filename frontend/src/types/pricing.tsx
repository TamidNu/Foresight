export type PricingItem = {
  date: string;
  room_type_code: string;
  price_rec: number;
  price_min: number;
  price_max: number;
  drivers: string[];
};

export type PricingResponse = {
  items: PricingItem[];
  modelVersion: string;
};