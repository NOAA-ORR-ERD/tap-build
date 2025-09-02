=====
Usage
=====

Setting up a new location
=========================

To set up a new location, you must create two things:

1) The configuration -- in a yaml file

  - The idea is that all the configuration is on one place, and then all the various parts of the process can access that configuration, and everything will be kept in sync.

2) the PyGNOME code to actually run PyGNOME:

 - This is put in a python file with two functions:


.. code-block:: python

    def initialize_model(config):
        """
        Set up the model with all the not-specific to the run stuff (map, etc)

        :param config: the configuration object -- everything loaded from the configuration python or yaml file.

        :returns: A configured ``gnome.Model`` object.

        """

.. code-block:: python

    def setup_for_run(model, config, params):
        """
        Run the model, after setting up the parameters needed.

        :param model: A configured ``gnome.Model`` object usually what is returned
                      by the initialize_model function.

        :param config: The configuration object -- everything loaded from the configuration
                       python or yaml file.

        :param params: the parameters of the specific gnome run, for example::
        :type params: dict

            {'coords':(-117.211873, 32.682502),
             'name': 'Ellen',
             'oil_file': 'AD01438.json'},


        :returns: A configured ``gnome.Model`` object.

        """


Command Line Runner
===================

There are a number of steps to be done to complete a full TAP computation:

* Selecting the start times

* Running PyGNOME

* Building the Cubes

* Making the Config file for WebTAP.


Each of these steps can be accessed via the command line tapbuild command:

::

 $ tapbuild [command] config_file.yaml

The command options are:
 - `start_times`
 - `run_gnome`
 - `build_cubes`
 - `build_site`



To use TAPbuild in a project::

    import tapbuild

