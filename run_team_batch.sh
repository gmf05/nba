#!/bin/bash
declare -a teams=("ATL" "BKN" "BOS" "CHI" "CHA" "CLE" "DAL" "DEN" "DET" "GSW" "HOU" "IND" "LAC" "LAL" "MEM" "MIA" "MIL" "MIN" "NOP" "NYK" "OKC" "ORL" "PHI" "PHX" "POR" "SAC" "SAS" "TOR" "UTA" "WAS")
# echo ${#teams[@]} # check number of teams
for i in "${teams[@]}"
do
	echo $i
  ./nbastats.py $i
done

