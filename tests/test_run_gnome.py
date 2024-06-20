"""
Testing the run_gnome script.

and the example ...
"""

from datetime import datetime, timedelta
from pathlib import Path

from tapbuild.utilities import load_config
from tapbuild.run_gnome import run_gnome

## for the example pygnome file:

EXAMPLE_DIR = Path(__file__).parent.parent / "locations" / "example"
DATA_DIR = Path(__file__).parent / "example_files"

example_run_params = {'start_time': datetime(2023, 6, 18, 12),
                  'release_duration': timedelta(hours=3),
                  'run_duration': timedelta(hours=72),
                  'start_position':'(-117.226992, 32.676416)',
                  'oil_file': EXAMPLE_DIR / 'alaska-north-slope-middle-pipeline_AD01987.json'
                  }

def test_run_example():
    config = load_config(DATA_DIR / "example_tap_setup.py")
    model_runner = load_config(EXAMPLE_DIR / "make_gnome_model.py")

    model = model_runner.initilize_model(config)

    model_runner.setup_for_run(model, config, example_run_params)

    model.full_run()


def test_run_gnome():
    run_gnome(EXAMPLE_DIR / "example_tap_setup.py")







