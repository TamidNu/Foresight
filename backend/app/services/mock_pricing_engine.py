# this is a MOCK service (should straight up give BS/random price reccomendations)
# the point of this is to follow good architecture practices and build out the rest of the backend
# we should be doing this though DI (Dependency Injection), meaning we can swap this mock service out for the real one
# in our controller (pricing_controller.py) and the functionality should still be the same
# the point of this file is to figure out the shape of data, the shape of our DTOs, and what functions or abstractions
# we should have here

from datetime import datetime, timedelta
from typing import List

from app.models.dto import PricingItem


class MockPricingEngine:
    def __init__(self, version: str = "mock-v1"):
        self.version = version

    def quote(self, *, hotel_id: int, room_type_code: str, start_date: str, end_date: str) -> tuple[List[PricingItem], str]:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        items: List[PricingItem] = []

        cursor = start

        while cursor <= end:
            dow = cursor.weekday()  # 0=Mon..6=Sun
            month = cursor.month

            base = 150.0
            drivers: List[str] = []

            # weekend uplift
            if dow in (4, 5):
                base += 20.0
                drivers.append("Weekend uplift")

            # midweek softness
            if dow in (1, 2):
                base -= 10.0
                drivers.append("Midweek softness")

            # simple monthly seasonality map
            seasonality_map = {6: 10, 7: 15, 8: 10, 12: 5}

            if month in seasonality_map:
                base += seasonality_map[month]
                drivers.append("Seasonality")

            price_rec = round(base, 2)
            price_min = round(price_rec - 20, 2)
            price_max = round(price_rec + 20, 2)

            items.append(PricingItem(
                date=cursor.date().isoformat(),
                room_type_code=room_type_code,
                price_rec=price_rec,
                price_min=price_min,
                price_max=price_max,
                drivers=drivers,
            ))

            cursor += timedelta(days=1)

        return items, self.version