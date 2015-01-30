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
    letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

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
    tokens = tokenize(infile, keywords, letters, digits)
    
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

def fail(line, column, char):
    print "Lexing error on line {}, column {}: char '{}' not in language.".format(line, column, char)
    sys.exit(2)

def tokenize(infile, keywords, letters, digits):
    """Returns a list of Tokens."""
    tokens = []
    code = infile.read()
    counter = 0
    lexeme = ""
    tokentype = None
    state = 0
    line = 1
    column = 1
    while counter < len(code):
        char = code[counter]
        lexeme += char
        if char in [' ', '\t', '\n']:
            if lexeme != "":
                tokens.append(Token(tokentype, lexeme[:-1]))
                lexeme = ""
                state = 0
                tokentype = None
            if char == '\n':
                line += 1
                column = 1
        elif state == 0:
            if char == '+': state = 1; tokentype = 'op'
            elif char == '-': state = 2; tokentype = 'op'
            elif char == '*': state = 3; tokentype = 'op'
            elif char == '/': state = 4; tokentype = 'op'
            elif char == '%': state = 5; tokentype = 'op'
            elif char == '^': state = 6; tokentype = 'op'
            elif char == '=': state = 7; tokentype = 'op'
            elif char == '<': state = 8; tokentype = 'op'
            elif char == '>': state = 10; tokentype = 'op'
            elif char == '!': state = 12; tokentype = 'op'
            elif char == ':': state = 14; tokentype = 'op'
            elif char == '(': state = 16; tokentype = 'op'
            elif char == ')': state = 17; tokentype = 'op'
            elif char == '\'': state = 18; tokentype = 'string'
            elif char == '"': state = 20; tokentype = 'string'
            elif char in letters: state = 22; tokentype = 'id'
            elif char in digits: state = 23; tokentype = 'int'
            elif char == '.': state = 25; tokentype = 'real'
            else: fail(line, column, char)
        elif state == 23:
            if char == 'i': state = 24
            elif char == '.': state = 26; tokentype = 'real'
            elif char in digits: state = 23
            else: counter -= 1; tokens.append(Token(tokentype, lexeme[:-1])); lexeme = ""; state = 0;
        elif state == 24:
            counter -= 1; tokens.append(Token(tokentype, lexeme[:-1])); lexeme = ""; state = 0;
        elif state == 25:
            if char in digits: state = 26
            else: fail(line, column, char)
        elif state == 26:
            if char == 'f': state = 33
            elif char == 'd': state = 30
            elif char =='e': state = 27
            elif char in digits: state = 26
            else: counter -= 1; tokens.append(Token(tokentype, lexeme[:-1])); lexeme = ""; state = 0;
        elif state == 27:
            if char in ['+', '-']: state = 28
            elif char in digits: state = 29
            else: fail(line, column, char)
        elif state == 28:
            if char in digits: state = 29
            else: fail(line, column, char)
        elif state == 29:
            if char == 'f': state = 33
            elif char == 'd': state = 30
            else: counter -= 1; tokens.append(Token(tokentype, lexeme[:-1])); lexeme = ""; state = 0;
        elif state == 30:
            if char == 'f': state = 32
            elif char == 'd': state = 31
            else: counter -= 1; tokens.append(Token(tokentype, lexeme[:-1])); lexeme = ""; state = 0;
        elif state == 31:
            counter -= 1; tokens.append(Token(tokentype, lexeme[:-1])); lexeme = ""; state = 0;
        elif state == 32:
            counter -= 1; tokens.append(Token(tokentype, lexeme[:-1])); lexeme = ""; state = 0;
        elif state == 33:
            if char == 'f': state = 34
            else: counter -= 1; tokens.append(Token(tokentype, lexeme[:-1])); lexeme = ""; state = 0;
        elif state == 34:
            counter -= 1; tokens.append(Token(tokentype, lexeme[:-1])); lexeme = ""; state = 0;

        counter += 1

    return tokens

if __name__ == '__main__':
    main()
