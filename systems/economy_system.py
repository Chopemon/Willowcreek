# systems/economy_system.py
# Business and economy system

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class JobType(Enum):
    UNEMPLOYED = "unemployed"
    RETAIL = "retail"
    OFFICE = "office"
    MEDICAL = "medical"
    EDUCATION = "education"
    SERVICE = "service"
    CREATIVE = "creative"


@dataclass
class Job:
    title: str
    job_type: JobType
    hourly_pay: int
    hours_per_week: int
    employer: str
    level: int = 1
    track: str = ""
    required_skill: str = ""
    required_level: int = 0
    
    @property
    def weekly_income(self) -> int:
        return self.hourly_pay * self.hours_per_week


@dataclass
class JobPerformance:
    performance_score: float = 50.0
    reliability: float = 1.0
    weeks_in_role: int = 0


class EconomySystem:
    def __init__(self):
        self.character_jobs: Dict[str, Job] = {}
        self.character_money: Dict[str, int] = {}
        self.character_performance: Dict[str, JobPerformance] = {}
        self.job_history: Dict[str, List[Job]] = {}
        self.available_jobs: List[Job] = self._initialize_jobs()
        self.career_ladders: Dict[str, List[Job]] = self._build_career_ladders()
    
    def _initialize_jobs(self) -> List[Job]:
        return [
            Job("Barista", JobType.SERVICE, 15, 25, "Willow Creek Cafe", level=1, track="service"),
            Job("Cafe Shift Lead", JobType.SERVICE, 20, 30, "Willow Creek Cafe", level=2, track="service"),
            Job("Cafe Manager", JobType.SERVICE, 28, 40, "Willow Creek Cafe", level=3, track="service", required_skill="charisma", required_level=3),
            Job("Retail Clerk", JobType.RETAIL, 14, 30, "General Store", level=1, track="retail"),
            Job("Retail Supervisor", JobType.RETAIL, 19, 35, "General Store", level=2, track="retail"),
            Job("Store Manager", JobType.RETAIL, 27, 40, "General Store", level=3, track="retail", required_skill="charisma", required_level=3),
            Job("Nurse", JobType.MEDICAL, 35, 40, "Willow Creek Clinic", level=1, track="medical", required_skill="intelligence", required_level=4),
            Job("Senior Nurse", JobType.MEDICAL, 42, 40, "Willow Creek Clinic", level=2, track="medical", required_skill="intelligence", required_level=5),
            Job("Teacher", JobType.EDUCATION, 30, 40, "Willow Creek School", level=1, track="education", required_skill="intelligence", required_level=3),
            Job("Head Teacher", JobType.EDUCATION, 38, 40, "Willow Creek School", level=2, track="education", required_skill="intelligence", required_level=4),
            Job("Office Admin", JobType.OFFICE, 22, 40, "Town Hall", level=1, track="office"),
            Job("Office Manager", JobType.OFFICE, 30, 40, "Town Hall", level=2, track="office", required_skill="charisma", required_level=3),
            Job("Graphic Designer", JobType.CREATIVE, 25, 35, "Willow Creek Studio", level=1, track="creative", required_skill="creativity", required_level=3),
            Job("Creative Director", JobType.CREATIVE, 38, 40, "Willow Creek Studio", level=2, track="creative", required_skill="creativity", required_level=5),
        ]

    def _build_career_ladders(self) -> Dict[str, List[Job]]:
        ladders: Dict[str, List[Job]] = {}
        for job in self.available_jobs:
            if job.track:
                ladders.setdefault(job.track, []).append(job)
        for track, jobs in ladders.items():
            ladders[track] = sorted(jobs, key=lambda j: j.level)
        return ladders
    
    def hire(self, character_name: str, job: Job):
        self.character_jobs[character_name] = job
        self.character_performance.setdefault(character_name, JobPerformance())
        self.job_history.setdefault(character_name, []).append(job)
    
    def get_job(self, character_name: str) -> Optional[Job]:
        return self.character_jobs.get(character_name)
    
    def get_money(self, character_name: str) -> int:
        return self.character_money.get(character_name, 500)  # Start with $500
    
    def add_money(self, character_name: str, amount: int):
        current = self.get_money(character_name)
        self.character_money[character_name] = current + amount
    
    def spend_money(self, character_name: str, amount: int) -> bool:
        current = self.get_money(character_name)
        if current >= amount:
            self.character_money[character_name] = current - amount
            return True
        return False
    
    def pay_weekly_wages(self):
        for character_name, job in self.character_jobs.items():
            bonus_multiplier = 1.0
            performance = self.character_performance.get(character_name)
            if performance and performance.performance_score >= 80:
                bonus_multiplier = 1.1
            self.add_money(character_name, int(job.weekly_income * bonus_multiplier))
            if performance:
                performance.weeks_in_role += 1

    def apply_for_job(
        self,
        character_name: str,
        job: Job,
        skill_levels: Optional[Dict[str, int]] = None,
    ) -> bool:
        """Attempt to apply for a job with optional skill requirements."""
        if job.required_skill and job.required_level > 0:
            skill_value = (skill_levels or {}).get(job.required_skill, 0)
            if skill_value < job.required_level:
                return False
        self.hire(character_name, job)
        return True

    def record_shift(self, character_name: str, hours_worked: int, performance: float = 1.0) -> int:
        """Log a shift and reward hourly pay. Returns money earned."""
        job = self.get_job(character_name)
        if not job:
            return 0
        earned = int(job.hourly_pay * hours_worked)
        self.add_money(character_name, earned)
        perf = self.character_performance.setdefault(character_name, JobPerformance())
        perf.performance_score = max(0.0, min(100.0, perf.performance_score + (performance - 1.0) * 10))
        perf.reliability = max(0.5, min(1.5, perf.reliability + (performance - 1.0) * 0.05))
        return earned

    def evaluate_promotions(self, character_name: str) -> Optional[Job]:
        """Promote character if performance and ladder permit; returns new job."""
        job = self.get_job(character_name)
        if not job or not job.track:
            return None
        perf = self.character_performance.get(character_name)
        if not perf or perf.performance_score < 75 or perf.weeks_in_role < 2:
            return None
        ladder = self.career_ladders.get(job.track, [])
        for next_job in ladder:
            if next_job.level == job.level + 1:
                self.hire(character_name, next_job)
                perf.performance_score = 55.0
                perf.weeks_in_role = 0
                return next_job
        return None
