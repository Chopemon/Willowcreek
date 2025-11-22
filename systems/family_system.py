# systems/family_system.py
# Family relationships and household management

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class FamilyRelation(Enum):
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    SPOUSE = "spouse"
    GRANDPARENT = "grandparent"
    GRANDCHILD = "grandchild"
    AUNT_UNCLE = "aunt_uncle"
    NIECE_NEPHEW = "niece_nephew"
    COUSIN = "cousin"


@dataclass
class Household:
    id: str
    address: str
    members: List[str] = field(default_factory=list)
    owner: Optional[str] = None
    
    def add_member(self, character_name: str):
        if character_name not in self.members:
            self.members.append(character_name)
    
    def remove_member(self, character_name: str):
        if character_name in self.members:
            self.members.remove(character_name)


class FamilySystem:
    def __init__(self):
        self.family_relations: Dict[tuple, FamilyRelation] = {}
        self.households: Dict[str, Household] = {}
        self.character_household: Dict[str, str] = {}
    
    def add_family_relation(self, person_a: str, person_b: str, relation: FamilyRelation):
        key = (person_a, person_b)
        self.family_relations[key] = relation
    
    def get_family_relation(self, person_a: str, person_b: str) -> Optional[FamilyRelation]:
        return self.family_relations.get((person_a, person_b))
    
    def are_related(self, person_a: str, person_b: str) -> bool:
        return (person_a, person_b) in self.family_relations or (person_b, person_a) in self.family_relations
    
    def get_family_members(self, character_name: str, relation_type: Optional[FamilyRelation] = None) -> List[str]:
        family = []
        for (person_a, person_b), relation in self.family_relations.items():
            if person_a == character_name:
                if relation_type is None or relation == relation_type:
                    family.append(person_b)
            elif person_b == character_name:
                if relation_type is None or self._reverse_relation(relation) == relation_type:
                    family.append(person_a)
        return family
    
    def _reverse_relation(self, relation: FamilyRelation) -> FamilyRelation:
        reverse_map = {
            FamilyRelation.PARENT: FamilyRelation.CHILD,
            FamilyRelation.CHILD: FamilyRelation.PARENT,
            FamilyRelation.GRANDPARENT: FamilyRelation.GRANDCHILD,
            FamilyRelation.GRANDCHILD: FamilyRelation.GRANDPARENT,
            FamilyRelation.AUNT_UNCLE: FamilyRelation.NIECE_NEPHEW,
            FamilyRelation.NIECE_NEPHEW: FamilyRelation.AUNT_UNCLE,
        }
        return reverse_map.get(relation, relation)
    
    def create_household(self, address: str, owner: str) -> Household:
        household_id = f"house_{len(self.households)}"
        household = Household(id=household_id, address=address, owner=owner)
        household.add_member(owner)
        self.households[household_id] = household
        self.character_household[owner] = household_id
        return household
    
    def move_in(self, character_name: str, household_id: str):
        # Remove from old household
        if character_name in self.character_household:
            old_household_id = self.character_household[character_name]
            if old_household_id in self.households:
                self.households[old_household_id].remove_member(character_name)
        
        # Add to new household
        if household_id in self.households:
            self.households[household_id].add_member(character_name)
            self.character_household[character_name] = household_id
    
    def get_household_members(self, character_name: str) -> List[str]:
        if character_name not in self.character_household:
            return []
        household_id = self.character_household[character_name]
        if household_id not in self.households:
            return []
        return self.households[household_id].members
