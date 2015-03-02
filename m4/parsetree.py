#!/usr/bin/python

"""
Converts the output of parser.py to a generalized parse tree.
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

class ParseTree(object):

    def __init__(self):
        self.debug = 0
        self.verbose = 0
        self.tokens = []
        self.curTokenNumber = 0

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
            
        self.vprint(self.tokens, 2)

        # Create parse tree
        tree = Tree()
        children = []
        while self.curTokenNumber + 4 < len(self.tokens):
            newchild = TreeNode()
            self.makeParseTree(newchild, 0)
            children.append(newchild)
            self.curTokenNumber += 1

        tree.root.value = ""
        tree.root.children = children

        if self.verbose >= 1:
            print ""
            tree.printTree()

        # Clean up input file
        self.infile.close()

        # Open output file
        if self.outfilename is not None:
            self.outfile = open(self.outfilename+".tmp", 'w')

        # Write output
        pickle.dump(tree, self.outfile)

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

    def makeParseTree(self, curNode, depth):
        depth += 1
        indent = "  " * depth
        curToken = self.tokens[self.curTokenNumber]
        if curToken.t == "OPEN":
            openLevel = curToken.level
            self.curTokenNumber += 1
            curToken = self.tokens[self.curTokenNumber]
            curNode.value = curToken
            curNode.children = []
            while not (curToken.level == openLevel and curToken.t == "CLOSE"):
                self.curTokenNumber += 1
                curToken = self.tokens[self.curTokenNumber]
                self.vprint("{}CurNode: {}    Creating child node under token '{}'".format(indent, curNode.value.v, curToken.t), 3)
                child = self.makeParseTree(TreeNode(), depth)
                if child.value.t != "CLOSE":
                    curNode.children.append(child)
            self.vprint("{}CurNode: {}    Children: {}".format(indent, curNode.value.v, [c.value for c in curNode.children]), 3)
        else:
            curToken = self.tokens[self.curTokenNumber]
            curNode.value = curToken
            self.vprint("{}CurNode: {}    Found terminal '{}'; creating node with no children".format(indent, curNode.value.v, curToken.t), 3)
        return curNode

if __name__ == '__main__':
    parsetree = ParseTree()
    parsetree.main()
