Tests for the communication between the GUI and ARMSim server versions
======================================================================

In order to test the communication with the simulator server versions, open two terminals. In one of the terminals run the next commands (fish instructions follow, adapt for bash, or try fish)::

  set -xp PATH src/qtarmsim/gcc-arm/linux64/bin/
  python src/qtarmsim/armsim/server.py 8010

In the other terminal (fish version)::

  set -p PATH src/qtarmsim/gcc-arm/linux64/bin/
  PYTHONPATH=src python -m unittest qtarmsim.test.integration.test_armsim
