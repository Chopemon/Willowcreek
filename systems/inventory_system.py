# systems/inventory_system.py
# Inventory and items system

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ItemCategory(Enum):
    """Item categories"""
    GIFT = "gift"              # Gifts for NPCs
    CONSUMABLE = "consumable"  # Food, drinks, etc.
    CLOTHING = "clothing"      # Wearable items
    TOOL = "tool"              # Useful items
    KEY_ITEM = "key_item"      # Important story items
    MISC = "misc"              # Miscellaneous


class ItemEffect(Enum):
    """What an item does when used"""
    RESTORE_ENERGY = "restore_energy"
    RESTORE_HUNGER = "restore_hunger"
    BOOST_MOOD = "boost_mood"
    INCREASE_RELATIONSHIP = "increase_relationship"
    UNLOCK_DIALOGUE = "unlock_dialogue"


@dataclass
class Item:
    """Base item class"""
    id: str
    name: str
    description: str
    category: ItemCategory
    value: int = 0  # Monetary value
    effects: Dict[ItemEffect, float] = None  # Effect -> magnitude
    consumable: bool = False
    gift_appeal: Dict[str, int] = None  # NPC personality traits -> appeal score

    def __post_init__(self):
        if self.effects is None:
            self.effects = {}
        if self.gift_appeal is None:
            self.gift_appeal = {}


class Inventory:
    """Character inventory"""

    def __init__(self, max_slots: int = 50):
        self.items: Dict[str, int] = {}  # item_id -> quantity
        self.max_slots = max_slots
        self.money: int = 500  # Starting money

    @property
    def used_slots(self) -> int:
        """Number of used inventory slots"""
        return sum(self.items.values())

    @property
    def free_slots(self) -> int:
        """Number of free slots"""
        return self.max_slots - self.used_slots

    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """Add item to inventory. Returns True if successful."""
        if self.free_slots < quantity:
            return False

        self.items[item_id] = self.items.get(item_id, 0) + quantity
        return True

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove item from inventory. Returns True if successful."""
        if item_id not in self.items or self.items[item_id] < quantity:
            return False

        self.items[item_id] -= quantity
        if self.items[item_id] <= 0:
            del self.items[item_id]
        return True

    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory contains item"""
        return self.items.get(item_id, 0) >= quantity

    def get_count(self, item_id: str) -> int:
        """Get quantity of item"""
        return self.items.get(item_id, 0)

    def add_money(self, amount: int):
        """Add money"""
        self.money += amount

    def spend_money(self, amount: int) -> bool:
        """Spend money. Returns True if successful."""
        if self.money < amount:
            return False
        self.money -= amount
        return True


