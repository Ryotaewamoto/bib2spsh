#!/bin/sh

# input file name
input_file="input.bib"

# output file name 
output_file="output.json"

# python script to write bib info to spreadsheet
python bib2spsh.py ${input_file} ${output_file}
