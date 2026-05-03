"""
Pytest configuration file.
Adds the workspace root to the Python path so tests can import from agent module.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
"""
Pytest configuration that adds the project root to sys.path.
This allows tests to import the agent module properly.
"""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
