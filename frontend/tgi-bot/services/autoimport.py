import importlib
import os


def autoimport(init_file):
    directory = os.path.dirname(os.path.abspath(init_file))
    module_name = os.path.basename(directory)

    files = os.listdir(directory)
    step_files = [f for f in files if f.startswith("step_") and f.endswith(".py")]

    for step_file in step_files:
        importlib.import_module(f"commands.{module_name}.{step_file[:-3]}")
