"""
tests for the build_cubes code.
"""

from datetime import datetime, timedelta
from pathlib import Path

from tapbuild.utilities import load_config
from tapbuild.build_cubes import build_cubes

## for the example pygnome files:

EXAMPLE_DIR = Path(__file__).parent.parent / "locations" / "example"


def test_build_cubes():
    try:
        build_cubes(EXAMPLE_DIR / "example_tap_setup.py")
    except FileNotFoundError as err:
        print("you need to run the test_run_gnome test first")
        raise
    # assert something here?

