"""PawPal system classes: Owner, Pet, Task, and Scheduler.

Skeleton generated from diagrams/uml.mmd. Method bodies are stubs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Task:
    """A single care task (feeding, walk, meds, etc.) for one pet."""

    task_name: str
    time: datetime
    description: str = ""
    duration_minutes: int = 0
    priority: str = "medium"  # "low", "medium", "high"
    frequency: str = "once"  # "once", "daily", "weekly"
    status: str = "pending"  # "pending", "complete"
    # repr/compare off to avoid infinite recursion between Task <-> Pet
    pet: Optional[Pet] = field(default=None, repr=False, compare=False)

    def get_task_name(self) -> str:
        pass

    def get_time(self) -> datetime:
        pass

    def set_time(self, time: datetime) -> None:
        pass

    def get_priority(self) -> str:
        pass

    def set_task_status(self, status: str) -> None:
        pass

    def mark_complete(self) -> None:
        pass

    def is_complete(self) -> bool:
        pass

    def is_overdue(self, now: datetime) -> bool:
        pass

    def next_occurrence(self) -> Optional[Task]:
        pass


@dataclass
class Pet:
    """A pet belonging to an owner, with its own list of tasks."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    status: str = "healthy"
    # repr/compare off to avoid infinite recursion between Pet <-> Owner
    owner: Optional[Owner] = field(default=None, repr=False, compare=False)
    tasks: list[Task] = field(default_factory=list)

    def get_name(self) -> str:
        pass

    def get_owner(self) -> Optional[Owner]:
        pass

    def get_species(self) -> str:
        pass

    def get_age(self) -> int:
        pass

    def get_status(self) -> str:
        pass

    def set_status(self, status: str) -> None:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass


@dataclass
class Owner:
    """A pet owner who can have zero or more pets."""

    name: str
    email: str = ""
    phone: str = ""
    pets: list[Pet] = field(default_factory=list)

    def get_name(self) -> str:
        pass

    def get_pets(self) -> list[Pet]:
        pass

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def find_pet(self, name: str) -> Optional[Pet]:
        pass

    def get_contact_info(self) -> str:
        pass


class Scheduler:
    """Organizes and plans tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner: Owner = owner
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        pass

    def get_tasks_for_day(self, day: date) -> list[Task]:
        pass

    def get_pending_tasks(self) -> list[Task]:
        pass

    def sort_by_time(self) -> list[Task]:
        pass

    def sort_by_priority(self) -> list[Task]:
        pass

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        pass

    def generate_daily_plan(self, day: date) -> list[Task]:
        pass

    def complete_task(self, task: Task) -> None:
        pass
