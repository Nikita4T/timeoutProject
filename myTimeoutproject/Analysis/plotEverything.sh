#!/bin/bash
set -e

echo "plotVehiclesReached"
python plotVehiclesReached.py
echo "plotVehiclesReachedMean"
python plotVehiclesReachedMean.py
echo "plotTimeAllVehiclesReached"
python plotTimeAllVehiclesReached.py
echo "plotMessageOverheadAllVehiclesReached"
python plotMessageOverheadAllVehiclesReached.py
echo "plotMessageOverheadAllVehiclesReachedMean"
python plotMessageOverheadAllVehiclesReachedMean.py

