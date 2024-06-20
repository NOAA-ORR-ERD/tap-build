"""
Example of a script to make the GNOME model.

This one starts with a save file, only 'cause that was easy ..'

The goal here is that this file will build a gnome.Model object that can then be used
in the run_pygnome.py script.

We'll see if that's plausible

Each new script for a new location will require that this file defines
a "run_model" function:

A dict of parameters will be passed to that function, used for each run.

at a minimum, that dict will have:

{'coords':(-117.211873, 32.682502),
           'name': 'Ellen',
           'run_duration':

"""

import gnome.scripting as gs



def initilize_model(config):
    """
    Set up the model with all the not-specific to the run stuff

    This will usually be more complicated -- setting up movers, currents, etc, etc.
    """
    model = gs.load_model(config.RootDir / "san_diego_bay_save.gnome")

    model.outputters.clear()

    return model


def setup_for_run(model, config, params):
    """
    run the model, after setting up the parameters needed.

    {'coords':(-117.211873, 32.682502),
               'name': 'Ellen',
               'oil_file': 'AD01438.json'},
    """

    # set the start_time:
    start_time = params['start_time']
    spill = model.spills[0]
    spill.release_time = start_time
    spill.end_release_time = start_time + params['release_duration']

    # add code to
    model.start_time = start_time
    model.duration = params['run_duration']

    return model


