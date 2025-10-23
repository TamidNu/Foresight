# this is a MOCK service (should straight up give BS/random price reccomendations)
# the point of this is to follow good architecture practices and build out the rest of the backend
# we should be doing this though DI (Dependency Injection), meaning we can swap this mock service out for the real one
# in our controller (pricing_controller.py) and the functionality should still be the same
# the point of this file is to figure out the shape of data, the shape of our DTOs, and what functions or abstractions
# we should have here

from typing import List, Dict, Any
from pydantic import BaseModel

class PricingItem(BaseModel):
    date: str
    room_type_code: str
    price_rec: float
    price_min: float
    price_max: float
    drivers: List[str] = []

class MockPricingEngine:
    def __init__(self):
        pass

    def price(self, hotel_id: int, room_type_code: str, dates: List[str]) -> List[PricingItem]:
        return [PricingItem(date=date, room_type_code=room_type_code, price_rec=random.random(), price_min=random.random(), price_max=random.random(), drivers=[]) for date in dates]

    def quote(self, hotel_id: int, room_type_code: str, dates: List[str]) -> List[PricingItem]:
        return [PricingItem(date=date, room_type_code=room_type_code, price_rec=random.random(), price_min=random.random(), price_max=random.random(), drivers=[]) for date in dates]