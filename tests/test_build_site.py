"""
Tests for the build_cubes code.

Note: doesn't test much, but at least it tests that it runs.
"""

from datetime import datetime, timedelta
from pathlib import Path

from tapbuild.utilities import load_config
from tapbuild.build_site import build_site

## for the example pygnome file:

EXAMPLE_DIR = Path(__file__).parent.parent / "locations" / "example"
DATA_DIR = Path(__file__).parent / "full_example"


def test_build_site():
    try:
        build_site(DATA_DIR / "minimal_tap_setup.py")
    except FileNotFoundError as err:
        print("you need to run the test_run_gnome test first")
        raise
    # at least check that the site.txt file exists, and isn't empty.
    assert len(open(DATA_DIR / "site.txt").read()) > 100

