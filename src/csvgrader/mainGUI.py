# Main.py

import traceback

from gui.mainWindow import MainWindow

filepath = "/home/auttieb/Documents/college/TA/211LSP25/120251-PHYS-211-labs-1.csv"
submitpath = "/home/auttieb/Documents/college/TA/211LSP25/submissions/lab1/L3E"



if __name__ == "__main__":
    mw = MainWindow()

    try:
        mw.run()
    except Exception as e:
        print("Critical Error")
        print(traceback.print_exception(e))