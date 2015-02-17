class TreeNode(object):
    def __init__(self, value=None, parent=None, children=list([])):
        self.value = value
        self.parent = parent
        self.children = children

    def printNode(self, level, depthleft=None):
        if depthleft is not None:
            depthleft -= 1
            if depthleft < 0:
                return
        indent = "    " * level
        print indent + str(self.value)
        for child in self.children:
            child.printNode(level+1, depthleft=depthleft)

class Tree(object):
    def __init__(self):
        self.root = TreeNode(value='S')

    def printTree(self, maxdepth=None):
        self.root.printNode(0, depthleft=maxdepth)
