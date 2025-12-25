# conftest.py
import pytest
import tempfile
import shutil
import os
from habit.tracker import HabitTracker

@pytest.fixture
def tracker():
    # 1. SETUP: Create a fresh temp directory and database
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, "test.db")
    
    # Initialize the tracker with this isolated path
    t = HabitTracker(db_path=db_path)
    
    # 2. YIELD: Pass the tracker object to the test function
    yield t
    
    # 3. TEARDOWN: This runs automatically after the test finishes (even if it fails!)
    t.conn.close()
    shutil.rmtree(tmp_dir)