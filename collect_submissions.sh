#!/bin/bash

BASE_BRANCH=main
OUTPUT_DIR=student_submissions

mkdir -p "$OUTPUT_DIR"

jq -c '.[]' prs.json | while read pr; do
  PR_NUMBER=$(echo "$pr" | jq -r '.number')
  BRANCH=$(echo "$pr" | jq -r '.headRefName')
  ROLL_NO=${BRANCH#exam-}

  echo "Processing PR #$PR_NUMBER (Roll: $ROLL_NO)"

  git fetch origin pull/$PR_NUMBER/head:pr-$PR_NUMBER

  STUDENT_DIR="$OUTPUT_DIR/$ROLL_NO"
  mkdir -p "$STUDENT_DIR"

  # Get added + modified files
  FILES=$(git diff --diff-filter=AM --name-only "$BASE_BRANCH"...pr-$PR_NUMBER)

  for file in $FILES; do
    mkdir -p "$STUDENT_DIR/$(dirname "$file")"

    # Extract file from PR branch (THIS IS THE FIX)
    git show pr-$PR_NUMBER:"$file" > "$STUDENT_DIR/$file"
  done

  git branch -D pr-$PR_NUMBER
done
