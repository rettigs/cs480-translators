class TreeNode(object):
    def __init__(self, value=None, parent=None, children=list([])):
        self.value = value
        self.parent = parent
        self.children = children

    def printNode(self, level):
        indent = "    " * level
        level += 1
        print "{}{}".format(indent, self.value)
        for child in self.children:
            child.printNode(level)

class Tree(object):
    def __init__(self):
        self.root = TreeNode(value='S')

    def printTree(self):
        self.root.printNode(0)
