from datetime import datetime, timedelta

from pawpal_system import Frequency, Owner, Pet, Scheduler, Task, TaskStatus


def test_mark_complete_changes_status():
    task = Task(task_name="Feed Fluffy", time=datetime(2026, 10, 27, 8, 0))
    assert task.status == TaskStatus.PENDING
    assert not task.is_complete()

    task.mark_complete()

    assert task.status == TaskStatus.COMPLETE
    assert task.is_complete()


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task(task_name="Walk Buddy", time=datetime(2026, 10, 27, 9, 0)))
    assert len(pet.get_tasks()) == 1

    pet.add_task(Task(task_name="Brush Buddy", time=datetime(2026, 10, 27, 18, 0)))
    assert len(pet.get_tasks()) == 2


def test_sort_by_time_returns_tasks_in_chronological_order():
    """Tasks added out of order, across pets, come back earliest first."""
    owner = Owner(name="Alice")
    fluffy = Pet(name="Fluffy", species="Cat")
    buddy = Pet(name="Buddy", species="Dog")
    owner.add_pet(fluffy)
    owner.add_pet(buddy)
    scheduler = Scheduler(owner)
    vet = Task(task_name="Vet Appointment", time=datetime(2026, 10, 27, 10, 0))
    feed = Task(task_name="Feed Fluffy", time=datetime(2026, 10, 27, 8, 0))
    walk = Task(task_name="Walk Buddy", time=datetime(2026, 10, 27, 9, 0))
    scheduler.add_task(fluffy, vet)
    scheduler.add_task(buddy, walk)
    scheduler.add_task(fluffy, feed)

    assert scheduler.sort_by_time() == [feed, walk, vet]


def test_complete_daily_task_creates_next_day_task():
    """Completing a daily task adds a pending copy for the same pet one day later."""
    owner = Owner(name="Alice")
    buddy = Pet(name="Buddy", species="Dog")
    owner.add_pet(buddy)
    scheduler = Scheduler(owner)
    walk = Task(
        task_name="Walk Buddy",
        time=datetime(2026, 10, 27, 9, 0),
        duration_minutes=30,
        frequency=Frequency.DAILY,
    )
    scheduler.add_task(buddy, walk)

    next_walk = scheduler.complete_task(walk)

    assert walk.is_complete()
    assert next_walk is not None and next_walk is not walk
    assert next_walk.time == walk.time + timedelta(days=1)
    assert next_walk.status == TaskStatus.PENDING
    assert next_walk.pet is buddy
    assert next_walk.task_name == walk.task_name
    assert next_walk.duration_minutes == walk.duration_minutes
    assert buddy.get_tasks() == [walk, next_walk]


def _make_filter_scheduler():
    """Owner with Fluffy (feed done, vet pending) and Buddy (walk pending)."""
    owner = Owner(name="Alice")
    fluffy = Pet(name="Fluffy", species="Cat")
    buddy = Pet(name="Buddy", species="Dog")
    owner.add_pet(fluffy)
    owner.add_pet(buddy)
    scheduler = Scheduler(owner)
    feed = Task(task_name="Feed Fluffy", time=datetime(2026, 10, 27, 8, 0))
    vet = Task(task_name="Vet Appointment", time=datetime(2026, 10, 27, 10, 0))
    walk = Task(task_name="Walk Buddy", time=datetime(2026, 10, 27, 9, 0))
    scheduler.add_task(fluffy, feed)
    scheduler.add_task(fluffy, vet)
    scheduler.add_task(buddy, walk)
    feed.mark_complete()
    return scheduler, feed, vet, walk


def test_filter_tasks_with_no_filters_returns_all():
    """With no filters, every task across all pets is returned."""
    scheduler, feed, vet, walk = _make_filter_scheduler()
    assert set(scheduler.filter_tasks()) == {feed, vet, walk}


def test_filter_tasks_by_pet_name_ignores_case_and_spaces():
    """Pet name matching ignores case and spaces; unknown names give no tasks."""
    scheduler, feed, vet, walk = _make_filter_scheduler()
    assert set(scheduler.filter_tasks(pet_name="  fLuFfY ")) == {feed, vet}
    assert scheduler.filter_tasks(pet_name="Buddy") == [walk]
    assert scheduler.filter_tasks(pet_name="Rex") == []


def test_filter_tasks_by_status():
    """Status can be a TaskStatus or its plain string value."""
    scheduler, feed, vet, walk = _make_filter_scheduler()
    assert scheduler.filter_tasks(status=TaskStatus.COMPLETE) == [feed]
    assert set(scheduler.filter_tasks(status="pending")) == {vet, walk}


def test_filter_tasks_by_pet_name_and_status():
    """Both filters together return only tasks matching both."""
    scheduler, feed, vet, walk = _make_filter_scheduler()
    assert scheduler.filter_tasks("Fluffy", TaskStatus.PENDING) == [vet]
    assert scheduler.filter_tasks("Buddy", TaskStatus.COMPLETE) == []


