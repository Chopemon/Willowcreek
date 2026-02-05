# systems/business_system.py
# NPC-run businesses with hiring/employees.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Business:
    name: str
    owner: str
    category: str
    location: str
    employees: List[str] = field(default_factory=list)
    cash_on_hand: int = 1000

    def hire(self, npc_name: str) -> bool:
        if npc_name in self.employees:
            return False
        self.employees.append(npc_name)
        return True

    def fire(self, npc_name: str) -> bool:
        if npc_name not in self.employees:
            return False
        self.employees.remove(npc_name)
        return True


class BusinessSystem:
    """
    Tracks NPC-owned businesses and hiring.
    """

    def __init__(self):
        self.businesses: Dict[str, Business] = {}
        self.owner_index: Dict[str, List[str]] = {}

    def create_business(self, owner: str, name: str, category: str, location: str) -> Business:
        business = Business(name=name, owner=owner, category=category, location=location)
        self.businesses[name] = business
        self.owner_index.setdefault(owner, []).append(name)
        return business

    def get_business(self, name: str) -> Optional[Business]:
        return self.businesses.get(name)

    def get_owner_businesses(self, owner: str) -> List[Business]:
        return [self.businesses[name] for name in self.owner_index.get(owner, []) if name in self.businesses]

    def hire_employee(self, business_name: str, npc_name: str) -> bool:
        business = self.businesses.get(business_name)
        if not business:
            return False
        return business.hire(npc_name)

    def fire_employee(self, business_name: str, npc_name: str) -> bool:
        business = self.businesses.get(business_name)
        if not business:
            return False
        return business.fire(npc_name)
