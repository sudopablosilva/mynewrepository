#!/bin/bash

for i in `seq 1 1 50`
do
  echo $i >> ./logs.txt
  sleep 1
done
