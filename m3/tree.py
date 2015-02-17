class Token(object):
    def __init__(self, t, v=None):
        self.t = t # Token type, e.g. id, keyword, op, bool, int, real, string
        self.v = v # Token value

    def __str__(self):
        #return "Token(\"{}\", \"{}\")".format(self.t, self.v)
        return str(self.v)

    def __repr__(self):
        return "<{} \"{}\">".format(self.t, self.v)

class Node(object):
    def __init__(self, value=None, parent=None, children=list([])):
        self.value = value
        self.parent = parent
        self.children = children

    def printNode(self, level):
        indent = "    " * level
        print indent + str(self.value)
        for child in self.children:
            child.printNode(level+1)

class Tree(object):
    def __init__(self):
        self.root = Node(value='S')

    def printTree(self):
        self.root.printNode(0)


tree = Tree()
pointer = tree.root

pointer.children = [Node(Token('OPEN', '(')), Node('S'), Node(Token('CLOSE', ')'))]
pointer = pointer.children[1]

pointer.children = [Node('expr')]
pointer = pointer.children[0]

pointer.children = [Node('oper')]
pointer = pointer.children[0]

pointer.children = [Node(Token('OPEN', '(')), Node('binops'), Node('oper'), Node('oper'), Node(Token('OPEN', '('))]

pointer.children[1].children = [Node(Token('PLUS', '+'))]

pointer.children[2].children = [Node('constants')]
pointer.children[2].children[0].children = [Node(Token('INT', "1"))]

pointer.children[3].children = [Node('constants')]
pointer.children[3].children[0].children = [Node(Token('INT', "2"))]

tree.printTree()
