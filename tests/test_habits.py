# tests/test_habits.py
def test_create_habit(tracker):
    user_id = tracker.register_user("test", "t@t.com", "password")
    
    habit_id = tracker.create_habit(
        user_id, "Drink Water", "Hydration", "Daily"
    )
    
    habits = tracker.list_habits(user_id)
    assert len(habits) == 1
    assert habits[0]["name"] == "Drink Water"

def test_delete_habit(tracker):
    user_id = tracker.register_user("test", "t@t.com", "password")
    habit_id = tracker.create_habit(
        user_id, "Sleep Early", "", "Daily"
    )
    
    tracker.delete_habit(habit_id)
    
    habits = tracker.list_habits(user_id)
    assert len(habits) == 0