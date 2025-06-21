class FontManager:
    def addfont(self, *args, **kwargs):
        pass

fontManager = FontManager()

class FontProperties:
    def __init__(self, fname=None):
        self.fname = fname
    def get_name(self):
        return self.fname or ""
