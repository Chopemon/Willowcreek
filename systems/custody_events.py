# systems/custody_events.py
"""
Custody event system for Milo & Ivy.
Handles Friday pickup (18:00) and Sunday return (18:00).
Triggers narrative if Malcolm is present.
"""

class CustodyEvents:
    def __init__(self):
        self.friday_warning_given = False
        self.last_day = None
        self.last_hour = None

    def check(self, sim, narrative=None):
        """
        Called every time time advances.
        sim: WillowCreekSimulation
        narrative: NarrativeChat instance (optional, for direct narrator injection)
        """
        t = sim.time
        malcolm = sim.world.get_npc("Malcolm Newt")

        # Detect time change
        if self.last_day is None:
            self.last_day = t.day_of_week
            self.last_hour = t.hour
            return

        # --- FRIDAY MORNING WARNING ---
        if t.day_of_week == 4 and 8 <= t.hour <= 12 and not self.friday_warning_given:
            tessa = sim.world.get_npc("Tessa")
            if tessa and malcolm.current_location == tessa.current_location:
                # Narrative hint only if Malcolm is near Tessa
                if narrative:
                    narrative.inject_narration(
                        f"Tessa mentions casually, without looking up, "
                        f"that Nate is picking the kids up later today."
                    )
                self.friday_warning_given = True

        # --- FRIDAY 18:00 PICKUP ---
        if t.day_of_week == 4 and self.last_hour < 18 <= t.hour:
            self._pickup_event(sim, narrative)

        # --- SUNDAY 18:00 RETURN ---
        if t.day_of_week == 6 and self.last_hour < 18 <= t.hour:
            self._return_event(sim, narrative)

        # Reset warning next week
        if t.day_of_week == 0:
            self.friday_warning_given = False

        self.last_day = t.day_of_week
        self.last_hour = t.hour

    # ------------------------------------------------------------------

    def _pickup_event(self, sim, narrative):
        malcolm = sim.world.get_npc("Malcolm Newt")
        tessa = sim.world.get_npc("Tessa")
        kids = [sim.world.get_npc("Milo"), sim.world.get_npc("Ivy")]

        # Update kid locations
        for k in kids:
            if k:
                k.current_location = "Nate's House"

        # If Malcolm isn't at Tessa's house, no narration
        if not tessa or malcolm.current_location != "Tessa's House":
            return

        if narrative:
            narrative.inject_narration(
                "A silver sedan pulls smoothly into the gravel outside Tessa's house. "
                "Nate steps out with his typical stiff posture, barely nodding as Milo and Ivy "
                "walk past Malcolm toward the car. Tessa keeps her arms wrapped around herself, "
                "eyes fixed on the ground as the car pulls away."
            )

    # ------------------------------------------------------------------

    def _return_event(self, sim, narrative):
        malcolm = sim.world.get_npc("Malcolm Newt")
        tessa = sim.world.get_npc("Tessa")
        kids = [sim.world.get_npc("Milo"), sim.world.get_npc("Ivy")]

        # Kids come back
        for k in kids:
            if k:
                k.current_location = "Tessa's House"

        # Malcolm not present → silent
        if not tessa or malcolm.current_location != "Tessa's House":
            return

        if narrative:
            narrative.inject_narration(
                "The crunch of tires on gravel draws Malcolm’s attention. "
                "Nate’s car rolls to a stop outside Tessa’s house. "
                "Ivy climbs out first, followed by Milo. "
                "Nate and Tessa exchange a brief, brittle nod before he drives off."
            )
