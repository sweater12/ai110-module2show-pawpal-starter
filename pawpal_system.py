"""PawPal system classes: Owner, Pet, Task, and Scheduler.

Implements the design in diagrams/uml.mmd.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from enum import Enum, IntEnum
from itertools import combinations
from typing import Optional


class Priority(IntEnum):
    """Lower value = more urgent, so sorting ascending puts HIGH first."""

    HIGH = 1
    MEDIUM = 2
    LOW = 3


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETE = "complete"


class Frequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


# How far ahead the next copy of a repeating task is scheduled.
_REPEAT_INTERVAL = {
    Frequency.DAILY: timedelta(days=1),
    Frequency.WEEKLY: timedelta(weeks=1),
}


# eq=False: two tasks with identical fields are still different tasks,
# so list.remove() removes the exact object passed in.
@dataclass(eq=False)
class Task:
    """A single care task (feeding, walk, meds, etc.) for one pet."""

    task_name: str
    time: datetime
    description: str = ""
    duration_minutes: int = 0  # used by Scheduler.detect_conflicts for overlaps
    priority: Priority = Priority.MEDIUM
    frequency: Frequency = Frequency.ONCE
    status: TaskStatus = TaskStatus.PENDING
    # Back-link set by Pet.add_task. repr=False avoids infinite recursion.
    pet: Optional[Pet] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Validate that the duration is not negative."""
        if self.duration_minutes < 0:
            raise ValueError("duration_minutes cannot be negative")

    @property
    def end_time(self) -> datetime:
        """Return the time the task finishes (start time plus duration)."""
        return self.time + timedelta(minutes=self.duration_minutes)

    def get_task_name(self) -> str:
        """Return the task's name."""
        return self.task_name

    def get_time(self) -> datetime:
        """Return the task's scheduled start time."""
        return self.time

    def set_time(self, time: datetime) -> None:
        """Change the task's scheduled start time."""
        self.time = time

    def get_priority(self) -> Priority:
        """Return the task's priority level."""
        return self.priority

    def set_task_status(self, status: TaskStatus | str) -> None:
        """Set the task's status from a TaskStatus or its string value."""
        # TaskStatus("complete") also accepts the plain string value
        self.status = TaskStatus(status)

    def mark_complete(self) -> None:
        """Mark the task as complete."""
        self.status = TaskStatus.COMPLETE

    def is_complete(self) -> bool:
        """Return True if the task has been completed."""
        return self.status == TaskStatus.COMPLETE

    def is_overdue(self, now: datetime) -> bool:
        """A task is overdue if it is still pending and its start time has passed."""
        return not self.is_complete() and self.time < now

    def overlaps(self, other: Task) -> bool:
        """True if the two tasks' time ranges overlap.

        Tasks that start at the same moment always overlap, even with zero duration.
        Back-to-back tasks (one ends exactly when the other starts) do not.
        """
        if self.time == other.time:
            return True
        return self.time < other.end_time and other.time < self.end_time

    def next_occurrence(self) -> Optional[Task]:
        """Return a new Task for the next repeat, or None if frequency is ONCE.

        Does not add the new task anywhere; Scheduler.complete_task does that.
        """
        interval = _REPEAT_INTERVAL.get(self.frequency)
        if interval is None:
            return None
        return replace(
            self,
            time=self.time + interval,
            status=TaskStatus.PENDING,
            pet=None,
        )


@dataclass(eq=False)
class Pet:
    """A pet belonging to an owner, with its own list of tasks.

    Pet.tasks is the single source of truth for tasks.
    """

    name: str
    species: str
    breed: str = ""
    age: int = 0
    status: str = "healthy"
    # Back-link set by Owner.add_pet. repr=False avoids infinite recursion.
    owner: Optional[Owner] = field(default=None, repr=False)
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the age and link any starting tasks back to this pet."""
        if self.age < 0:
            raise ValueError("age cannot be negative")
        # Tasks passed to the constructor still need their back-link set.
        for task in self.tasks:
            task.pet = self

    def get_name(self) -> str:
        """Return the pet's name."""
        return self.name

    def get_owner(self) -> Optional[Owner]:
        """Return the pet's owner, or None if it has no owner."""
        return self.owner

    def get_species(self) -> str:
        """Return the pet's species."""
        return self.species

    def get_age(self) -> int:
        """Return the pet's age in years."""
        return self.age

    def get_status(self) -> str:
        """Return the pet's current status (for example, healthy)."""
        return self.status

    def set_status(self, status: str) -> None:
        """Update the pet's current status."""
        self.status = status

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and link the task back to it."""
        # Move the task if it currently belongs to a different pet.
        if task.pet is not None and task.pet is not self:
            task.pet.remove_task(task)
        if task not in self.tasks:
            self.tasks.append(task)
        task.pet = self

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet and clear the task's pet link."""
        self.tasks.remove(task)
        task.pet = None

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        # Return a copy so callers can't bypass add_task/remove_task.
        return list(self.tasks)


