.. highlight:: shell

============
Installation
============


From Source
-----------

Requirements
............

We recommend using a conda environment to work in. The requirements for
``tapbuild`` can be found in the conda_requirements.txt file, and installed with:

.. code-block:: console

   conda install --file conda_requirements.txt

``tapbuild`` also requires two packages not found on public repos:

``PyGNOME:``

https://gitlab.orr.noaa.gov/gnome/pygnome


``GnomeTools:``

https://github.com/NOAA-ORR-ERD/GnomeTools

you need the "post_gnome" package


Installing:
...........

`tapbuild` can be found here: (this is probably where you are already)

https://gitlab.orr.noaa.gov/gnome/tap/tapbuild


`tapbuild` is not (currently) available on PyPi or conda-forge. It needs to be installed from source:

To install TAPbuild, run this command in your terminal:

.. code-block:: console

    $ pip install ./

or

.. code-block:: console

   $ pip install -e ./

For an "editable" install.


