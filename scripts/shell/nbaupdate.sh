#!/bin/bash
echo 
echo "Updating NBA data..."
echo
python $NBA/py/nbaupdate.py

echo
echo "Estimating regression model & predicting today's games..."
echo
# Rscript predict_nba.R

# predict_nba.R writes predictions to predictions.txt:
# format text (remove ") and email / post?
