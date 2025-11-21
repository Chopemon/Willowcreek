# systems/sexual_activity_system.py
# ENHANCED SEXUAL ACTIVITY SYSTEM v1.0 — FULL PYTHON PORT
# Fully compatible with Willow Creek 2025 (simulation_v2.py)

from __future__ import annotations
from typing import Dict, List, Any, Optional
import random
from dataclasses import dataclass, field
from entities.npc import NPC


@dataclass
class SexualEncounter:
    type: str
    partner: str
    location: str
    day: int
    hour: int
    risk: int
    witnessed: bool = False
    consequences: List[str] = field(default_factory=list)


@dataclass
class SexualStatistics:
    totalEncounters: int = 0
    byType: Dict[str, int] = field(default_factory=lambda: {
        "fullSex": 0, "oral": 0, "manual": 0, "quickie": 0, "public": 0, "risky": 0
    })
    byLocation: Dict[str, int] = field(default_factory=dict)
    byPartner: Dict[str, int] = field(default_factory=dict)


@dataclass
class RiskTracking:
    publicExposures: int = 0
    closeCalls: int = 0
    witnessed: List[Dict[str, Any]] = field(default_factory=list)


class SexualActivitySystem:
    def __init__(self, simulation):
        self.sim = simulation
        self.npcs = simulation.npcs
        self.time = simulation.time

        # FIXED: 100% safe access — no crash even if malcolm doesn't exist yet
        self.malcolm = getattr(simulation, "malcolm", None) or simulation.npc_dict.get("Malcolm Newt")

        # Initialize shared state
        if not hasattr(self.sim, "sexualActivitySystem"):
            self.sim.sexualActivitySystem = {
                "activities": [],
                "statistics": SexualStatistics(),
                "riskTracking": RiskTracking()
            }

        self.sex_sys = self.sim.sexualActivitySystem
        self.activities: List[SexualEncounter] = self.sex_sys["activities"]
        self.stats: SexualStatistics = self.sex_sys["statistics"]
        self.risk: RiskTracking = self.sex_sys["riskTracking"]

        # Activity definitions
        self.activity_types = {
            "fullSex": {"keywords": ["sex", "fuck", "intercourse", "came inside", "creampie", "penetrat"],
                        "duration": "long", "intimacy": 10, "pregnancyRisk": True, "arousalRelief": 100, "energy": -30},
            "blowjob": {"keywords": ["blowjob", "blow job", "suck", "oral", "head", "fellatio"],
                        "duration": "medium", "intimacy": 7, "pregnancyRisk": False, "arousalRelief": 90, "energy": -15},
            "cunnilingus": {"keywords": ["cunnilingus", "eat out", "lick", "oral", "went down", "taste"],
                          "duration": "medium", "intimacy": 7, "pregnancyRisk": False, "arousalRelief": 85, "energy": -15},
            "handjob": {"keywords": ["handjob", "hand job", "jerk", "stroke", "manual"],
                        "duration": "short", "intimacy": 5, "pregnancyRisk": False, "arousalRelief": 70, "energy": -10},
            "fingering": {"keywords": ["finger", "manual", "touch", "rub"],
                          "duration": "short", "intimacy": 5, "pregnancyRisk": False, "arousalRelief": 65, "energy": -10},
            "quickie": {"keywords": ["quickie", "quick", "fast", "hurry"],
                        "duration": "short", "intimacy": 6, "pregnancyRisk": True, "arousalRelief": 75, "energy": -20},
            "mutualMasturbation": {"keywords": ["mutual", "together", "watch", "stroke together"],
                                   "duration": "medium", "intimacy": 6, "pregnancyRisk": False, "arousalRelief": 60, "energy": -10},
        }

        # Location risk levels
        self.location_risk = {
            "Malcolm's House": {"risk": 0, "type": "private"},
            "Home": {"risk": 0, "type": "private"},
            "Bedroom": {"risk": 0, "type": "private"},
            "Car": {"risk": 2, "type": "semi-private"},
            "Parked Car": {"risk": 3, "type": "semi-private"},
            "Harmony Studio": {"risk": 1, "type": "semi-private"},
            "Bathroom": {"risk": 4, "type": "semi-public"},
            "Closet": {"risk": 5, "type": "semi-public"},
            "Storage Room": {"risk": 5, "type": "semi-public"},
            "Empty Classroom": {"risk": 6, "type": "semi-public"},
            "Locker Room": {"risk": 7, "type": "semi-public"},
            "Rick's Place": {"risk": 8, "type": "public"},
            "The Circuit": {"risk": 9, "type": "public"},
            "Willow Creek Park": {"risk": 7, "type": "public"},
            "Main Street": {"risk": 10, "type": "public"},
            "Alley": {"risk": 8, "type": "public"},
            "Woods": {"risk": 6, "type": "public"},
        }

    def detect_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        text_lower = text.lower()
        detected_type = None
        partner_name = None

        for act_type, data in self.activity_types.items():
            if any(kw in text_lower for kw in data["keywords"]):
                detected_type = act_type
                break
        if not detected_type:
            return None

        for npc in self.npcs:
            if npc.full_name == "Malcolm Newt":
                continue
            first_name = npc.full_name.split()[0].lower()
            if first_name in text_lower:
                partner_name = npc.full_name
                break

        if not partner_name:
            return None

        # FIXED: Check if malcolm exists and has current_location before accessing
        if not self.malcolm or not hasattr(self.malcolm, 'current_location') or not self.malcolm.current_location:
            print(f"[Sexual Detection] Malcolm not ready or no location set, skipping detection")
            return None

        return {
            "type": detected_type,
            "partner": partner_name,
            "location": self.malcolm.current_location,
            "day": self.time.total_days,
            "hour": self.time.hour
        }

    def calculate_risk(self, activity: Dict[str, Any]) -> int:
        base = 5
        loc_data = self.location_risk.get(activity["location"], {"risk": 5})
        base = loc_data["risk"]

        act_data = self.activity_types[activity["type"]]
        if act_data["duration"] == "long":
            base += 2
        elif act_data["duration"] == "short":
            base -= 1

        hour = self.time.hour
        if hour >= 22 or hour <= 5:
            base -= 2
        elif 12 <= hour <= 14:
            base += 2

        mal_drunk = getattr(self.malcolm.psyche, "drunkLevel", 0)
        if mal_drunk > 5:
            base += mal_drunk // 2

        partner_npc = self.sim.world.get_npc(activity["partner"])
        if partner_npc and hasattr(partner_npc, "coreTraits"):
            traits = " ".join(partner_npc.coreTraits).lower()
            if any(w in traits for w in ["exhibitionist", "thrill", "adventurous"]):
                base += 3
            if any(w in traits for w in ["shy", "reserved", "private"]):
                base -= 2

        return max(0, min(10, base))

    def process_encounter(self, activity: Dict[str, Any], narrative_text: str = ""):
        act_data = self.activity_types[activity["type"]]
        risk = self.calculate_risk(activity)

        encounter = SexualEncounter(
            type=activity["type"],
            partner=activity["partner"],
            location=activity["location"],
            day=activity["day"],
            hour=activity["hour"],
            risk=risk
        )
        self.activities.append(encounter)

        self.stats.totalEncounters += 1
        if activity["type"] in ["blowjob", "cunnilingus"]:
            self.stats.byType["oral"] += 1
        elif activity["type"] in ["handjob", "fingering", "mutualMasturbation"]:
            self.stats.byType["manual"] += 1
        else:
            self.stats.byType[activity["type"]] += 1

        if risk >= 6:
            self.stats.byType["risky"] += 1
        if risk >= 8:
            self.stats.byType["public"] += 1

        self.stats.byLocation[activity["location"]] = self.stats.byLocation.get(activity["location"], 0) + 1
        self.stats.byPartner[activity["partner"]] = self.stats.byPartner.get(activity["partner"], 0) + 1
        # Apply effects to Malcolm – SAFE
        if self.malcolm is not None:
            self.malcolm.needs.horny = max(0, self.malcolm.needs.horny - act_data["arousalRelief"])
            self.malcolm.needs.energy = max(0, self.malcolm.needs.energy + act_data["energy"])

        rel = self.malcolm.relationships.get(activity["partner"], {})
        if rel:
            rel["level"] = rel.get("level", 0) + 1
            rel["attraction"] = rel.get("attraction", 0) + 5
            sexual = rel.get("sexual", {})
            sexual["active"] = True
            sexual["lastTime"] = activity["day"]
            sexual["frequency"] = sexual.get("frequency", 0) + 1
            variety = sexual.get("variety", [])
            if activity["type"] not in variety:
                variety.append(activity["type"])
            sexual["variety"] = variety
            rel["sexual"] = sexual
            self.malcolm.relationships[activity["partner"]] = rel

        if risk > 0 and random.random() * 10 < risk:
            witness = random.choice([n.full_name for n in self.npcs if n.full_name != "Malcolm Newt"])
            encounter.witnessed = True
            encounter.consequences.append(f"Witnessed by {witness}")
            self.risk.publicExposures += 1
            self.risk.witnessed.append({"witness": witness, "day": activity["day"]})

            self.sim.reputation.spread_gossip(
                f"{self.malcolm.full_name} and {activity['partner']} caught in {activity['type']} at {activity['location']}!"
            )
            print(f"SEXUAL EXPOSURE: Witnessed by {witness}!")

        desc = {
            "fullSex": "Full penetrative sex",
            "blowjob": "Oral sex (fellatio)",
            "cunnilingus": "Oral sex (cunnilingus)",
            "quickie": "Fast, urgent encounter",
            "handjob": "Manual stimulation",
            "fingering": "Manual stimulation",
            "mutualMasturbation": "Mutual masturbation"
        }.get(activity["type"], activity["type"])

        return f"[SEXUAL: {desc} with {activity['partner']} at {activity['location']} | Risk: {risk}/10]"

    def detect_and_process(self, text: str) -> Optional[str]:
        activity = self.detect_from_text(text)
        if activity:
            return self.process_encounter(activity, text)
        return None

    def try_autonomous_behavior(self):
        if self.malcolm is None:
            return  # Malcolm not ready yet
        if self.malcolm.needs.horny > 80:
            loc_risk = self.location_risk.get(self.malcolm.current_location, {"risk": 5})["risk"]
            if loc_risk == 0:
                print(f"[AROUSAL] Malcolm is extremely horny in private — relief possible.")
            elif loc_risk >= 7 and random.random() < 0.15:
                print(f"[AROUSAL] Malcolm having risky thoughts in {self.malcolm.current_location}...")