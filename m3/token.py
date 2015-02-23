class Token(object):
    def __init__(self, t, v=None):
        self.t = t # Token type, e.g. id, keyword, op, bool, int, real, string
        self.v = v # Token value

    def __str__(self):
        return "Token(\"{}\", \"{}\")".format(self.t, self.v.replace('"','\\"'))

    def __repr__(self):
        return "<{} \"{}\">".format(self.t, self.v.replace('"','\\"'))
