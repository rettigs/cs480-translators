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
import re
import sys
import time

from tree import *

class Token(object):
    def __init__(self, t, v=None):
        self.t = t # Token type, e.g. id, keyword, op, bool, int, real, string
        self.v = v # Token value

    def __str__(self):
        return "Token(\"{}\", \"{}\")".format(self.t, self.v)

    def __repr__(self):
        return "<{} \"{}\">".format(self.t, self.v)

class Parser(object):

    def __init__(self):
        self.debug = 0
        self.verbose = 0
        self.tokens = []
        self.nexttoken = 0

    def main(self):

        # Grammar Productions
        self.prods = {}
        self.prods['E'] = [['T'], ['T', 'PLUS', 'E']]
        self.prods['T'] = [['INT'], ['INT', 'TIMES', 'T'], ['OPEN', 'E', 'CLOSE']]

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
                global debug
                debug += 1
            elif o == "-v":
                global verbose
                verbose += 1
            elif o == "-i":
                self.infilename = a
            elif o == "-o":
                self.outfilename = a
            else:
                usage()

        # Open input file
        if self.infilename is not None:
            self.infile = open(self.infilename, 'r')

        # Get tokens
        self.tokens = eval(self.infile.read())
        self.tokens.append(Token('NONE'))

        # Create parse tree
        self.tree = Tree()
        self.A('E', self.tree.root, 0)
        self.tree.printTree(maxdepth=3)

        # Clean up input file
        self.infile.close()

        # Open output file
        if self.outfilename is not None:
            self.outfile = open(self.outfilename+".tmp", 'w')

        # Write output
        #self.outfile.write("[" + ", ".join([str(token) for token in self.tokens]) + "]\n")
        self.outfile.write("[" + ", ".join([str(token) for token in self.tokens]) + "]\n")

        # Clean up output file
        self.outfile.close()
        if self.outfilename is not None:
            os.rename(self.outfilename+".tmp", self.outfilename)

    def usage():
        print 'Usage: {0} [-h] [-i infile] [-o outfile] [-a alg(s)] [-p] [-l] [-v]... [-d]...'.format(sys.argv[0])
        print '\t-h\tview this help'
        print '\t-i\tspecify an input file of IBTL code, defaults to stdin'
        print '\t-o\tspecify an output file of tokens, defaults to stdout'
        print '\t-v\tenable more verbose messages; use -vv for more even more messages'
        print '\t-d\tenable debug messages; use -dd for more even more messages'
        sys.exit(2)

    def term(self, kind, node):
        result = self.tokens[self.nexttoken].t == kind
        #if result:
        #    node.children.append(TreeNode(self.tokens[self.nexttoken], node))
        self.nexttoken += 1
        return result

    def Anum(self, string, node, depth):
        '''"string" is a list of terminals/nonterminals that come as the result of a single derivation step'''
        newnodes = []
        for i in xrange(len(string)):
            if string[i] in self.prods: # If it's a nonterminal
                result = self.A(string[i], node.children[i], depth)
            else: # If it's a terminal
                result = self.term(string[i], node.children[i])
            if result is False:
                return False

        #for newnode in newnodes:
        #    node.children.append(TreeNode(newnode, node))

        return True

    def A(self, word, node, depth):
        depth += 1
        indent = "  " * depth
        node.value = word
        save = self.nexttoken
        productions = self.prods[word]
        print indent + "At node '{}', see productions '{}'.".format(word, productions)
        for production in productions:
            self.nexttoken = save
            for newword in production:
                node.children.append(TreeNode(newword, node))
            print indent + "At node '{}', appending children '{}'.".format(word, [c.value for c in node.children])
            if self.Anum(production, node, depth):
                result = True
                print indent + "At node '{}', was success.".format(word)
                break
            else:
                node.children = []
                print indent + "At node '{}', was failure; new children: {}.".format(word, [c.value for c in node.children])
        else:
            result = False
        if result:
            pass
            #node.children = [TreeNode('E', self.treepointer)]

        return result

if __name__ == '__main__':
    parser = Parser()
    parser.main()
