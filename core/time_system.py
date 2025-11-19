# core/time_system.py
from datetime import datetime, timedelta


class TimeSystem:
    """
    Upgraded time system for Willow Creek 2025.
    Compatible with ALL older and newer systems.
    """

    def __init__(self, start_datetime: datetime):
        self.current_time: datetime = start_datetime
        self.total_days: int = 0
        self._update_internal_state()

    # -----------------------------------------------------------
    # INTERNAL STATE UPDATE
    # -----------------------------------------------------------
    def _update_internal_state(self):
        """Refresh all derived values used by multiple systems."""
        self.hour = self.current_time.hour
        self.minute = self.current_time.minute

        # Monday = 0, Sunday = 6
        self.day_of_week = self.current_time.weekday()

        # monday / tuesday / ...
        self.weekday_name = self.current_time.strftime("%A").lower()

        # Old compatibility (some systems still use this)
        self.day_name = self.weekday_name

        # Weekend?
        self.is_weekend = self.day_of_week >= 5

        # Determine season
        month = self.current_time.month
        if month in (12, 1, 2):
            self.season = "winter"
        elif month in (3, 4, 5):
            self.season = "spring"
        elif month in (6, 7, 8):
            self.season = "summer"
        else:
            self.season = "autumn"

        # Determine time-of-day phase (for older systems)
        if 0 <= self.hour < 6:
            self.time_of_day = "night"
        elif 6 <= self.hour < 12:
            self.time_of_day = "morning"
        elif 12 <= self.hour < 18:
            self.time_of_day = "afternoon"
        elif 18 <= self.hour < 22:
            self.time_of_day = "evening"
        else:
            self.time_of_day = "late"

    # -----------------------------------------------------------
    # STRING FORMATTER
    # -----------------------------------------------------------
    def get_datetime_string(self) -> str:
        return self.current_time.strftime("%A, %B %d, %Y %I:%M %p")
    
    @property
    def current_datetime(self) -> datetime:
        """Alias for current_time (for compatibility)"""
        return self.current_time

    @property
    def is_school_hours(self) -> bool:
        """School hours: 8 AM - 3 PM on weekdays"""
        return 8 <= self.hour < 15 and not self.is_weekend

    @property
    def is_business_hours(self) -> bool:
        """Business hours: 9 AM - 5 PM on weekdays"""
        return 9 <= self.hour < 17 and not self.is_weekend

    # -----------------------------------------------------------
    # ADVANCE TIME
    # -----------------------------------------------------------
    def advance(self, hours: float):
        """Advance time forward by fractional hours."""
        if hours <= 0:
            return

        delta = timedelta(hours=hours)
        old_day = self.current_time.day

        self.current_time += delta

        # Day rollover?
        if self.current_time.day != old_day:
            self.total_days += 1

        self._update_internal_state()
