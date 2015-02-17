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
        self.offset = 0

    def main(self):

        # Grammar Productions
        self.prods = {}
        self.prods['S'] = [['OPEN', 'CLOSE'], ['OPEN', 'S', 'CLOSE'], ['S', 'S'], ['EXPR']]
        self.prods['EXPR'] = [['OPER'], ['STMTS']]
        self.prods['OPER'] = [['OPEN', 'ASSIGN', 'NAME', 'OPER', 'CLOSE'], ['OPEN', 'BINOPS', 'OPER', 'OPER', 'CLOSE'], ['OPEN', 'UNOPS', 'OPER'], ['CONSTANTS'], ['NAME']]
        self.prods['BINOPS'] = [['PLUS'], ['MINUS'], ['TIMES'], ['DIVIDE'], ['MOD'], ['POWER'], ['EQ'], ['GT'], ['GE'], ['LT'], ['LE'], ['NE'], ['OR'], ['AND']]
        self.prods['UNOPS'] = [['NEGATE'], ['NOT'], ['SIN'], ['COS'], ['TAN']]
        self.prods['CONSTANTS'] = [['STRINGS'], ['INTS'], ['REALS']]
        self.prods['STRINGS'] = [['STRING'], ['TRUE'], ['FALSE']]
        self.prods['INTS'] = [['INT']]
        self.prods['REALS'] = [['REAL']]
        self.prods['NAME'] = [['ID']]
        self.prods['STMTS'] = [['IFSTMTS'], ['WHILESTMTS'], ['LETSTMTS'], ['PRINTSTMTS']]
        self.prods['PRINTSTMTS'] = [['OPEN', 'STDOUT', 'OPER', 'CLOSE']]
        self.prods['IFSTMTS'] = [['OPEN', 'IF', 'EXPR', 'EXPR', 'EXPR', 'CLOSE'], ['OPEN', 'IF', 'EXPR', 'EXPR', 'CLOSE']]
        self.prods['WHILESTMTS'] = [['OPEN', 'WHILE', 'EXPR', 'EXPRLIST', 'CLOSE']]
        self.prods['EXPRLIST'] = [['EXPR'], ['EXPR', 'EXPRLIST']]
        self.prods['LETSTMTS'] = [['OPEN', 'LET', 'OPEN', 'VARLIST', 'CLOSE', 'CLOSE']]
        self.prods['VARLIST'] = [['OPEN', 'NAME', 'TYPE', 'CLOSE'], ['OPEN', 'NAME', 'TYPE', 'CLOSE', 'VARLIST']]
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
        self.tree.root.value = 'E'
        #print self.A('E', self.tree.root, 0)
        print self.parse('E', 0)
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

    def parse(self, curword, depth, offset=0):
        depth += 1
        indent = "  " * depth
        save = self.nexttoken
        print indent + "Parser: current word: '{}'".format(curword)
        for prod in self.prods[curword][offset:]:
            self.nexttoken = save
            print indent + "Parser: trying production '{}'".format(prod)
            matched = self.matcher(prod, depth)
            if matched:
                if depth == 1 and self.nexttoken + 2 >= len(self.tokens):
                    return False
                else:
                    return True
        return False

    def matcher(self, prod, depth):
        depth += 1
        indent = "  " * depth
        for word in prod:
            if self.nexttoken >= len(self.tokens):
                return False
            for i in xrange(5):
                if word in self.prods: # If it's a nonterminal
                    print indent + "Matcher: trying to match nonterminal '{}'".format(word)
                    result = self.parse(word, depth, offset=i)
                else:
                    print indent + "Matcher: trying to match terminal '{}' with next token '{}'".format(word, repr(self.tokens[self.nexttoken]))
                    result = self.tokens[self.nexttoken].t == word
                    self.nexttoken += 1
                if result:
                    print indent + "Matcher: success matching nonterminal '{}'".format(word)
                    break
                else:
                    print indent + "Matcher: failure matching nonterminal '{}'".format(word)
            else:
                return False

        return True

    def term(self, kind, node):
        result = self.tokens[self.nexttoken].t == kind
        self.nexttoken += 1
        #print "TERM: next token is '{}'; does it match kind '{}'? {}".format(repr(self.tokens[tokenpointer]), kind, result)
        return result

    def Anum(self, node, depth):
        indent = "    " * depth
        for child in node.children: # Check to make sure each terminal/nonterminal can be matched
            print indent + "Trying to match a '{}'...".format(child.value)
            if child.value in self.prods: # If it's a nonterminal
                result = self.A(child.value, child, depth)
            else: # If it's a terminal
                print "{}".format(repr(self.tokens[self.nexttoken]))
                result = self.term(child.value, child)
            if result:
                print indent + "Matched a '{}'.".format(child.value)
            else:
                print indent + "Failed to match a '{}'.".format(child.value)
                return False

        return True

    def A(self, word, node, depth):
        depth += 1
        indent = "    " * depth
        node.value = word
        save = self.nexttoken
        for prod in self.prods[word]:
            print indent + "At node '{}', trying production '{}'.".format(word, prod)
            node.children = [TreeNode(prodword, node) for prodword in prod] # Create a child for each word in the production
            self.nexttoken = save
            match = self.Anum(node, depth) # Whether all words matched
            if match:
                result = True
                break
        else:
            result = False

        return result

if __name__ == '__main__':
    parser = Parser()
    parser.main()
