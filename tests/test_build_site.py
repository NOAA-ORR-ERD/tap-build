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


def test_build_site():
    # delete the site.txt file, if it exists
    (EXAMPLE_DIR / "site.txt").unlink(missing_ok=True)
    try:
        build_site(EXAMPLE_DIR / "example_tap_setup.py")
    except FileNotFoundError as err:
        print("you need to run the test_run_gnome test first")
        raise
    # at least check that the site.txt file exists, and isn't empty.
    assert len(open(EXAMPLE_DIR / "site.txt").read()) > 100

