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

        # Work schedule profiles: (start_hour, end_hour, days_pattern)
        # days_pattern: "weekdays", "everyday", "rotating", "2-weeks-on-off"
        self.work_schedules = {
            "standard": (9, 17, "weekdays"),           # 9 AM - 5 PM, Mon-Fri
            "school": (8, 15, "weekdays"),             # 8 AM - 3 PM, Mon-Fri
            "retail": (10, 18, "weekdays"),            # 10 AM - 6 PM, Mon-Fri
            "restaurant_day": (7, 15, "everyday"),     # 7 AM - 3 PM, Every day
            "restaurant_evening": (16, 22, "everyday"), # 4 PM - 10 PM, Every day
            "bar": (16, 1, "everyday"),                # 4 PM - 1 AM, Every day (closes after midnight)
            "healthcare_day": (7, 15, "everyday"),     # Day shift
            "healthcare_evening": (15, 23, "everyday"), # Evening shift
            "healthcare_night": (23, 7, "everyday"),   # Night shift (wraps around)
            "police_day": (7, 15, "everyday"),         # Day shift
            "police_evening": (15, 23, "everyday"),    # Evening shift
            "police_night": (23, 7, "everyday"),       # Night shift
            "oil_rig": (0, 24, "2-weeks-on-off"),      # 24/7 for 2 weeks, then 2 weeks off
            "military": (6, 18, "weekdays"),           # Variable, using standard for now
            "flexible": (10, 16, "weekdays"),          # Part-time/flexible
        }

        # Keywords → (location, schedule_type)
        self.workplaces = {
            "teacher": ("Willow Creek High School", "school"),
            "pastor": ("Willow Creek Lutheran Church", "standard"),
            "priest": ("Willow Creek Lutheran Church", "standard"),
            "nurse": ("Willow Creek Clinic", "healthcare_day"),
            "doctor": ("Willow Creek Clinic", "healthcare_day"),
            "psychiatrist": ("Magnolia Mental Health Center", "standard"),
            "therapist": ("Voss Massage Studio", "flexible"),
            "massage": ("Voss Massage Studio", "flexible"),
            "police": ("Willow Creek Police Station", "police_day"),
            "officer": ("Willow Creek Police Station", "police_day"),
            "security": ("Willow Creek Police Station", "police_evening"),
            "librarian": ("Willow Creek Public Library", "standard"),
            "library": ("Willow Creek Public Library", "standard"),
            "barista": ("Willow Creek Mall - Food Court", "retail"),
            "waiter": ("Main Street Diner", "restaurant_day"),
            "waitress": ("Main Street Diner", "restaurant_day"),
            "server": ("Main Street Diner", "restaurant_day"),
            "chef": ("Main Street Diner", "restaurant_evening"),
            "cook": ("Main Street Diner", "restaurant_evening"),
            "retail": ("Willow Creek Mall - Retail Wing", "retail"),
            "sales": ("Willow Creek Mall - Retail Wing", "retail"),
            "clerk": ("Willow Creek Mall - Retail Wing", "retail"),
            "cashier": ("Willow Creek Mall - Retail Wing", "retail"),
            "yoga": ("Namaste Yoga Studio", "flexible"),
            "instructor": ("Namaste Yoga Studio", "flexible"),
            "grocery": ("Willow Creek Grocery", "retail"),
            "post": ("Sycamore Post Office", "standard"),
            "mail": ("Sycamore Post Office", "standard"),
            "mechanic": ("Hanson Auto Shop", "standard"),
            "carpenter": ("Thompson Carpentry", "standard"),
            "janitor": ("Willow Creek High School", "school"),
            "custodian": ("Willow Creek High School", "school"),
            "salon": ("Maple Salon", "retail"),
            "hairdresser": ("Maple Salon", "retail"),
            "bartender": ("Willow Creek Bar & Grill", "bar"),
            "road crew": ("County Roads Depot", "standard"),
            "road worker": ("County Roads Depot", "standard"),
            "bubble bloom": ("Willow Creek Mall - Food Court", "retail"),
            "food court": ("Willow Creek Mall - Food Court", "retail"),
            "artist": ("Art Cooperative", "flexible"),
            "model": ("Art Cooperative", "flexible"),
            "engineer": ("Engineering Firm", "standard"),
            "mother": ("Home", "standard"),
            "student": ("Willow Creek High School", "school"),
            "administrator": ("Lutheran Church", "standard"),
            "driver": ("Local Transportation", "standard"),
            "nightclub": ("Willow Creek Nightlife District", "bar"),
            "the circuit": ("Willow Creek Nightlife District", "bar"),
            # Military and industrial workers
            "navy": ("Lakeside Research & Seal Station", "military"),
            "seal": ("Lakeside Research & Seal Station", "military"),
            "military": ("Willow Creek Military Outpost", "military"),
            "soldier": ("Willow Creek Military Outpost", "military"),
            "oil": ("Offshore Oil Rig #7", "oil_rig"),
            "rig": ("Offshore Oil Rig #7", "oil_rig"),
        }

    # ---------------------------------------------------------
    # TIME WINDOWS
    # ---------------------------------------------------------
    def is_in_shift(self, start_hour, end_hour, current_hour):
        """Check if current hour is within shift, handling overnight shifts"""
        if end_hour > start_hour:
            # Normal shift (e.g., 9-17)
            return start_hour <= current_hour < end_hour
        else:
            # Overnight shift (e.g., 23-7)
            return current_hour >= start_hour or current_hour < end_hour

    def is_oil_rig_week(self, npc):
        """
        Oil rig workers: 2 weeks on, 2 weeks off
        Use simulation day to determine if worker is on-shift
        """
        if not hasattr(self.sim.time, 'total_days'):
            return False

        # Use NPC age as seed for staggered rotations (different workers have different schedules)
        offset = (npc.age * 7) % 14
        cycle_day = (self.sim.time.total_days + offset) % 28

        # First 14 days of cycle = on rig, next 14 days = off
        return cycle_day < 14

    def is_work_time_custom(self, npc, schedule_type):
        """
        Check if NPC should be at work based on their custom schedule
        """
        if npc.age < 19:
            return False

        if schedule_type not in self.work_schedules:
            schedule_type = "standard"

        start_hour, end_hour, days_pattern = self.work_schedules[schedule_type]

        # Check day pattern
        if days_pattern == "weekdays" and self.time.is_weekend:
            return False
        elif days_pattern == "2-weeks-on-off":
            if not self.is_oil_rig_week(npc):
                return False
            # If on oil rig week, they're there 24/7
            return True
        # "everyday" pattern works all days

        # Check time
        return self.is_in_shift(start_hour, end_hour, self.time.hour)

    def is_work_time(self, npc):
        """Legacy method for backward compatibility"""
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
        """
        Returns (location, schedule_type) tuple or (None, None) if no workplace found
        """
        aff = (npc.affiliation or "").lower()
        occ = (npc.occupation or "").lower()
        text = aff + " " + occ

        for key, (place, schedule) in self.workplaces.items():
            if key in text:
                return place, schedule

        return None, None

    # ---------------------------------------------------------
    # MAIN LOCATION ASSIGNMENT
    # ---------------------------------------------------------
    def update_locations(self):
        t = self.time

        for npc in self.npcs:
            home = getattr(npc, "home_location", "Home")

            # Toddlers
            if npc.age < 3:
                npc.current_location = home
                continue

            # Daycare (3–5)
            if 3 <= npc.age <= 5:
                if self.is_daycare_time():
                    npc.current_location = "Willow Creek Daycare Center"
                else:
                    npc.current_location = home
                continue

            # Preschool (6)
            if npc.age == 6:
                if self.is_preschool_time():
                    npc.current_location = "Willow Creek Pre-School"
                else:
                    npc.current_location = home
                continue

            # School (7–18)
            if self.is_school_time(npc):
                npc.current_location = "Willow Creek High School"
                continue

            # Work (with custom schedules)
            workplace, schedule_type = self._detect_workplace(npc)

            if workplace and schedule_type:
                if self.is_work_time_custom(npc, schedule_type):
                    npc.current_location = workplace
                    continue

                # Lunch break (only for standard day shifts, not night/oil rig workers)
                if schedule_type in ["standard", "school", "retail"] and self.is_lunch_time() and npc.age >= 19:
                    npc.current_location = "Main Street Diner"
                    continue

            # Weekend → free roam
            if t.is_weekend:
                loc = self.choose_default_location(npc)
                npc.current_location = loc
                continue

            # Evening free time
            if 17 <= t.hour < 21:
                loc = self.choose_default_location(npc)
                npc.current_location = loc
                continue

            # Night → home
            if t.hour >= 21 or t.hour < 6:
                npc.current_location = home
                continue

            # Weekday day with no job
            if 8 <= t.hour < 17:
                npc.current_location = home
                continue

            # Fallback
            loc = self.choose_default_location(npc)
            npc.current_location = loc
