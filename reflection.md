# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

In the UML Design, I added the classes that were necesarry: Owner, Pet, Task, Scheduler. 
The Owner class contains basic attributes such as the name, email, phone number, and their list of pets. The methods that were included were basic getters and setters (get_name(), get_pets(), get_contact_info(), add_pe()t), removing, and finding pets. The Owner is responsible of keeping their pets in check.

In Pet class has basic attributes just like the Owner class like their owner, species, breed, and their tasks. The methods that are included would also be getters and setters, and adding/removing tasks. The Pet class is responsible for knowing which owner they belong to and the tasks that they are supposed to do.

The Task class has attributes of task name, duration, description, priority, status, pet assigned to, etc. The methods are getters and setters, as well as come checks such as is_complete(). This class is responsible for keeping the description and necessary information for the assigned pet.

The Scheduler class has attributes of the Owner and the list of task. It has methods of getters and setters, sorting, generating daily plans, detecting any conflicts. This class is responsible for creating the correct schedule for the owner based on the tasks for their pets.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

One change that I made was storing the tasks all in one place. Before the tasks were being stored in two different places: Pet.tasks and Scheduler.tasks. Now the tasks are stored in one place, Pet.tasks. The Scheduler can get the tasks through this attribute. This will make sure that all the tasks can be the same on both end of the Pet and Scheduler.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The constraints that the scheduler will consider are the priority, the duration of the task, and any conflicts between tasks. 

I considered the constraints based on the basic of what I would expect in a daily planner personally. I would want to know the how long a task would be in order to complete all of them on time, the importance of each task, and if there are no tasks that overlap one another.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff that the scheduler makes is creating the daily plan based on the start time for each task instead of the priority level. This is reasonable because the Owner will not be behind for the schedule if there is something that needs to be done before another task.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?



**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
