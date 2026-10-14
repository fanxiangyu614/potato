#!/usr/bin/env python3
"""Read-only random-photo planning. No network, image reads, or generation calls."""
import sys
from pathlib import Path

# Support both direct CLI use and file-based imports used by existing callers.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from random_photo_core import *

if __name__ == '__main__':
    raise SystemExit(main())
