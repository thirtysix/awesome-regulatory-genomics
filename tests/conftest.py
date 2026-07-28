"""Make the pipeline modules importable.

They import each other flatly (``from config import ...``) because every stage
is run as a script, so ``pipeline/`` itself has to be on the path rather than
being treated as a package.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
