"""
tests for the build_cubes code.
"""

from datetime import datetime, timedelta
from pathlib import Path

from tapbuild.utilities import load_config
from tapbuild.run_gnome import run_gnome

## for the example pygnome file:

EXAMPLE_DIR = Path(__file__).parent.parent / "locations" / "example"
DATA_DIR = Path(__file__).parent / "example_files"

# def test_build_cubes():
#     build_cubes(EXAMPLE_DIR / "example_tap_setup.py")


