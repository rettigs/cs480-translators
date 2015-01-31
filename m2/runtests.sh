#!/bin/bash

TESTDIR="test"

for file in `ls $TESTDIR`; do
    echo -e "Test '$file':\n"
    python lexer.py -i "$TESTDIR/$file"
    echo -e "\n"
done
