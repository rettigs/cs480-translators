#!/usr/bin/python

"""
Converts the parse tree output of parser.py to a syntax tree.
"""

from __future__ import division
import getopt
import math
import os
import pickle
import re
import sys
import time

from symbol import *
from token import *
from tree import *

class SyntaxTree(object):

    def __init__(self):
        self.debug = 0
        self.verbose = 0
        self.tokens = []
        self.curTokenNumber = -1
        self.doReturn = False
        self.returns = 0

    def main(self):
        # Defaults
        self.infile = sys.stdin
        self.outfile = sys.stdout
        self.infilename = None
        self.outfilename = None

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

        # Get tokens
        self.tokens = []
        for line in self.infile.readlines():
            level = len(re.findall('    ', line))
            token = eval(line)
            token.level = level
            self.tokens.append(token)
        self.tokens = self.tokens[::-1]
            
        self.vprint(self.tokens, 2)

        # Create parse tree
        self.tree = Tree()
        self.tree.root.value = ""
        self.makeSyntaxTree(self.tree.root)

        if self.verbose >= 1:
            self.tree.printTree()

        # Clean up input file
        self.infile.close()

        try:
            # Open output file
            if self.outfilename is not None:
                self.outfile = open(self.outfilename+".tmp", 'w')

            # Write output
            pickle.dump(self.tree, self.outfile)

            # Clean up output file
            self.outfile.close()
            if self.outfilename is not None:
                os.rename(self.outfilename+".tmp", self.outfilename)
        except:
            pass

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

    def makeSyntaxTree(self, root):
        children = {}
        scopeDepth = 0
        children[0] = []
        tok = self.tokens
        i = self.curTokenNumber
        while i + 1 < len(tok):
            i += 1
            self.vprint("{}curToken: {}, {}".format("  "*scopeDepth, i, tok[i]), 3)
            if tok[i].t == "CLOSE":
                scopeDepth += 1
                children[scopeDepth] = []
                self.vprint("{}Found CLOSE; opening new scope".format("  "*scopeDepth), 3)
            elif tok[i].t == "OPEN":
                if i + 1 < len(tok) and tok[i+1].t == "LET":
                    children[scopeDepth-1] = children[scopeDepth]
                    del children[scopeDepth]
                    scopeDepth -= 1
                else:
                    newParent = children[scopeDepth][0]
                    newChildren = children[scopeDepth][1:]
                    self.vprint("{}Found OPEN; closing scope and setting children of '{}' to '{}'".format("  "*scopeDepth, newParent.value, [str(c.value) for c in newChildren]), 3)
                    newParent.children.extend(newChildren)

                    del children[scopeDepth]
                    scopeDepth -= 1
                    children[scopeDepth].insert(0, newParent)
            else:
                newSymbol = self.createSymbolFromToken(tok[i])
                newSymbol.s = scopeDepth
                newNode = TreeNode(value=newSymbol)
                self.vprint("{}Adding terminal to scope".format("  "*scopeDepth), 3)
                children[scopeDepth].insert(0, newNode)

        root.children = children[0]

    @staticmethod
    def createSymbolFromToken(tok):
        sym = SymbolNode()

        bools = ['TRUE', 'FALSE']
        types = ['BOOL', 'INT', 'REAL', 'STRING']
        ops = ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'POWER', 'EQ', 'LT', 'LE', 'GT', 'GE', 'NE', 'ASSIGN', 'SIN', 'COS', 'TAN', 'AND', 'OR', 'NOT']
        cfs = ['STDOUT', 'IF', 'WHILE', 'LET']

        # Constants
        if tok.t in types:
            sym.f = 'CONST'
            sym.t = tok.t
            sym.v = tok.v
        elif tok.t in bools:
            sym.f = 'CONST'
            sym.t = 'BOOL'
            sym.v = tok.v

        # Variables
        elif tok.t == 'ID':
            sym.f = 'VAR'
            sym.v = tok.v

        # Operators
        elif tok.t in ops:
            sym.f = 'OP'
            sym.v = tok.v
        
        # Control flow statements
        elif tok.t in cfs:
            sym.f = 'CF'
            sym.t = tok.t
            sym.v = tok.v

        # Type declarations
        elif tok.t == 'TYPE':
            sym.f = 'TYPE'
            sym.v = tok.v

        else:
            print "Error converting token '{}' to a symbol".format(tok)

        return sym

if __name__ == '__main__':
    syntaxtree = SyntaxTree()
    syntaxtree.main()
