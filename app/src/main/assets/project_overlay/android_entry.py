import os
import runpy
from pathlib import Path
os.environ["MAAFGO_PLATFORM"] = "android"
runpy.run_path(str(Path(__file__).with_name("main.py")), run_name="__main__")
