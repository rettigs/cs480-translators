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
        self.scopeStack = []
        self.gforth = []

    def main(self):
        # Defaults
        self.infile = sys.stdin
        self.outfile = sys.stdout
        self.infilename = None
        self.outfilename = None

        self.conversions = {
                "%": "mod",
                "!=": "<>",
                "sin": "fsin",
                "cos": "fcos",
                "tan": "ftan"
        }
        self.realConversions = {
                "+": "f+",
                "-": "f-",
                "*": "f*",
                "/": "f/",
                "mod": "fmod",
                "<": "f<",
                "<=": "f<=",
                ">": "f>",
                ">=": "f>=",
                "=": "f=",
                "<>": "f<>"
        }
        self.stringConversions = {
                "+": "s+"
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
            print "Tree:"
            tree.printTree()

        # Clean up input file
        self.infile.close()

        self.varTypePass(tree.root)

        if self.verbose >= 1:
            print "Scope stack:"
            print self.scopeStack

        self.typeCastPass(tree.root)

        if self.verbose >= 1:
            print "Tree:"
            tree.printTree()

        self.gforthPass(tree.root)

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

    def varTypePass(self, node):
        for child in node.children:
            if child.value.f == 'CF' and child.value.v == 'let':
                self.letVars(child)
            else:
                self.varTypePass(child)

    def letVars(self, node):
        for child in node.children:
            var = child.value
            var.t = child.children[0].value.v.upper()
            varscope = node.value.s
            self.scopeStack.append((var, varscope))

    def typeCastPass(self, node):

        # Set types for all variable uses
        if node.value != "" and node.value.f == 'VAR':
            node.value.t = self.getVarInScope(node.value.v).t

        # Recurse through children
        for child in node.children:
            self.typeCastPass(child)

        # Infer types of expressions
        if node.value != "" and node.value.t != 'CF' and node.value.t is None:
            if len(node.children) == 1:
                node.value.t = node.children[0].value.t
            elif len(node.children) == 2:
                if node.children[0].value.t == node.children[1].value.t:
                    node.value.t = node.children[0].value.t
                else:
                    node.value.t = 'REAL'

        # Convert operations to gforth-compatible ones
        if node.value != "" and node.value.f == 'OP':
            if node.value.v in self.conversions:
                node.value.v = self.conversions[node.value.v]

        # Convert reals and strings to gforth-compatible formats
        if node.value != "" and node.value.f == 'CONST' and node.value.t == 'REAL':
            if re.search('e', node.value.v) is None:
                node.value.v = re.sub('$', 'e', node.value.v)
        if node.value != "" and node.value.f == 'CONST' and node.value.t == 'STRING':
            node.value.v = re.sub('^"', 's" ', node.value.v)

        # Convert int operations to real/string operations if necessary
        if node.value != "" and node.value.f == 'OP':
            if node.value.t == 'REAL' and node.value.v in self.realConversions:
                node.value.v = self.realConversions[node.value.v]
            if node.value.t == 'STRING' and node.value.v in self.stringConversions:
                node.value.v = self.stringConversions[node.value.v]

    def getVarInScope(self, varname):
        for symbol, scope in self.scopeStack[::-1]:
            if symbol.v == varname:
                return symbol

    def gforthPass(self, node):

        # Recurse through children
        for child in node.children:
            self.gforthPass(child)

            # Make Gforth

            self.gforth.append(child.value.v)

            if node.value != "":
                if node.value.t != child.value.t:
                    self.gforth.append('s>f')

if __name__ == '__main__':
    gforther = Gforther()
    gforther.main()
