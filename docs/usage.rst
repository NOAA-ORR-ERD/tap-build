=====
Usage
=====

Setting up a new location
=========================

To set up a new location, you must create two things:

1) The configuration -- in a yaml file
  - The idea is that all the configuration is on one place, and then all the various parts of the process can access that configuration, and everything will be kept in sync.

2) the PyGNOME code to actually run PyGNOME:
 - This


Command Line Runner
===================

There are a number of steps to be done to complete a full TAP computation:

* Selecting the start times

* Running PyGNOME

* Building the Cubes

* Making the Config file for WebTAP.
 - To Be Completed

Each of these steps can be accessed via the command line tapbuild command:

::

 $ tapbuild [command] config_file.yaml

The command options are:
 - `start_times`
 - `run_gnome`
 - `build_cubes`
 - `build_site` [build_site is yet to be finished ...]









To use TAPbuild in a project::

    import tapbuild
