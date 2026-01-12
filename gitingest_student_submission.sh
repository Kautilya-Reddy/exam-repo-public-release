#!/bin/bash

INPUT_DIR=student_submissions
OUTPUT_DIR=gitingest

mkdir -p "$OUTPUT_DIR"

for student_dir in "$INPUT_DIR"/*; do
  if [ -d "$student_dir" ]; then
    ROLL_NO=$(basename "$student_dir")
    OUTPUT_FILE="$OUTPUT_DIR/$ROLL_NO.txt"

    echo "Creating gitingest for $ROLL_NO"

    uvx gitingest "$student_dir" -o "$OUTPUT_FILE" 
  fi
done
