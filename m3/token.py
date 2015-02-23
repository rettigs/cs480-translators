class Token(object):
    def __init__(self, t, v=None):
        self.t = t # Token type, e.g. id, keyword, op, bool, int, real, string
        self.v = v # Token value

    def __str__(self):
        if isinstance(self.v, str):
            return "Token(\"{}\", \"{}\")".format(self.t, self.v.replace('"','\\"'))
        else:
            return "Token(\"{}\", \"{}\")".format(self.t, self.v)

    def __repr__(self):
        if isinstance(self.v, str):
            return "<{} \"{}\">".format(self.t, self.v.replace('"','\\"'))
        else:
            return "<{} \"{}\">".format(self.t, self.v)
