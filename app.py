from datetime import date, datetime, time

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Frequency  

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Owner: created once and kept in the session "vault" across reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
owner: Owner = st.session_state.owner
# Scheduler only holds a reference to the owner, so it's cheap to rebuild each run.
scheduler = Scheduler(owner)

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

# --- Add a pet: calls Owner.add_pet ---
st.subheader("Pets")
with st.form("add_pet_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col2:
        breed = st.text_input("Breed (optional)")
        age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        elif owner.find_pet(pet_name):
            st.error(f"{owner.name} already has a pet named {pet_name}.")
        else:
            owner.add_pet(Pet(name=pet_name.strip(), species=species, breed=breed, age=int(age)))
            st.success(f"Added {pet_name}!")

# Reserve this spot; the table is filled in after the task form runs so the
# "Tasks" count includes a task added on this rerun.
pets_table = st.empty()

# --- Schedule a task: calls Scheduler.add_task ---
st.subheader("Tasks")

if not owner.get_pets():
    st.caption("Add a pet first, then you can schedule tasks for it.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        # Select by name, then look up the real Pet. Streamlit can hand back a
        # copy when the options are objects, which would break pet.owner links.
        selected_name = st.selectbox("Pet", [p.name for p in owner.get_pets()])
        pet = owner.find_pet(selected_name)
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
            task_time = st.time_input("Time", value=time(8, 0))
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            task_day = st.date_input("Date", value=date.today())
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
        description = st.text_input("Notes (optional)")

        if st.form_submit_button("Add task"):
            if not task_title.strip():
                st.error("Please enter a task title.")
            else:
                scheduler.add_task(
                    pet,
                    Task(
                        task_name=task_title.strip(),
                        time=datetime.combine(task_day, task_time),
                        description=description,
                        duration_minutes=int(duration),
                        priority=Priority[priority.upper()],
                        frequency=Frequency(frequency),
                    ),
                )
                st.success(f"Added '{task_title}' for {pet.name}.")

all_tasks = scheduler.sort_by_time()
if all_tasks:
    st.write("All tasks:")
    st.table(
        [
            {
                "When": f"{t.time:%a %b %d, %I:%M %p}",
                "Task": t.task_name,
                "Pet": t.pet.name,
                "Minutes": t.duration_minutes,
                "Priority": t.priority.name.title(),
                "Repeats": t.frequency.value,
                "Status": t.status.value,
            }
            for t in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

if owner.get_pets():
    pets_table.table(
        [
            {"Name": p.name, "Species": p.species, "Breed": p.breed, "Age": p.age,
             "Tasks": len(p.get_tasks())}
            for p in owner.get_pets()
        ]
    )
else:
    pets_table.info("No pets yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )
