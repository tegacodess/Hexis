# habit/app.py
from habit.tracker import HabitTracker
from getpass import getpass 
from datetime import datetime, date, timedelta

def input_frequency(prompt_text="Frequency (Daily/Weekly/Monthly): "):
    while True:
        freq = input(prompt_text).strip().capitalize()
        if freq in ("Daily","Weekly","Monthly"):
            return freq
        print("Invalid frequency. Choose Daily, Weekly, or Monthly.")

def run_cli():
    tracker = HabitTracker()
    print("Welcome to Hexis (CLI). DB is inside the habit/ folder.")
    while True:
        print("\n1) Register\n2) Login\n3) Quit\n")
        choice = input("Choose: ").strip()
        if choice == "1":
            u = input("Username: ").strip()
            e = input("Email (optional): ").strip()
            p = getpass("Password: ")
            try:
                uid = tracker.register_user(u, e, p)
                print("Registered id:", uid)
            except Exception as ex:
                print("Error:", ex)
        elif choice == "2":
            u = input("Username: ").strip()
            p = getpass("Password: ")
            uid = tracker.login(u, p)
            if not uid:
                print("Login failed")
                continue
            print("Logged in as", u)
            # user loop
            while True:
                print("\n1) List habits\n2) Create habit\n3) Complete habit\n4) Analyze habit\n5) Delete habit\n6) Logout\n")
                cmd = input("Cmd: ").strip()
                if cmd == "1":
                    hs = tracker.list_habits(uid)
                    if not hs:
                        print("No habits.")
                    else:
                        for h in hs:
                            print(f"[{h['id']}] {h['name']} ({h['frequency']}) - streak {h['current_streak']}/{h['longest_streak']} last_checked:{h['last_checked']}")
                elif cmd == "2":
                    name = input("Name: ").strip()
                    desc = input("Description: ").strip()
                    freq = input_frequency()
                    hid = tracker.create_habit(uid, name, desc, freq)
                    print("Created habit id:", hid)
                elif cmd == "3":
                    hid = int(input("Habit id: ").strip())
                    ds = input("Date YYYY-MM-DD or empty for today: ").strip()
                    if ds:
                        
                        try:
                            d = datetime.fromisoformat(ds).date()
                            tracker.add_completion(hid, d)
                            print("Recorded.")
                        except ValueError:
                            print("Invalid date format. Use YYYY-MM-DD.")
                            continue
                    else:
                        tracker.add_completion(hid, None)
                    print("Recorded.")
                elif cmd == "4":
                    hid = int(input("Habit id: ").strip())
                    res = tracker.analyze_habit(hid)
                    h = res["habit"]
                    print(f"Name: {h['name']} ({h['frequency']})")
                    print("Completions:", [d.isoformat() for d in res["completions"]])
                    print("Current streak:", res["current_streak"])
                    print("Longest:", res["longest_streak"])
                    print("Missed (recent):", res["missed_periods"][:10])
                elif cmd == "5":
                    hid = int(input("Habit id: ").strip())
                    rem = input("Remove history too? (y/n) [y]: ").strip().lower() or "y"
                    tracker.delete_habit(hid, remove_history=(rem=="y"))
                    print("Deleted (if existed).")
                elif cmd == "6":
                    break
                else:
                    print("Unknown.")
        elif choice == "3":
            break
        else:
            print("Unknown option.")
if __name__ == "__main__":
    run_cli()
