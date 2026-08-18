#!/bin/bash
set -e

export TOTAL_REPETITIONS=1000
export NODE_COUNT=100
export SENDING_START_TIME=2

PROJECT_DIR="$HOME/workspace.omnetpp/timeout"		#Wo ist das Veins Projekt
ANALYSIS_DIR="$HOME/storage/analysis/microseconds"	#Wo sind die Analysis(graphen/veinshelper) Scripte
STORAGE_DIR="$HOME/storage"				#Wo sollen die Ergebnisse hin
SCADATA_DIR="$HOME/storage/result"			#Wo veins die sca ordner speichert
APPLICATION_DIR="$HOME/src/veins/src/veins/modules/application/traci" # Wo ist MyVeinsApp.cc
RESULTDIR_DEFAULTNAME="Timeout_0_60" #exported wird RESULT_DIR mit einem gewählten Namen später

echo
echo "===================================================================================="
echo "Überprüfe ob die Werte mit der Omnet ini und der Sumo Datei übereinstimmen:"
echo "TOTAL_REPETITIONS  = $TOTAL_REPETITIONS"
echo "--'repeat' in omnetpp.ini"
echo
echo "SENDING_START_TIME = $SENDING_START_TIME"
echo "--'*.node[*].appl.start' in omnetpp.ini"
echo
echo "SCADATA_DIR = $SCADATA_DIR"
echo "--'result-dir' in omnetpp.ini"
echo
echo "NODE_COUNT         = $NODE_COUNT"
echo "--Fahrzeuge ohne Leader in gewählter rou.xml"
echo
echo "===================================================================================="
echo 
echo "Projekt nach Änderung von Projekt Dateien immer neu builden!(Per Eclipse einen Run starten)"
echo ""
echo "Dieses Script ist stark auf Timeouts von 0-60 ms ausgelegt. Die Dateien 'move60.py' und" 
echo "('MoveCsv.py') und extractEverything müssten evtl angepasst werden wenn timeouts anders"
echo "gesetzt werden. Das sind helfer Scripte für zu viele Sca Dateien"
echo ""
read -p "Mit diesen Werten fortfahren? [Y/N] " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Abgebrochen."
    exit 1
fi

while true; do
    read -p "Wie soll der Ergebnis Ordner heißen? Enter für Standard [$RESULTDIR_DEFAULTNAME]: " RESULT_NAME

    # Falls Enter gedrückt wurde, Standardnamen verwenden
    RESULT_NAME="${RESULT_NAME:-$RESULTDIR_DEFAULTNAME}"

    export RESULT_DIR="$STORAGE_DIR/$RESULT_NAME"

    if [[ -e "$RESULT_DIR" ]]; then
        echo "Ordner existiert bereits: $RESULT_DIR"
        echo "Ordne den in die Daten ein oder gib einen anderen Namen ein."
    else
        mkdir -p "$RESULT_DIR/plots"
        export PLOT_OUTPUT_DIR="$RESULT_DIR/plots"
        echo "Datenablage- und Plotordner angelegt: $RESULT_DIR/plots"
        cp "$PROJECT_DIR/omnetpp.ini" "$RESULT_DIR/"
	echo "omnetpp.ini kopiert nach: $RESULT_DIR"
	cp "$PROJECT_DIR/line.sumocfg" "$RESULT_DIR/"
	echo "line.sumocfg kopiert nach: $RESULT_DIR"
	cp "$APPLICATION_DIR/MyVeinsApp.cc" "$RESULT_DIR/"
	cp "$APPLICATION_DIR/MyVeinsApp.h" "$RESULT_DIR/"
	echo "MyVeinsApp kopiert nach: $RESULT_DIR"
        break
    fi
done

echo "Starte veins_launchd"
xterm -class veins_launchd -e env SUMO_HOME=/home/veins/src/sumo-1.11.0 /home/veins/src/veins/bin/veins_launchd & LAUNCHD_PID=$!

cleanup() {
    echo "Beende veins_launchd..."
    kill "$LAUNCHD_PID" 2>/dev/null || true
}

trap cleanup EXIT

echo "starting runs"
cd "$PROJECT_DIR"
./generateRunsFile.pl | grep NoGui > runs.txt && wc -l runs.txt
python3 runmaker4.py -j $(nproc) runs.txt
mv "$SCADATA_DIR" "$RESULT_DIR/"

cd "$ANALYSIS_DIR"
echo "splitting data"
python3 move60.py
echo "converting data to csv. This may take a while"
bash extractEverything.sh
echo "move csv into one folder"
python3 MoveCsv.py
echo "plotting all plots"
bash plotEverything.sh
