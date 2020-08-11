#!/bin/bash

# bash script that executes WoZ -> Behavior Tree Pipeline
# Written by Adam Wathieu, 2020
# USC REU Summer 2020

config=$1
outputFile="output.log"
errorFile="error.log"
fmt_format=""

# outputPath=jq .outputPackage_path $config
# parameter="$outputPath$outputFile"
# echo $parameter


# echo $config
# > $outputFile 2> $errorFile
echo 'Starting Cleaning Processes...'
sleep 1
echo -ne '    [normalizing...] [                     ]   (0%)\r'
python3 0_normalize1.py -config $config
echo -ne '    [hotEncoding...] [#######              ]   (33%)\r'
python3 1_hotEncode1.py -config $config > $outputFile
echo -ne '    [upSampling....] [##############       ]   (66%)\r'
python3 2_upsample1.py -config $config -outputLog $outputFile
echo -ne '    [Cleaning..Done] [#####################]   (100%)\r'
echo -ne '\n'
echo 'Data Preparation Process Done'
echo 'Starting Behavior Tree Development...'
sleep 1
python3 3_behaviorTree.py -config config.json -outputLog $outputFile
echo -ne 'Done. Check OUTPUT file.\n'

