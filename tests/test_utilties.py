
import datetime
from pathlib import Path

from tapbuild.utilities import load_config, read_start_times_file

import pytest


DATA_DIR = Path(__file__).parent / "example_files"


@pytest.mark.parametrize('filename', ['config.py',
                                      'config.yaml'
                                      ])
def test_load_config_py(filename):
    """
    test loading a python file
    """
    config = load_config(DATA_DIR / filename)

    assert config.one_value == 3.1459

    assert config.a_list_of_strings == ["this", "that", "the_other"]

    assert config.Seasons == [['AllYear', [1,2,3,4,5,6,7,8,9,10,11,12]],
                              ['Summer', [6,7,8,9,10,11]],
                              ['Winter', [12,1,2,3,4,5]],
                              ]

def test_read_startimes_file():
    starts = read_start_times_file(DATA_DIR / "SummerStarts.txt", 10)

    assert len(starts) == 10
    for s in starts:
        assert isinstance(s, datetime.datetime)

    # If you don't have enough start time in the file, it should raise
    with pytest.raises(ValueError):
        starts = read_start_times_file(DATA_DIR / "SummerStarts.txt", 1000)



