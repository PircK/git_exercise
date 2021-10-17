from cx_Freeze import setup, Executable
import os

includes = []
include_files = [r"C:\Users\Tinka\AppData\Local\Programs\Python\Python36\DLLs\tcl86t.dll",
r"C:\Users\Tinka\AppData\Local\Programs\Python\Python36\DLLs\tk86t.dll",
r"C:\Users\Tinka\Documents\Documents\Sola\FMF\2.letnik\Programiranje_2\six\matica.ico"
]

os.environ['TCL_LIBRARY'] = r'C:\Users\Tinka\AppData\Local\Programs\Python\Python36\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\Tinka\AppData\Local\Programs\Python\Python36\tcl\tk8.6'

base = None

setup(
    name = "Six",
    version = "0.1",
    options = {"build_exe": {"includes": includes, "include_files": include_files}},
    executables = [Executable("sliks.py", base=base)]
    )