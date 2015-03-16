#!/usr/bin/python

"""
lexer.py
Sean Rettig
2015-01-30
CS 480 - Milestone 2

Lexes the Itty Bitty Teaching Language (IBTL).
Run "./lexer.py -i INFILE" or "./lexer.py < INFILE" to use.
Run "./lexer.py -h" for additional usage information.
"""

from __future__ import division
import getopt
import math
import os
import sys

from token import *

class State(object):
    def __init__(self, number, tokentype, transitions):
        self.number = number # The state's number
        self.tokentype = tokentype # The type of token this state produces if it's an accept/final state (None for reject state)
        self.transitions = transitions # A dict that maps sets of input chars to other states

    def __str__(self):
        return "State({})".format(self.number)

    def __repr__(self):
        return "{}".format(self.number)

# Constants
BUF_SIZE = 4096

# Globals
debug = 0
verbose = 0

def main():

    # Keywords
    keywords = [
            # Types
            "bool",
            "int",
            "real",
            "string",
            # Built-in functions
            "sin",
            "cos",
            "tan",
            # Statements
            "stdout",
            "if",
            "while",
            "let",
            # Logic
            "true",
            "false",
            "and",
            "or",
            "not"]

    # Character sets
    letters = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
    digits = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")

    # States of DFA
    states = {}
    addState(states, State(0, None, {
            ('+'): 1,
            ('-'): 2,
            ('*'): 3,
            ('/'): 4,
            ('%'): 5,
            ('^'): 6,
            ('='): 7,
            ('<'): 8,
            ('>'): 10,
            ('!'): 12,
            (':'): 14,
            ('('): 16,
            (')'): 17,
            ('\''): 18,
            ('"'): 20,
            letters: 22,
            digits: 23,
            ('.'): 26
    }))
    addState(states, State(1, 'PLUS', {}))
    addState(states, State(2, 'MINUS', {}))
    addState(states, State(3, 'TIMES', {}))
    addState(states, State(4, 'DIVIDE', {}))
    addState(states, State(5, 'MOD', {}))
    addState(states, State(6, 'POWER', {}))
    addState(states, State(7, 'EQ', {}))
    addState(states, State(8, 'LT', {('='): 9}))
    addState(states, State(9, 'LE', {}))
    addState(states, State(10, 'GT', {('='): 11}))
    addState(states, State(11, 'GE', {}))
    addState(states, State(12, None, {('='): 13}))
    addState(states, State(13, 'NE', {}))
    addState(states, State(14, None, {('='): 15}))
    addState(states, State(15, 'ASSIGN', {}))
    addState(states, State(16, 'OPEN', {}))
    addState(states, State(17, 'CLOSE', {}))
    addState(states, State(18, None, {(''): 18, ('\''): 19}))
    addState(states, State(19, 'STRING', {}))
    addState(states, State(20, None, {(''): 20, ('"'): 21}))
    addState(states, State(21, 'STRING', {}))
    addState(states, State(22, 'ID', {letters+digits+("_",): 22}))
    addState(states, State(23, 'INT', {digits: 23, ('e'): 24, ('.'): 27}))
    addState(states, State(24, None, {digits: 28, ('+', '-'): 25}))
    addState(states, State(25, None, {digits: 28}))
    addState(states, State(26, None, {digits: 27}))
    addState(states, State(27, 'REAL', {digits: 27, ('e'): 24}))
    addState(states, State(28, 'REAL', {digits: 28}))

    # Defaults
    infile = sys.stdin
    outfile = sys.stdout
    infilename = None
    outfilename = None

    # Parse arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dvi:o:h")
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        sys.exit(2)
    for o, a in opts:
        if o == "-d":
            global debug
            debug += 1
        elif o == "-v":
            global verbose
            verbose += 1
        elif o == "-i":
            infilename = a
        elif o == "-o":
            outfilename = a
        else:
            usage()

    # Open input file
    if infilename is not None:
        infile = open(infilename, 'r')

    # Tokenize input
    tokens = tokenize(infile, keywords, states)
    
    # Clean up input file
    infile.close()

    # Open output file
    if outfilename is not None:
        outfile = open(outfilename+".tmp", 'w')

    # Write output
    outfile.write("[" + ", ".join([str(token) for token in tokens]) + "]\n")

    # Clean up output file
    outfile.close()
    if outfilename is not None:
        os.rename(outfilename+".tmp", outfilename)

def usage():
    print 'Usage: {0} [-h] [-i infile] [-o outfile] [-a alg(s)] [-p] [-l] [-v]... [-d]...'.format(sys.argv[0])
    print '\t-h\tview this help'
    print '\t-i\tspecify an input file of IBTL code, defaults to stdin'
    print '\t-o\tspecify an output file of tokens, defaults to stdout'
    print '\t-v\tenable more verbose messages; use -vv for more even more messages'
    print '\t-d\tenable debug messages; use -dd for more even more messages'
    sys.exit(2)

def addState(states, state):
    states[state.number] = state

def fail(line, column, lexeme, char):
    print "Lexing error on line {}, column {}: char '{}' can't come after lexeme '{}'.".format(line, column, char, lexeme)
    sys.exit(2)

def tokenize(infile, keywords, states):
    """Returns a list of Tokens."""
    tokens = []
    code = infile.read()
    counter = 0
    lexeme = ""
    state = states[0]
    line = 1
    column = 0
    while counter < len(code):
        char = code[counter]
        if char == '\n':
            line += 1
            column = 0
        if char in (' ', '\t', '\n') and state != states[18] and state != states[20]: # Don't lex whitespace differently in strings
            if state == states[0]:
                counter += 1; column += 1
            else:
                if state.tokentype is not None: # If it's an accept/final state
                    tokens.append(Token(state.tokentype, lexeme)) # Houston, we have a token
                    lexeme = ""
                    nextstate = states[0] # Start over from the top of the DFA
                    counter += 1; column += 1
                else: # If it's a reject state
                    fail(line, column, lexeme, char) # <insert sad trombone>
        else:
            for matchset, matchstate in state.transitions.iteritems():
                if char in matchset:
                    lexeme += char
                    counter += 1; column += 1
                    nextstate = states[matchstate]
                    break
            else: # This happens if none of the state's transitions could handle the char
                if state == states[18] or state == states[20]: # If lexing a string, add the char anyway
                    lexeme += char
                    counter += 1; column += 1
                    nextstate = state
                elif state.tokentype is not None: # If it's an accept/final state
                    tokens.append(Token(state.tokentype, lexeme)) # Houston, we have a token
                    lexeme = ""
                    nextstate = states[0] # Start over from the top of the DFA
                else: # If it's a reject state
                    fail(line, column, lexeme, char) # <insert sad trombone>

        state = nextstate

    for token in tokens:
        if token.v in ['bool', 'int', 'real', 'string']:
            token.t = 'TYPE'
        elif token.v in keywords:
            token.t = token.v.upper()

    return tokens

if __name__ == '__main__':
    main()
