from datetime import date

def test_register_create_and_complete(tracker):
    # Using the tracker fixture which provides isolated DB
    uid = tracker.register_user("testuser", "t@example.com", "pass")
    assert uid is not None

    hid = tracker.create_habit(uid, "Test", "desc", "Daily")
    assert hid is not None

    tracker.add_completion(hid, date.today())
    analysis = tracker.analyze_habit(hid)
    assert analysis["current_streak"] >= 1
    assert analysis["longest_streak"] >= 1