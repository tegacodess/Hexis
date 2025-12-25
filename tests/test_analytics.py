# tests/test_analytics.py
from tests.tests_data import DAILY_4_WEEKS, WEEKLY_4_WEEKS

def test_daily_streak_4_weeks(tracker):
    # Setup data
    uid = tracker.register_user("u", "e", "p")
    hid = tracker.create_habit(uid, "H", "D", "Daily")
    
    # Run test
    for d in DAILY_4_WEEKS:
        tracker.add_completion(hid, d)
    
    res = tracker.analyze_habit(hid)
    assert res["current_streak"] == 28
    assert res["longest_streak"] == 28

def test_weekly_streak_4_weeks(tracker):
    # Setup data
    uid = tracker.register_user("u", "e", "p")
    hid = tracker.create_habit(uid, "H", "D", "Weekly")
    
    # Run test
    for d in WEEKLY_4_WEEKS:
        tracker.add_completion(hid, d)
        
    res = tracker.analyze_habit(hid)
    assert res["current_streak"] == 4
    assert res["longest_streak"] == 4