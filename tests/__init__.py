import sys
import importlib
from pathlib import Path

STUB_DIR = Path(__file__).resolve().parent.parent / 'stubs'
sys.path.insert(0, str(STUB_DIR))

for mod in ['openai', 'pandas', 'streamlit']:
    sys.modules[mod] = importlib.import_module(mod)

# Matplotlib stubs have submodules
sys.modules['matplotlib'] = importlib.import_module('matplotlib')
for sub in ['pyplot', 'dates', 'font_manager']:
    sys.modules[f'matplotlib.{sub}'] = importlib.import_module(f'matplotlib.{sub}')
