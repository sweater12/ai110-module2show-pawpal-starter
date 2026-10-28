from pawpal_system import Owner, Pet, Task, Scheduler, Priority, TaskStatus, Frequency
from datetime import date, datetime

today = date.today()


def at(hour: int, minute: int = 0) -> datetime:
    """Return a datetime for today at the given hour and minute."""
    return datetime(today.year, today.month, today.day, hour, minute)


def print_tasks(title: str, tasks: list[Task]) -> None:
    """Print a heading and one line per task (or a note if there are none)."""
    print(f"\n{title}")
    print("-" * 50)
    if not tasks:
        print("  (no tasks)")
    for task in tasks:
        print(f"  {task.time:%a %I:%M %p}  {task.task_name:<16} [{task.pet.get_name():<6}]  "
              f"{task.priority.name.title():<6}  {task.status.value}")


owner1 = Owner(name="Alice", email="alice.pets@example.com", phone="555-1234")
pet1 = Pet(name="Fluffy", species="Cat", breed="Siamese", age=3)
pet2 = Pet(name="Buddy", species="Dog", breed="Golden Retriever", age=5)
# add_pet links both directions: owner1.pets and pet.owner
owner1.add_pet(pet1)
owner1.add_pet(pet2)

scheduler = Scheduler(owner1)

# Tasks are added out of time order on purpose, so the sorting below has work to do.
# add_task links both directions: pet.tasks and task.pet
scheduler.add_task(pet2, Task(task_name="Evening Walk", time=at(18, 30), priority=Priority.MEDIUM,
                              description="Walk Buddy around the block.", frequency=Frequency.DAILY))
vet = Task(task_name="Vet Appointment", time=at(10), priority=Priority.HIGH,
           description="Annual check-up for Fluffy.")
scheduler.add_task(pet1, vet)
scheduler.add_task(pet2, Task(task_name="Brush Buddy", time=at(15, 15), priority=Priority.LOW,
                              description="Brush out Buddy's coat."))
feed = Task(task_name="Feed Fluffy", time=at(8), priority=Priority.HIGH,
            description="Feed Fluffy her favorite cat food.", frequency=Frequency.DAILY)
scheduler.add_task(pet1, feed)
scheduler.add_task(pet2, Task(task_name="Morning Walk", time=at(9), priority=Priority.MEDIUM,
                              description="Take Buddy for a walk in the park."))
scheduler.add_task(pet1, Task(task_name="Clean Litter", time=at(12, 45), priority=Priority.LOW,
                              description="Scoop and refresh the litter box."))

# Complete two tasks so the status filter has something to separate.
scheduler.complete_task(vet)   # one-time, so nothing new is added
scheduler.complete_task(feed)  # daily, so tomorrow's copy is added automatically

print(f"PawPal Schedule for {owner1.get_name()} ({today:%A, %B %d, %Y})")

print_tasks("All tasks (in the order they were added)", scheduler.get_all_tasks())
print_tasks("Sorted by time", scheduler.sort_by_time())
print_tasks("Sorted by priority (ties broken by time)", scheduler.sort_by_priority())
print_tasks("Filter: Fluffy's tasks", scheduler.filter_tasks(pet_name="fluffy"))
print_tasks("Filter: completed tasks", scheduler.filter_tasks(status=TaskStatus.COMPLETE))
print_tasks("Filter: Buddy's pending tasks, sorted by time",
            sorted(scheduler.filter_tasks("Buddy", TaskStatus.PENDING), key=lambda t: t.time))
print_tasks("Filter: unknown pet 'Rex'", scheduler.filter_tasks(pet_name="Rex"))
print_tasks("Today's plan (pending only)", scheduler.generate_daily_plan(today))
