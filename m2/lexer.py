#!/usr/bin/python

"""
lexer.py
Sean Rettig
2015-01-30
CS 480 - Milestone 2

Lexes the Itty Bitty Teaching Language (IBTL).
"""

from __future__ import division
import getopt
import math
import os
import sys

class Token(object):
    def __init__(self, t, v):
        self.t = t # Token type, e.g. id, keyword, op, bool, int, real, string
        self.v = v # Token value

    def __str__(self):
        return "Token({}, \"{}\")".format(self.t, self.v)

    def __repr__(self):
        return "<{} \"{}\">".format(self.t, self.v)

class State(object):
    def __init__(self, number, tokentype, transitions):
        self.number = number # The state's number
        self.tokentype = tokentype # The type of token this state produces if it's an accept/final state (None for reject state)
        self.transitions = transitions # A dict that maps sets of input chars to other states

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
            ('.'): 25
    }))
    addState(states, State(1, 'op', {}))
    addState(states, State(2, 'op', {}))
    addState(states, State(3, 'op', {}))
    addState(states, State(4, 'op', {}))
    addState(states, State(5, 'op', {}))
    addState(states, State(6, 'op', {}))
    addState(states, State(7, 'op', {}))
    addState(states, State(8, 'op', {('='): 9}))
    addState(states, State(9, 'op', {}))
    addState(states, State(10, 'op', {('='): 11}))
    addState(states, State(11, 'op', {}))
    addState(states, State(12, None, {('='): 13}))
    addState(states, State(13, 'op', {}))
    addState(states, State(14, None, {('='): 15}))
    addState(states, State(15, 'op', {}))
    addState(states, State(16, 'op', {}))
    addState(states, State(17, 'op', {}))
    addState(states, State(18, None, {(''): 18, ('\''): 19}))
    addState(states, State(19, 'string', {}))
    addState(states, State(20, None, {(''): 20, ('"'): 21}))
    addState(states, State(21, 'string', {}))
    addState(states, State(22, 'id', {letters+digits+("_",): 22}))
    addState(states, State(23, 'int', {digits: 23, ('i'): 24, ('.'): 26}))
    addState(states, State(24, 'int', {}))
    addState(states, State(25, None, {digits: 26}))
    addState(states, State(26, 'real', {digits: 26, ('f'): 33, ('d'): 30, ('e'): 27}))
    addState(states, State(27, None, {digits: 29, ('+', '-'): 28}))
    addState(states, State(28, None, {digits: 29}))
    addState(states, State(29, 'real', {('f'): 33, ('d'): 30}))
    addState(states, State(30, 'real', {('f'): 32, ('d'): 31}))
    addState(states, State(31, 'real', {}))
    addState(states, State(32, 'real', {}))
    addState(states, State(33, 'real', {('f'): 34}))
    addState(states, State(34, 'real', {}))

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
    outfile.write(str(tokens) + '\n')

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

def fail(line, column, lexeme, char):
    print "Lexing error on line {}, column {} : char '{}' can't come after lexeme '{}'.".format(line, column, char, lexeme)
    sys.exit(2)

def tokenize(infile, keywords, states):
    """Returns a list of Tokens."""
    tokens = []
    code = infile.read()
    counter = 0
    lexeme = ""
    state = states[0]
    line = 1
    column = 1
    while counter < len(code):
        char = code[counter]
        for matchset, matchstate in state.transitions.iteritems():
            if char in matchset:
                lexeme += char
                counter += 1
                nextstate = states[matchstate]
                break
        else: # This happens if none of the state's transitions could handle the char
            if state.tokentype is not None: # If it's an accept/final state
                tokens.append(Token(state.tokentype, lexeme)) # Houston, we have a token
            else: # If it's a reject state
                fail(line, column, lexeme, char) # <insert sad trombone>

        state = nextstate

    return tokens

def addState(states, state):
    states[state.number] = state

if __name__ == '__main__':
    main()
