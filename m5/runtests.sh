#!/bin/bash

TESTDIR="test"

for file in `ls $TESTDIR`; do
    echo -e "Test '$file':\n"
    cat "$TESTDIR/$file" | ./lexer.py | ./parser.py | ./syntaxtree.py | ./gforther.py
    echo -e "\n"
done
