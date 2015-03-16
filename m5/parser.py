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

from token import *
from tree import *

class Parser(object):

    def __init__(self):
        self.debug = 0
        self.verbose = 0
        self.tokens = []
        self.nexttoken = 0

    def main(self):

        # Grammar Productions
        self.prods = {}
        self.prods['S'] = [['OPEN', 'SPP'], ['EXPR', 'SP']]
        self.prods['SP'] = [['S', 'SP'], []]
        #self.prods['SPP'] = [['CLOSE', 'SP'], ['S', 'CLOSE', 'SP'], []]
        self.prods['SPP'] = [['CLOSE', 'SP'], ['S', 'CLOSE', 'SP']]
        self.prods['EXPR'] = [['OPER'], ['STMTS']]
        self.prods['OPER'] = [['OPEN', 'OPERP'], ['CONSTANTS'], ['NAME']]
        self.prods['OPERP'] = [['ASSIGN', 'NAME', 'OPER', 'CLOSE'], ['BINOPS', 'OPER', 'OPER', 'CLOSE'], ['UNOPS', 'OPER', 'CLOSE']]
        self.prods['BINOPS'] = [['PLUS'], ['MINUS'], ['TIMES'], ['DIVIDE'], ['MOD'], ['POWER'], ['EQ'], ['GT'], ['GE'], ['LT'], ['LE'], ['NE'], ['OR'], ['AND']]
        self.prods['UNOPS'] = [['NEGATE'], ['NOT'], ['SIN'], ['COS'], ['TAN']]
        self.prods['CONSTANTS'] = [['STRINGS'], ['INTS'], ['REALS']]
        self.prods['STRINGS'] = [['STRING'], ['TRUE'], ['FALSE']]
        self.prods['INTS'] = [['INT']]
        self.prods['REALS'] = [['REAL']]
        self.prods['NAME'] = [['ID']]
        self.prods['STMTS'] = [['IFSTMTS'], ['WHILESTMTS'], ['LETSTMTS'], ['PRINTSTMTS']]
        self.prods['PRINTSTMTS'] = [['OPEN', 'STDOUT', 'OPER', 'CLOSE']]
        self.prods['IFSTMTS'] = [['OPEN', 'IF', 'EXPR', 'EXPR', 'IFSTMTSP']]
        self.prods['IFSTMTSP'] = [['EXPR', 'CLOSE'], ['CLOSE']]
        self.prods['WHILESTMTS'] = [['OPEN', 'WHILE', 'EXPR', 'EXPRLIST', 'CLOSE']]
        self.prods['EXPRLIST'] = [['EXPR', 'EXPRLISTP']]
        self.prods['EXPRLISTP'] = [['EXPRLIST'], []]
        self.prods['LETSTMTS'] = [['OPEN', 'LET', 'OPEN', 'VARLIST', 'CLOSE', 'CLOSE']]
        self.prods['VARLIST'] = [['OPEN', 'NAME', 'VARTYPE', 'CLOSE', 'VARLISTP']]
        self.prods['VARLISTP'] = [['VARLIST'], []]
        self.prods['VARTYPE'] = [['TYPE']]

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
        self.tokens = eval(self.infile.read())
        self.tokens.append(Token('NONE'))
        self.vprint(self.tokens)

        # Create parse tree
        self.tree = Tree()
        result = self.parse('S', self.tree.root, 0)
        parseTree = self.tree.printTreeParse()
        if self.verbose >= 1:
            print "Valid syntax: {}".format(result)
        if self.verbose >= 2:
            self.tree.printTree()

        # Clean up input file
        self.infile.close()
        
        if not result:
            print "Parse Error"
            exit(1)

        # Open output file
        if self.outfilename is not None:
            self.outfile = open(self.outfilename+".tmp", 'w')

        # Write output
        #self.outfile.write("[" + ", ".join([str(token) for token in self.tokens]) + "]\n")
        self.outfile.write(parseTree)

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

    def parse(self, word, node, depth):
        depth += 1
        indent = "  " * depth
        node.value = word
        self.vprint(indent + "Parser: Current word: '{}'".format(word), 3)
        save = self.nexttoken
        for prod in self.prods[word]:
            self.vprint(indent + "Parser: Trying production '{}'".format(prod), 3)
            node.children = [TreeNode(prodword, node) for prodword in prod]
            self.nexttoken = save
            if self.matcher(node, depth):
                self.dprint("depth: {}".format(depth))
                self.dprint("nexttoken: {}".format(self.nexttoken))
                self.dprint("len(tokens): {}".format(len(self.tokens)))
                if depth == 1 and self.nexttoken + 1 < len(self.tokens):
                    return False # Special case: don't accept if it's the last production and we haven't read all the tokens yet
                else:
                    return True
        return False # Return false if none of the productions worked

    def matcher(self, node, depth):
        depth += 1
        indent = "  " * depth
        newChildren = []
        for child in node.children:
            word = child.value
            if word in self.prods: # If it's a nonterminal
                self.vprint(indent + "Matcher: Trying to match nonterminal '{}'".format(word), 3)
                result = self.parse(word, child, depth)
            else: # If it's a terminal
                self.vprint(indent + "Matcher: Trying to match nonterminal '{}' to next token '{}'".format(word, repr(self.tokens[self.nexttoken])), 3)
                result = self.tokens[self.nexttoken].t == word
                if result:
                    self.vprint(indent + "Matcher: Success matching '{}'".format(word), 3)
                    child.children = [TreeNode(self.tokens[self.nexttoken], child)]
                    self.nexttoken += 1
                else:
                    self.vprint(indent + "Matcher: Failure matching '{}'".format(word), 3)
            if result is False:
                break # Move on to the next production if this one didn't match
        else:
            return True # Return true if all words in the production matched

if __name__ == '__main__':
    parser = Parser()
    parser.main()
