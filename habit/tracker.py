from datetime import timezone, datetime, date, timedelta
import hashlib
from typing import List, Tuple, Optional
import sqlite3
from .database import ensure_db


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def iso_week_index(d: date) -> int:
    return d.toordinal() // 7


def month_index(d: date) -> int:
    return d.year * 12 + d.month


class HabitTracker:
    def __init__(self, db_path: Optional[str] = None):
        self.conn = ensure_db(db_path) if db_path else ensure_db()
        self.conn.row_factory = sqlite3.Row

    # ---------- User management ----------
    def register_user(self, username: str, email: str, password: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        pw_hash = hash_password(password)

        try:
            cur = self.conn.execute(
                "INSERT INTO users (username,email,password,created_at) VALUES (?,?,?,?)",
                (username, email, pw_hash, now),
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("Username already exists")

    def login(self, username: str, password: str) -> Optional[int]:
        pw_hash = hash_password(password)
        row = self.conn.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username, pw_hash),
        ).fetchone()
        return row["id"] if row else None

    # ---------- Habit CRUD ----------
    def create_habit(
        self, user_id: int, name: str, description: str, frequency: str
    ) -> int:
        if frequency not in ("Daily", "Weekly", "Monthly"):
            raise ValueError("frequency must be one of Daily, Weekly, Monthly")

        now = datetime.now(timezone.utc).isoformat()
        cur = self.conn.execute(
            """INSERT INTO habits
               (user_id,name,description,frequency,created_at,updated_at)
               VALUES (?,?,?,?,?,?)""",
            (user_id, name, description, frequency, now, now),
        )
        self.conn.commit()
        return cur.lastrowid

    def list_habits(self, user_id: int) -> List[dict]:
        rows = self.conn.execute(
            "SELECT * FROM habits WHERE user_id=? ORDER BY id",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def delete_habit(self, habit_id: int, remove_history: bool = True):
        if remove_history:
            self.conn.execute(
                "DELETE FROM habit_completion WHERE habit_id=?",
                (habit_id,),
            )
        self.conn.execute("DELETE FROM habits WHERE id=?", (habit_id,))
        self.conn.commit()

    # ---------- Completions & analysis ----------
    def add_completion(self, habit_id: int, completion_date: Optional[date] = None):
        completion_date = completion_date or date.today()
        iso_date = completion_date.isoformat()

        habit = self.conn.execute(
            "SELECT frequency FROM habits WHERE id=?", (habit_id,)
        ).fetchone()
        if not habit:
            raise ValueError("Habit not found")

        exists = self.conn.execute(
            "SELECT 1 FROM habit_completion WHERE habit_id=? AND date=?",
            (habit_id, iso_date),
        ).fetchone()

        if not exists:
            self.conn.execute(
                "INSERT INTO habit_completion (habit_id,date) VALUES (?,?)",
                (habit_id, iso_date),
            )

        current, longest = self._recalc_streaks_for_habit(
            habit_id, habit["frequency"]
        )

        self.conn.execute(
            """UPDATE habits
               SET last_checked=?, current_streak=?, longest_streak=?, updated_at=?
               WHERE id=?""",
            (iso_date, current, longest, datetime.now(timezone.utc).isoformat(), habit_id),
        )
        self.conn.commit()

    def _get_completion_dates(self, habit_id: int) -> List[date]:
        rows = self.conn.execute(
            "SELECT date FROM habit_completion WHERE habit_id=? ORDER BY date",
            (habit_id,),
        ).fetchall()

        dates = []
        for r in rows:
            d = r["date"]
            if isinstance(d, str):
                dates.append(datetime.fromisoformat(d).date())
            elif isinstance(d, datetime):
                dates.append(d.date())
            else:
                dates.append(d)
        return dates

    def _recalc_streaks_for_habit(
        self, habit_id: int, frequency: str
    ) -> Tuple[int, int]:
        dates = self._get_completion_dates(habit_id)
        if not dates:
            return 0, 0

        if frequency == "Daily":
            indexes = sorted(d.toordinal() for d in set(dates))
        elif frequency == "Weekly":
            indexes = sorted(iso_week_index(d) for d in set(dates))
        else:
            indexes = sorted(month_index(d) for d in set(dates))

        longest = current = 1
        for i in range(1, len(indexes)):
            if indexes[i] - indexes[i - 1] == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1

        return current, longest

    def analyze_habit(self, habit_id: int, lookback: int = 30) -> dict:
        habit = self.conn.execute(
            "SELECT * FROM habits WHERE id=?", (habit_id,)
        ).fetchone()
        if not habit:
            raise ValueError("Habit not found")

        dates = self._get_completion_dates(habit_id)
        current, longest = self._recalc_streaks_for_habit(
            habit_id, habit["frequency"]
        )

        missed = self._compute_missed_periods(
            habit["created_at"], dates, habit["frequency"], lookback
        )

        return {
            "habit": dict(habit),
            "completions": dates,
            "current_streak": current,
            "longest_streak": longest,
            "missed_periods": missed,
        }

    def _compute_missed_periods(
        self, created_at, dates: List[date], frequency: str, lookback: int
    ):
        if isinstance(created_at, str):
            created_date = datetime.fromisoformat(created_at).date()
        elif isinstance(created_at, datetime):
            created_date = created_at.date()
        else:
            created_date = created_at

        today = date.today()
        missed = []

        if frequency == "Daily":
            completed = {d.toordinal() for d in dates}
            for i in range(lookback):
                d = today - timedelta(days=i)
                if d < created_date:
                    break
                if d.toordinal() not in completed:
                    missed.append(d.isoformat())

        elif frequency == "Weekly":
            completed = {iso_week_index(d) for d in dates}
            for i in range(lookback):
                d = today - timedelta(weeks=i)
                if d < created_date:
                    break
                if iso_week_index(d) not in completed:
                    y, w, _ = d.isocalendar()
                    missed.append(f"week-{y}-W{w}")

        else:
            completed = {month_index(d) for d in dates}
            y, m = today.year, today.month
            for _ in range(lookback):
                if date(y, m, 1) < created_date:
                    break
                if y * 12 + m not in completed:
                    missed.append(f"{y}-{m:02d}")
                m -= 1
                if m == 0:
                    m = 12
                    y -= 1

        return missed
