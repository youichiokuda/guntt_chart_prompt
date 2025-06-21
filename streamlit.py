from contextlib import contextmanager

# Basic stubs for Streamlit functions used in the app

def pyplot(*args, **kwargs):
    pass

def error(*args, **kwargs):
    pass

def title(*args, **kwargs):
    pass

def text_area(*args, **kwargs):
    return ""

def button(*args, **kwargs):
    return False

def warning(*args, **kwargs):
    pass

@contextmanager
def spinner(*args, **kwargs):
    yield

def success(*args, **kwargs):
    pass

def dataframe(*args, **kwargs):
    pass

def code(*args, **kwargs):
    pass
