rcParams = {}

def subplots(*args, **kwargs):
    class Axis:
        def set_major_locator(self, *a, **k):
            pass
        def set_major_formatter(self, *a, **k):
            pass
        def tick_top(self, *a, **k):
            pass
        def set_label_position(self, *a, **k):
            pass
    class Axes:
        def __init__(self):
            self.xaxis = Axis()
        def barh(self, *a, **k):
            pass
        def grid(self, *a, **k):
            pass
    class Fig:
        pass
    return Fig(), Axes()

def xticks(*args, **kwargs):
    pass

def title(*args, **kwargs):
    pass

def tight_layout(*args, **kwargs):
    pass