def _make_conflict_scheduler(*tasks):
    """Owner with two pets; tasks alternate between them so conflicts cross pets."""
    owner = Owner(name="Alice")
    fluffy = Pet(name="Fluffy", species="Cat")
    buddy = Pet(name="Buddy", species="Dog")
    owner.add_pet(fluffy)
    owner.add_pet(buddy)
    scheduler = Scheduler(owner)
    for i, task in enumerate(tasks):
        scheduler.add_task(fluffy if i % 2 == 0 else buddy, task)
    return scheduler


def test_detect_conflicts_finds_overlapping_tasks_across_pets():
    """Overlapping tasks conflict even when they belong to different pets."""
    walk = Task(task_name="Walk", time=datetime(2026, 10, 27, 8, 0), duration_minutes=60)
    feed = Task(task_name="Feed", time=datetime(2026, 10, 27, 8, 30), duration_minutes=15)
    scheduler = _make_conflict_scheduler(walk, feed)
    assert scheduler.detect_conflicts() == [(walk, feed)]


def test_detect_conflicts_returns_earlier_task_first():
    """Each pair is (earlier, later) regardless of the order tasks were added."""
    later = Task(task_name="Feed", time=datetime(2026, 10, 27, 8, 30), duration_minutes=15)
    earlier = Task(task_name="Walk", time=datetime(2026, 10, 27, 8, 0), duration_minutes=60)
    scheduler = _make_conflict_scheduler(later, earlier)
    assert scheduler.detect_conflicts() == [(earlier, later)]


def test_detect_conflicts_ignores_back_to_back_tasks():
    """A task ending exactly when the next starts is not a conflict."""
    walk = Task(task_name="Walk", time=datetime(2026, 10, 27, 8, 0), duration_minutes=30)
    feed = Task(task_name="Feed", time=datetime(2026, 10, 27, 8, 30), duration_minutes=15)
    scheduler = _make_conflict_scheduler(walk, feed)
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_same_start_with_zero_duration():
    """Zero-duration tasks at the same moment still conflict."""
    meds = Task(task_name="Meds", time=datetime(2026, 10, 27, 8, 0))
    feed = Task(task_name="Feed", time=datetime(2026, 10, 27, 8, 0))
    scheduler = _make_conflict_scheduler(meds, feed)
    assert scheduler.detect_conflicts() == [(meds, feed)]


def test_detect_conflicts_skips_completed_tasks():
    """Completed tasks are left out of conflict checks."""
    walk = Task(task_name="Walk", time=datetime(2026, 10, 27, 8, 0), duration_minutes=60)
    feed = Task(task_name="Feed", time=datetime(2026, 10, 27, 8, 30), duration_minutes=15)
    scheduler = _make_conflict_scheduler(walk, feed)
    walk.mark_complete()
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_reports_every_overlapping_pair():
    """One long task overlapping two others produces two pairs."""
    long_walk = Task(task_name="Long Walk", time=datetime(2026, 10, 27, 8, 0), duration_minutes=120)
    feed = Task(task_name="Feed", time=datetime(2026, 10, 27, 8, 30), duration_minutes=15)
    brush = Task(task_name="Brush", time=datetime(2026, 10, 27, 9, 0), duration_minutes=15)
    scheduler = _make_conflict_scheduler(long_walk, feed, brush)
    # feed ends at 8:45, so it doesn't overlap brush; the long walk overlaps both.
    assert scheduler.detect_conflicts() == [(long_walk, feed), (long_walk, brush)]


def test_task_overlaps_is_symmetric():
    """a.overlaps(b) and b.overlaps(a) give the same answer."""
    walk = Task(task_name="Walk", time=datetime(2026, 10, 27, 8, 0), duration_minutes=60)
    feed = Task(task_name="Feed", time=datetime(2026, 10, 27, 8, 30), duration_minutes=15)
    assert walk.overlaps(feed)
    assert feed.overlaps(walk)


def test_task_overlaps_edge_cases():
    """Back-to-back, same-start, and far-apart tasks are handled correctly."""
    walk = Task(task_name="Walk", time=datetime(2026, 10, 27, 8, 0), duration_minutes=30)
    back_to_back = Task(task_name="Feed", time=datetime(2026, 10, 27, 8, 30), duration_minutes=15)
    same_start = Task(task_name="Meds", time=datetime(2026, 10, 27, 8, 0))
    later = Task(task_name="Brush", time=datetime(2026, 10, 27, 12, 0), duration_minutes=15)
    assert not walk.overlaps(back_to_back)
    assert walk.overlaps(same_start)
    assert same_start.overlaps(walk)
    assert not walk.overlaps(later)
