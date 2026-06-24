"""pytest configuration — add src/ to sys.path so test modules can import from it."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
