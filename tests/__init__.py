import os
import sys

# Füge das Projekt-Root (eine Ebene über tests/) zum PYTHONPATH hinzu,
# damit "import projekt.backend..." funktioniert.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)