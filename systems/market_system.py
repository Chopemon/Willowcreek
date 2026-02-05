# systems/market_system.py
# Market simulation with supply/demand dynamics.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MarketItem:
    name: str
    base_price: float
    supply: int
    demand: int
    price: float = 0.0
    recent_sales: int = 0
    recent_shipments: int = 0

    def recalc_price(self) -> None:
        demand_factor = max(0.1, self.demand / max(1, self.supply))
        self.price = round(self.base_price * demand_factor, 2)


class MarketSystem:
    """
    Simple market model that tracks supply/demand and adjusts prices.
    """

    def __init__(self):
        self.items: Dict[str, MarketItem] = {}
        self.market_events: List[str] = []
        self._seed_items()

    def _seed_items(self) -> None:
        seeds = [
            ("produce", 5.0, 120, 90),
            ("lumber", 12.0, 80, 70),
            ("medicine", 25.0, 40, 60),
            ("coffee_beans", 9.0, 60, 75),
            ("clothing", 20.0, 50, 45),
        ]
        for name, base, supply, demand in seeds:
            item = MarketItem(name=name, base_price=base, supply=supply, demand=demand)
            item.recalc_price()
            self.items[name] = item

    def get_item(self, name: str) -> Optional[MarketItem]:
        return self.items.get(name)

    def record_sale(self, item_name: str, qty: int = 1) -> None:
        item = self.items.get(item_name)
        if not item:
            return
        item.supply = max(0, item.supply - qty)
        item.demand += qty
        item.recent_sales += qty

    def record_shipment(self, item_name: str, qty: int = 1) -> None:
        item = self.items.get(item_name)
        if not item:
            return
        item.supply += qty
        item.recent_shipments += qty

    def update_market(self) -> None:
        self.market_events.clear()
        for item in self.items.values():
            # Adjust demand down if stock is abundant
            if item.supply > item.demand * 1.5:
                item.demand = max(1, int(item.demand * 0.95))
            # Demand drifts upward if supply is low
            if item.supply < item.demand * 0.75:
                item.demand = int(item.demand * 1.05) + 1

            item.recalc_price()
            if item.recent_sales or item.recent_shipments:
                event = (
                    f"{item.name}: price {item.price}, supply {item.supply}, demand {item.demand} "
                    f"(sales {item.recent_sales}, shipments {item.recent_shipments})"
                )
                self.market_events.append(event)
            item.recent_sales = 0
            item.recent_shipments = 0

    def summary(self) -> Dict[str, Dict[str, float]]:
        return {
            name: {
                "price": item.price,
                "supply": item.supply,
                "demand": item.demand,
            }
            for name, item in self.items.items()
        }
