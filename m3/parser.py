#!/usr/bin/python

"""
parser.py
Sean Rettig
2015-02-16
CS 480 - Milestone 3

Parses the Itty Bitty Teaching Language (IBTL) given a list of tokens.
Run "./parser.py -i INFILE" or "./parser.py < INFILE" to use.
Run "./parser.py -h" for additional usage information.
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
        return "Token(\"{}\", \"{}\")".format(self.t, self.v)

    def __repr__(self):
        return "<{} \"{}\">".format(self.t, self.v)

# Globals
debug = 0
verbose = 0

def main():

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

    # Get tokens
    tokens = eval(infile.read())

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

#def fail(line, column, lexeme, char):
#    print "Lexing error on line {}, column {}: char '{}' can't come after lexeme '{}'.".format(line, column, char, lexeme)
#    sys.exit(2)

if __name__ == '__main__':
    main()