class InventorySystem:
    """Manages inventories for all characters"""

    def __init__(self):
        self.inventories: Dict[str, Inventory] = {}
        self.item_catalog: Dict[str, Item] = {}
        self._initialize_items()

    def _initialize_items(self):
        """Initialize the item catalog"""

        # Gifts
        self.item_catalog["flowers"] = Item(
            id="flowers",
            name="Bouquet of Flowers",
            description="A beautiful bouquet of fresh flowers",
            category=ItemCategory.GIFT,
            value=25,
            effects={ItemEffect.INCREASE_RELATIONSHIP: 10},
            gift_appeal={"romantic": 15, "nature_lover": 10}
        )

        self.item_catalog["chocolate"] = Item(
            id="chocolate",
            name="Box of Chocolates",
            description="Assorted fine chocolates",
            category=ItemCategory.GIFT,
            value=20,
            effects={ItemEffect.INCREASE_RELATIONSHIP: 8},
            gift_appeal={"sweet_tooth": 15, "romantic": 8}
        )

        self.item_catalog["book"] = Item(
            id="book",
            name="Novel",
            description="A bestselling novel",
            category=ItemCategory.GIFT,
            value=15,
            effects={ItemEffect.INCREASE_RELATIONSHIP: 7},
            gift_appeal={"intellectual": 15, "bookworm": 20}
        )

        self.item_catalog["wine"] = Item(
            id="wine",
            name="Bottle of Wine",
            description="A nice bottle of red wine",
            category=ItemCategory.GIFT,
            value=30,
            effects={ItemEffect.INCREASE_RELATIONSHIP: 12},
            gift_appeal={"sophisticated": 15, "social": 10}
        )

        # Consumables
        self.item_catalog["coffee"] = Item(
            id="coffee",
            name="Coffee",
            description="Hot coffee for energy",
            category=ItemCategory.CONSUMABLE,
            value=5,
            effects={ItemEffect.RESTORE_ENERGY: 15, ItemEffect.BOOST_MOOD: 5},
            consumable=True
        )

        self.item_catalog["energy_drink"] = Item(
            id="energy_drink",
            name="Energy Drink",
            description="Powerful energy boost",
            category=ItemCategory.CONSUMABLE,
            value=8,
            effects={ItemEffect.RESTORE_ENERGY: 30},
            consumable=True
        )

        self.item_catalog["sandwich"] = Item(
            id="sandwich",
            name="Sandwich",
            description="A filling sandwich",
            category=ItemCategory.CONSUMABLE,
            value=10,
            effects={ItemEffect.RESTORE_HUNGER: 30, ItemEffect.RESTORE_ENERGY: 5},
            consumable=True
        )

        self.item_catalog["pizza"] = Item(
            id="pizza",
            name="Pizza",
            description="Large pizza",
            category=ItemCategory.CONSUMABLE,
            value=15,
            effects={ItemEffect.RESTORE_HUNGER: 50, ItemEffect.BOOST_MOOD: 10},
            consumable=True
        )

        # Clothing
        self.item_catalog["casual_outfit"] = Item(
            id="casual_outfit",
            name="Casual Outfit",
            description="Comfortable everyday clothes",
            category=ItemCategory.CLOTHING,
            value=50
        )

        self.item_catalog["formal_outfit"] = Item(
            id="formal_outfit",
            name="Formal Outfit",
            description="Sharp formal wear",
            category=ItemCategory.CLOTHING,
            value=150,
            effects={ItemEffect.BOOST_MOOD: 5}
        )

        self.item_catalog["athletic_wear"] = Item(
            id="athletic_wear",
            name="Athletic Wear",
            description="Workout clothes",
            category=ItemCategory.CLOTHING,
            value=60
        )

    def get_inventory(self, character_name: str) -> Inventory:
        """Get or create character's inventory"""
        if character_name not in self.inventories:
            self.inventories[character_name] = Inventory()
        return self.inventories[character_name]

    def get_item(self, item_id: str) -> Optional[Item]:
        """Get item from catalog"""
        return self.item_catalog.get(item_id)

    def give_item(self, from_char: str, to_char: str, item_id: str, quantity: int = 1) -> tuple[bool, str]:
        """
        Give item from one character to another.
        Returns (success, message)
        """
        from_inv = self.get_inventory(from_char)
        to_inv = self.get_inventory(to_char)
        item = self.get_item(item_id)

        if not item:
            return False, f"Item '{item_id}' not found"

        if not from_inv.has_item(item_id, quantity):
            return False, f"{from_char} doesn't have {quantity}x {item.name}"

        if to_inv.free_slots < quantity:
            return False, f"{to_char}'s inventory is full"

        from_inv.remove_item(item_id, quantity)
        to_inv.add_item(item_id, quantity)

        return True, f"{from_char} gave {quantity}x {item.name} to {to_char}"

    def use_item(self, character_name: str, item_id: str, npc=None) -> tuple[bool, str, Dict]:
        """
        Use an item. Returns (success, message, effects_applied)
        npc: Required for applying effects
        """
        inventory = self.get_inventory(character_name)
        item = self.get_item(item_id)

        if not item:
            return False, f"Item '{item_id}' not found", {}

        if not inventory.has_item(item_id):
            return False, f"You don't have {item.name}", {}

        effects_applied = {}

        # Apply effects if NPC provided
        if npc and item.effects:
            for effect, magnitude in item.effects.items():
                if effect == ItemEffect.RESTORE_ENERGY:
                    npc.needs.energy = min(100, npc.needs.energy + magnitude)
                    effects_applied["energy"] = magnitude
                elif effect == ItemEffect.RESTORE_HUNGER:
                    npc.needs.hunger = min(100, npc.needs.hunger + magnitude)
                    effects_applied["hunger"] = magnitude
                elif effect == ItemEffect.BOOST_MOOD:
                    # Would need mood system integration
                    effects_applied["mood"] = magnitude

        # Remove item if consumable
        if item.consumable:
            inventory.remove_item(item_id, 1)

        return True, f"Used {item.name}", effects_applied

    def list_items_by_category(self, category: ItemCategory) -> List[Item]:
        """Get all items in a category"""
        return [item for item in self.item_catalog.values() if item.category == category]

    def get_inventory_summary(self, character_name: str) -> str:
        """Get readable inventory summary"""
        inventory = self.get_inventory(character_name)
        lines = [
            f"\n{character_name}'s Inventory:",
            f"Money: ${inventory.money}",
            f"Slots: {inventory.used_slots}/{inventory.max_slots}",
            "\nItems:"
        ]

        if not inventory.items:
            lines.append("  (empty)")
        else:
            for item_id, quantity in inventory.items.items():
                item = self.get_item(item_id)
                name = item.name if item else item_id
                lines.append(f"  {name} x{quantity}")

        return "\n".join(lines)
