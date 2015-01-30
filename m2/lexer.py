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

# Globals
debug = 0
verbose = 0

def main():

    # Token types
    token = {}

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

    # Read file
    if infilename is not None:
        infile = open(infilename, 'r')
    code = readFile(infile)
    infile.close()

    # Tokenize input
    #tokens = ???

    # Write output
    if outfilename is not None:
        outfile = open(outfilename+".tmp", 'w')
    writeFile(outfile, tokens)
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

def readFile(infile):
    return infile.read()

def writeFile(outfile, tokens):
    outfile.write(tokens)

if __name__ == '__main__':
    main()