@dataclass(eq=False)
class Owner:
    """A pet owner who can have zero or more pets."""

    name: str
    email: str = ""
    phone: str = ""
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Link any starting pets back to this owner."""
        # Pets passed to the constructor still need their back-link set.
        for pet in self.pets:
            pet.owner = self

    def get_name(self) -> str:
        """Return the owner's name."""
        return self.name

    def get_pets(self) -> list[Pet]:
        """Return a copy of the owner's pet list."""
        # Return a copy so callers can't bypass add_pet/remove_pet.
        return list(self.pets)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner and link the pet back to it."""
        if pet.owner is not None and pet.owner is not self:
            pet.owner.remove_pet(pet)
        if pet not in self.pets:
            self.pets.append(pet)
        pet.owner = self

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner and clear the pet's owner link."""
        self.pets.remove(pet)
        pet.owner = None

    def find_pet(self, name: str) -> Optional[Pet]:
        """Return the first pet with this name, ignoring case (names are assumed unique)."""
        target = name.strip().lower()
        for pet in self.pets:
            if pet.name.lower() == target:
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_contact_info(self) -> str:
        """Return the owner's name, email, and phone joined into one line."""
        parts = [self.name] + [p for p in (self.email, self.phone) if p]
        return " | ".join(parts)


class Scheduler:
    """Organizes and plans tasks across all of an owner's pets.

    Does not store its own task list; tasks are read from the owner's pets
    so there is only one source of truth.
    """

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for the given owner's pets and tasks."""
        self.owner: Owner = owner

    def add_task(self, pet: Pet, task: Task) -> None:
        """Add a task to one of this owner's pets."""
        if pet.owner is not self.owner:
            raise ValueError(f"{pet.name} does not belong to {self.owner.name}")
        pet.add_task(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from whichever pet it belongs to."""
        if task.pet is None:
            raise ValueError(f"Task '{task.task_name}' is not assigned to a pet")
        task.pet.remove_task(task)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of the owner's pets."""
        # Always read through the Owner so tasks from every pet are included.
        return self.owner.get_all_tasks()

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Return only the tasks that belong to the given pet."""
        return [t for t in self.get_all_tasks() if t.pet is pet]

    def get_tasks_for_day(self, day: date) -> list[Task]:
        """Return all tasks scheduled on the given day."""
        return [t for t in self.get_all_tasks() if t.time.date() == day]

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks that are not yet complete."""
        return [t for t in self.get_all_tasks() if not t.is_complete()]

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        status: Optional[TaskStatus | str] = None,
    ) -> list[Task]:
        """Return tasks matching the given pet name and/or status; None means any.

        Pet names are matched ignoring case and surrounding spaces.
        """
        tasks = self.get_all_tasks()
        if pet_name is not None:
            target = pet_name.strip().lower()
            tasks = [t for t in tasks if t.pet is not None and t.pet.name.lower() == target]
        if status is not None:
            # TaskStatus("complete") also accepts the plain string value
            wanted = TaskStatus(status)
            tasks = [t for t in tasks if t.status == wanted]
        return tasks

    def sort_by_time(self) -> list[Task]:
        """Return all tasks sorted from earliest to latest."""
        return sorted(self.get_all_tasks(), key=lambda t: t.time)

    def sort_by_priority(self) -> list[Task]:
        """Most urgent first; tasks with equal priority are ordered by time."""
        return sorted(self.get_all_tasks(), key=lambda t: (t.priority, t.time))

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Find pairs of pending tasks whose time ranges overlap.

        Each pair is returned as (earlier task, later task). Every pair is
        checked, which is plenty fast for one owner's schedule.
        """
        tasks = sorted(self.get_pending_tasks(), key=lambda t: t.time)
        return [(a, b) for a, b in combinations(tasks, 2) if a.overlaps(b)]

    def generate_daily_plan(self, day: date) -> list[Task]:
        """Pending tasks for the day in time order; ties go to the higher priority."""
        todays = [t for t in self.get_tasks_for_day(day) if not t.is_complete()]
        return sorted(todays, key=lambda t: (t.time, t.priority))

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark the task complete and, if it repeats, add its next occurrence
        to the same pet. Returns the new task, or None if it doesn't repeat.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None and task.pet is not None:
            task.pet.add_task(next_task)
        return next_task
