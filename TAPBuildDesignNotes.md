# TAP Build Design Document


## "Structure expected by WebTAP"

For each Location, there are:

- One or more "start sites" - comprising:
 - A point location
 - A "Cube" -- data from a set of individual trajectory run
   - Each Cube is a num_trajectories X num_receptor_sites X num_output_times 3-D array

- For all "start sites", there are one or more "seasons".
 - note that "season" doesn't have to be a season. But it is a collection of individual trajectories (e.g. one cube) that have something in common.

- A set of receptor sites: they can be a grid, but in the client, they are arbitrary polygons.

- A bunch of surrounding info: a map, etc.

## For the building process:

Top level "run gnome" script needs to loop though:

```
for each "season"
  for each "start site"
      for each "start time"
          run pygnome with a bunch of parameters.

```
The gnome_parameters can get passed to the run_gnome script, and away we go.


