class TreeNode(object):
    def __init__(self, value=None, parent=None, children=list([])):
        self.value = value
        self.parent = parent
        if self.parent is not None:
            self.root = self.parent.root
        self.children = children

    def printNode(self, level):
        indent = "    " * level
        level += 1
        print "{}{}".format(indent, self.value)
        for child in self.children:
            child.printNode(level)

    def printNodeParse(self):
        if not isinstance(self.value, str): # If it's a token (i.e. terminal)
            if self.value.t == "CLOSE":
                self.root.curlevel -= 1
            indent = "    " * self.root.curlevel
            self.root.parsetree += "{}{}\n".format(indent, self.value)
            if self.value.t == "OPEN":
                self.root.curlevel += 1
        for child in self.children:
            child.printNodeParse()

class Tree(object):
    def __init__(self):
        self.root = TreeNode(value='S')
        self.root.root = self.root

    def printTree(self):
        self.root.printNode(0)

    def printTreeParse(self):
        self.root.curlevel = 0
        self.root.parsetree = ""
        self.root.printNodeParse()
        return self.root.parsetree
