class SymbolNode(object):
    def __init__(self, f=None, t=None, v=None, s=None):
        self.f = f # Form, e.g. var, const, op, cf (control flow), type (for let statements)
        self.t = t # Variable/return type, e.g. bool, int, real, string (does not apply to cf nodes)
        self.v = v # Value, e.g. variable name, constant, operator name, cf name
        self.s = s # Scope depth, e.g. "5" (only needed for variables)

    def __str__(self):
        if isinstance(self.v, str):
            return "Sym({}, {}, \"{}\", {})".format(self.f, self.t, self.v.replace('"','\\"').replace('\n', '\\n'), self.s)
        else:
            return "Sym({}, {}, \"{}\", {})".format(self.f, self.t, self.v, self.s)
