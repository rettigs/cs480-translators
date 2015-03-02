#!/usr/bin/python

"""
Converts the output of parsetree.py to gforth.
"""

from __future__ import division
import getopt
import math
import os
import pickle
import re
import sys
import time

from token import *
from tree import *

class Gforther(object):

    def __init__(self):
        self.debug = 0
        self.verbose = 0
        self.tokens = []
        self.gforth = []

    def main(self):
        # Defaults
        self.infile = sys.stdin
        self.outfile = sys.stdout
        self.infilename = None
        self.outfilename = None

        self.conversions = {
                "+": "f+",
                "-": "f-",
                "*": "f*",
                "/": "f/",
                "%": "fmod",
                "<": "f<",
                "<=": "f<=",
                ">": "f>",
                ">=": "f>=",
                "=": "f=",
                "!=": "f<>",
                "sin": "fsin",
                "cos": "fcos",
                "tan": "ftan",
        }

        # Parse arguments
        try:
            opts, args = getopt.getopt(sys.argv[1:], "dvi:o:h")
        except getopt.GetoptError as err:
            # print help information and exit:
            print str(err) # will print something like "option -a not recognized"
            sys.exit(2)
        for o, a in opts:
            if o == "-d":
                self.debug += 1
            elif o == "-v":
                self.verbose += 1
            elif o == "-i":
                self.infilename = a
            elif o == "-o":
                self.outfilename = a
            else:
                self.usage()

        # Open input file
        if self.infilename is not None:
            self.infile = open(self.infilename, 'r')

        # Get parse tree
        tree = pickle.load(self.infile)

        if self.verbose >= 1:
            print ""
            tree.printTree()

        # Clean up input file
        self.infile.close()

        self.traverse(tree.root)
        self.convertTokens()

        # Open output file
        if self.outfilename is not None:
            self.outfile = open(self.outfilename+".tmp", 'w')

        # Write output
        self.outfile.write(" ".join(self.gforth)+"\n")

        # Clean up output file
        self.outfile.close()
        if self.outfilename is not None:
            os.rename(self.outfilename+".tmp", self.outfilename)

    def usage(self):
        print 'Usage: {0} [-h] [-i infile] [-o outfile] [-v]... [-d]...'.format(sys.argv[0])
        print '\t-h\tview this help'
        print '\t-i\tspecify an input file of a list of IBTL tokens, defaults to stdin'
        print '\t-o\tspecify an output file of parse tree, defaults to stdout'
        print '\t-v\tenable more verbose messages; use -vv for more even more messages'
        print '\t-d\tenable debug messages; use -dd for more even more messages'
        sys.exit(2)

    def dprint(self, message, level=1):
        if self.debug >= level:
            print "DEBUG {}: {}".format(level, message)

    def vprint(self, message, level=1):
        if self.verbose >= level:
            print message

    def traverse(self, node):
        for child in node.children:
            self.traverse(child)
        try:
            self.tokens.append(node.value)
        except:
            pass

    def convertTokens(self):
        for token in self.tokens:
            try:
                if token.v in self.conversions:
                    token.v = self.conversions[token.v]
                self.gforth.append(token.v)
                if token.t == 'INT':
                    self.gforth.append('s>f')
            except:
                pass

if __name__ == '__main__':
    gforther = Gforther()
    gforther.main()
