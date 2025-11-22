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
    
    @property
    def weekly_income(self) -> int:
        return self.hourly_pay * self.hours_per_week


class EconomySystem:
    def __init__(self):
        self.character_jobs: Dict[str, Job] = {}
        self.character_money: Dict[str, int] = {}
        self.available_jobs: List[Job] = self._initialize_jobs()
    
    def _initialize_jobs(self) -> List[Job]:
        return [
            Job("Barista", JobType.SERVICE, 15, 25, "Willow Creek Cafe"),
            Job("Retail Clerk", JobType.RETAIL, 14, 30, "General Store"),
            Job("Nurse", JobType.MEDICAL, 35, 40, "Willow Creek Clinic"),
            Job("Teacher", JobType.EDUCATION, 30, 40, "Willow Creek School"),
            Job("Office Admin", JobType.OFFICE, 22, 40, "Town Hall"),
        ]
    
    def hire(self, character_name: str, job: Job):
        self.character_jobs[character_name] = job
    
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
            self.add_money(character_name, job.weekly_income)
