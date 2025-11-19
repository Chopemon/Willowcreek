# systems/schedule_system.py
import random

class ScheduleSystem:
    """
    Autonomous scheduling system for Willow Creek 2025.
    Contains:
      - daycare (3–5)
      - preschool (6)
      - school (7–18)
      - workplaces
      - weekend logic
      - evening social logic
      - full debug logging
    """

    def __init__(self, simulation):
        self.sim = simulation
        self.npcs = simulation.npcs
        self.time = simulation.time

        # Keywords → location
        self.workplaces = {
            "teacher": "Willow Creek High School",
            "pastor": "Willow Creek Lutheran Church",
            "priest": "Willow Creek Lutheran Church",
            "nurse": "Willow Creek Clinic",
            "doctor": "Willow Creek Clinic",
            "psychiatrist": "Magnolia Mental Health Center",
            "therapist": "Voss Massage Studio",
            "massage": "Voss Massage Studio",
            "police": "Willow Creek Police Station",
            "officer": "Willow Creek Police Station",
            "security": "Willow Creek Police Station",
            "librarian": "Willow Creek Public Library",
            "library": "Willow Creek Public Library",
            "barista": "Willow Creek Mall - Food Court",
            "waiter": "Main Street Diner",
            "waitress": "Main Street Diner",
            "server": "Main Street Diner",
            "chef": "Main Street Diner",
            "cook": "Main Street Diner",
            "retail": "Willow Creek Mall - Retail Wing",
            "sales": "Willow Creek Mall - Retail Wing",
            "clerk": "Willow Creek Mall - Retail Wing",
            "cashier": "Willow Creek Mall - Retail Wing",
            "yoga": "Namaste Yoga Studio",
            "instructor": "Namaste Yoga Studio",
            "grocery": "Willow Creek Grocery",
            "post": "Sycamore Post Office",
            "mail": "Sycamore Post Office",
            "mechanic": "Hanson Auto Shop",
            "carpenter": "Thompson Carpentry",
            "janitor": "Willow Creek High School",
            "custodian": "Willow Creek High School",
            "salon": "Maple Salon",
            "hairdresser": "Maple Salon",
            "bartender": "Willow Creek Bar & Grill",
            "road crew": "County Roads Depot",
            "road worker": "County Roads Depot",
            "bubble bloom": "Willow Creek Mall - Food Court",
            "food court": "Willow Creek Mall - Food Court",
            "artist": "Art Cooperative",
            "model": "Art Cooperative",
            "engineer": "Engineering Firm",
            "mother": "Home",
            "student": "Willow Creek High School",
            "administrator": "Lutheran Church",
            "driver": "Local Transportation",
            "nightclub": "Willow Creek Nightlife District",
            "the circuit": "Willow Creek Nightlife District",
            # Military
            "navy": "Willow Creek Naval Base",
            "seal": "Willow Creek Naval Base",
            "military": "Willow Creek Naval Base",
            "army": "Willow Creek Naval Base",
            "marine": "Willow Creek Naval Base",
            # Oil/Industrial
            "oil": "Offshore Oil Rig",
            "rig": "Offshore Oil Rig",
            "offshore": "Offshore Oil Rig",
        }

    # ---------------------------------------------------------
    # TIME WINDOWS
    # ---------------------------------------------------------
    def is_work_time(self, npc):
        if self.time.is_weekend:
            return False
        if npc.age < 19:
            return False
        return 9 <= self.time.hour < 17

    def is_school_time(self, npc):
        if npc.age < 7 or npc.age > 18:
            return False
        if self.time.is_weekend:
            return False
        return 8 <= self.time.hour < 15

    def is_daycare_time(self):
        return 7 <= self.time.hour < 17 and not self.time.is_weekend

    def is_preschool_time(self):
        return 8 <= self.time.hour < 14 and not self.time.is_weekend

    def is_lunch_time(self):
        return 12 <= self.time.hour < 13

    # ---------------------------------------------------------
    # FREE-TIME LOGIC
    # ---------------------------------------------------------
    def weighted_choice(self, table):
        r = random.random()
        total = 0
        for loc, weight in table:
            total += weight
            if r <= total:
                return loc
        return table[-1][0]

    def choose_default_location(self, npc):
        age = npc.age

        if 13 <= age <= 19:
            table = [
                ("Willow Creek Mall - Food Court", 0.30),
                ("Mall - Gaming Zone", 0.25),
                ("Bowling Alley - Arcade Section", 0.15),
                ("Downtown Café", 0.10),
                ("Willow Creek Park", 0.10),
                ("Public Library", 0.05),
                ("Friend's House", 0.05),
            ]
        elif age >= 60:
            table = [
                ("Main Street Diner", 0.25),
                ("Public Library", 0.25),
                ("Community Center", 0.20),
                ("Willow Creek Park", 0.15),
                ("Church Lounge", 0.15),
            ]
        else:
            table = [
                ("Downtown Café", 0.18),
                ("Willow Creek Mall - Retail Wing", 0.15),
                ("Mall - Food Court", 0.15),
                ("Cedar Lanes Bowling Alley", 0.10),
                ("Public Library", 0.10),
                ("Willow Creek Park", 0.10),
                ("Main Street Diner", 0.12),
                ("Community Center", 0.10),
            ]

        return self.weighted_choice(table)

    # ---------------------------------------------------------
    # DETECT WORKPLACE
    # ---------------------------------------------------------
    def _detect_workplace(self, npc):
        aff = (npc.affiliation or "").lower()
        occ = (npc.occupation or "").lower()
        text = aff + " " + occ

        for key, place in self.workplaces.items():
            if key in text:
                print(f"[DEBUG] {npc.full_name} matched job: {place}")
                return place

        print(f"[DEBUG] {npc.full_name} has no job match.")
        return None

    # ---------------------------------------------------------
    # MAIN LOCATION ASSIGNMENT
    # ---------------------------------------------------------
    def update_locations(self):
        t = self.time

        for npc in self.npcs:
            home = getattr(npc, "home_location", "Home")

            print(f"\n[DEBUG] Checking location for {npc.full_name}, Age: {npc.age}")

            # Toddlers
            if npc.age < 3:
                npc.current_location = home
                print(f"[DEBUG] {npc.full_name} (0–2) stays home.")
                continue

            # Daycare (3–5)
            if 3 <= npc.age <= 5:
                if self.is_daycare_time():
                    npc.current_location = "Willow Creek Daycare Center"
                    print(f"[DEBUG] {npc.full_name} (3–5) goes to daycare.")
                else:
                    npc.current_location = home
                    print(f"[DEBUG] {npc.full_name} (3–5) daycare closed → home.")
                continue

            # Preschool (6)
            if npc.age == 6:
                if self.is_preschool_time():
                    npc.current_location = "Willow Creek Pre-School"
                    print(f"[DEBUG] {npc.full_name} (6) goes to preschool.")
                else:
                    npc.current_location = home
                    print(f"[DEBUG] {npc.full_name} (6) preschool closed → home.")
                continue

            # School (7–18)
            if self.is_school_time(npc):
                npc.current_location = "Willow Creek High School"
                print(f"[DEBUG] {npc.full_name} (7–18) goes to school.")
                continue

            # Work
            workplace = self._detect_workplace(npc)

            if workplace and self.is_work_time(npc):
                npc.current_location = workplace
                print(f"[DEBUG] {npc.full_name} works at {workplace}.")
                continue

            # Lunch break
            if workplace and self.is_lunch_time() and npc.age >= 19:
                npc.current_location = "Main Street Diner"
                print(f"[DEBUG] {npc.full_name} lunch break → Main Street Diner.")
                continue

            # Weekend → free roam
            if t.is_weekend:
                loc = self.choose_default_location(npc)
                npc.current_location = loc
                print(f"[DEBUG] {npc.full_name} weekend free time → {loc}.")
                continue

            # Evening free time
            if 17 <= t.hour < 21:
                loc = self.choose_default_location(npc)
                npc.current_location = loc
                print(f"[DEBUG] {npc.full_name} evening free time → {loc}.")
                continue

            # Night → home
            if t.hour >= 21 or t.hour < 6:
                npc.current_location = home
                print(f"[DEBUG] {npc.full_name} night → home.")
                continue

            # Weekday day with no job
            if 8 <= t.hour < 17:
                npc.current_location = home
                print(f"[DEBUG] {npc.full_name} no work/school → home.")
                continue

            # Fallback
            loc = self.choose_default_location(npc)
            npc.current_location = loc
            print(f"[DEBUG] {npc.full_name} fallback → {loc}.")
