#!/bin/bash
#for f in $(ls json/bs_002*.json); do
for f in $(ls json/bs_004*.json); do
  f=${f#json/bs_}
  f=${f%.json}
  echo $f
  echo $f >> gameids.txt
done
