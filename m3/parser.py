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
        self.prods['S'] = [['EXPR', 'SP'], ['OPEN', 'SPP']]
        self.prods['SP'] = [['S', 'SP'], []]
        #self.prods['SPP'] = [['CLOSE', 'SP'], ['S', 'CLOSE', 'SP'], []]
        self.prods['SPP'] = [['CLOSE', 'SP'], ['S', 'CLOSE', 'SP']]
        self.prods['EXPR'] = [['OPER'], ['STMTS']]
        self.prods['OPER'] = [['OPEN', 'OPERP'], ['CONSTANTS'], ['NAME']]
        self.prods['OPERP'] = [['ASSIGN', 'NAME', 'OPER', 'CLOSE'], ['BINOPS', 'OPER', 'OPER', 'CLOSE'], ['UNOPS', 'OPER']]
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
        self.prods['VARLIST'] = [['OPEN', 'NAME', 'TYPE', 'CLOSE', 'VARLISTP']]
        self.prods['VARLISTP'] = [['VARLIST'], []]
        self.prods['TYPE'] = [['BOOL'], ['INT'], ['REAL'], ['STRING']]

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
        self.tree.root.value = 'S'
        #print self.A('S', self.tree.root, 0)
        print self.parse('S', 0)
        #self.tree.printTree()

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

    def parse(self, curword, depth):
        depth += 1
        indent = "  " * depth
        print indent + "Current word: '{}'".format(curword)
        save = self.nexttoken
        for prod in self.prods[curword]:
            print indent + "Trying production '{}'".format(prod)
            depth += 1
            indent = "  " * depth
            self.nexttoken = save
            for word in prod:
                if word in self.prods: # If it's a nonterminal
                    print indent + "Trying to match nonterminal '{}'".format(word)
                    result = self.parse(word, depth)
                else: # If it's a terminal
                    print indent + "Trying to match nonterminal '{}' to next token '{}'".format(word, repr(self.tokens[self.nexttoken]))
                    result = self.tokens[self.nexttoken].t == word
                    if result:
                        print indent + "Success matching '{}'".format(word)
                        self.nexttoken += 1
                    else:
                        print indent + "Failure matching '{}'".format(word)
                if result is False:
                    break # Move on to the next production if this one didn't match
            else:
                return True # Return true if all words in the production matched
            depth -= 1
            indent = "  " * depth
        return False # Return false if none of the productions worked

if __name__ == '__main__':
    parser = Parser()
    parser.main()
