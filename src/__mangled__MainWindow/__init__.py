import os
from tkinter import *
from tkinter import ttk, filedialog

from __mangled__Grader import Grader

rubric = {"1":{"1_1":"fail", "2_1":"ish", "3_1":"pass"}, "2":{"1_3":"fail", "2_2":"ish", "3_2":"pass"}}



class MainWindow:

    def __init__(self):
        
        self.gbLoad=False
        self.assignmentsLoaded = True

        self.studentGrade = {}


        self.root = Tk()
        self.root.title("Grading Program!")
        self.root.geometry("600x600")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.frm = ttk.Frame(self.root)
        self.frm.grid(column=0,row=0,sticky="nsew")
        self.frm.grid_rowconfigure(0, weight=1)
        self.frm.grid_columnconfigure(0,weight=1)
        # Everything is laid out in a tabbed config
        self.tabs = ttk.Notebook(self.frm)
        # Makes the window work, no clue why I need this
        self.tabs.grid(column=0, row=0,sticky=(N,E,S,W))

        # Each tab is a frame
        self.grade = ttk.Frame(self.tabs)
        self.grade.grid(column=0,row=0,sticky="nsew")
        self.grade.grid_rowconfigure(0, weight=1)
        self.grade.grid_columnconfigure(0,weight=1)

        self.config = ttk.Frame(self.tabs)
        
        self.config.grid(column=0,row=0,sticky="n")
        self.config.grid_rowconfigure(0, weight=1)
        self.config.grid_columnconfigure(0,weight=1)

        self.tabs.add(self.config, text="Configure")

        self.tabs.add(self.grade, text="Grader", state="disable")

        # Generates the configuration tab to make the code a bit nicer
        self.configureTab(self.config)
        #self.gradeTab(self.grade)

        

    def run(self):
        self.root.mainloop()


    def configureTab(self, tab:ttk.Frame):
        # File Input! Yay!
        ttk.Label(text="Gradebook CSV Path")
        self.gbook_path = StringVar(value=os.getcwd())
        ttk.Entry(tab, textvariable=self.gbook_path, width=50).grid(row=0, column=0)
        ttk.Button(tab, text="Open File", command=lambda: self.getPaths(self.gbook_path)).grid(column=1, row=0)
        ttk.Button(tab, text="Load Gradebook", command=self.loadGradeBook).grid(column=0, row=1)
            
        ttk.Label(text="Assignment Dirs")
        self.submission_path = StringVar(value=os.getcwd())
        ttk.Entry(tab, textvariable=self.submission_path, width=50).grid(row=2, column=0)
        ttk.Button(tab, text="Open Directory", command=lambda: self.getPaths(self.submission_path, mode="dir")).grid(column=1, row=2)
        ttk.Button(tab, text="Load Assignments", command=self.loadSubmissions).grid(column=0, row=3)

        ttk.Label(text="Group Import")
        self.groups_path = StringVar(value=os.getcwd())
        ttk.Entry(tab, textvariable=self.submission_path, width=50).grid(row=4, column=0)
        ttk.Button(tab, text="Open Directory", command=lambda: self.getPaths(self.groups_path, mode="csv")).grid(column=1, row=4)
        ttk.Button(tab, text="Load Assignments", command=self.importGroups).grid(column=0, row=5)

        ttk.Button(tab, text="Start Grading", command=self.enableGrading).grid(column=1, row=6)

        

    def gradeTab(self, tab:ttk.Frame):
        # Going to be a grid of frames here!
        self.rubricFrame = ttk.Labelframe(tab, text="rubric")
        self.rubricFrame.grid(row=0, column=0, sticky="w")
        self.rubricFrame.grid_rowconfigure(0, weight=1)
        self.rubricFrame.grid_columnconfigure(0,weight=1)
        # Create the rubric section
        self.displayRubric(self.rubricFrame)

        self.infoFrame = ttk.Labelframe(tab, text="Student Info")
        self.infoFrame.grid(row=0, column=1, sticky="w")
        self.infoFrame.grid_rowconfigure(0, weight=1)
        self.infoFrame.grid_columnconfigure(0,weight=1)

        self.groupFrame = ttk.Labelframe(tab, text="Groups")
        self.groupFrame.grid(row=0, column=2, sticky="w")
        self.groupFrame.grid_rowconfigure(0, weight=1)
        self.groupFrame.grid_columnconfigure(0,weight=1)


        ttk.Label(self.infoFrame, text="test").grid(column=0, row=0, sticky="w")
        ttk.Label(self.groupFrame, text="this").grid(column=0, row=0)


        
    def displayRubric(self, contain):
        # Create UI elements
        # Thanks chatGPT!
        for col, (outer_key, inner_dict) in enumerate(self.rubric.items()):
            ttk.Label(contain, text=f"{outer_key}:").grid(row=0, column=col, sticky="w")
            # Variable to store selected option for this category
            self.studentGrade[outer_key] = StringVar(value="")
            for row, (inner_key, value) in enumerate(inner_dict.items(), start=1):
                rb = ttk.Radiobutton(contain, text=value, variable=self.studentGrade[outer_key], value=inner_key)
                rb.grid(row=row, column=col, sticky="w")
                        




    
    def getPaths(self, stvar:StringVar, mode:str="csv"):
        allowedFiles=(("Comma Seperated Value", "*.csv"), ("all files", "*.*"))
        if mode == "csv":
            stvar.set(filedialog.askopenfilename(filetypes=allowedFiles, initialdir=os.getcwd()))
        elif mode == "dir":
            stvar.set(filedialog.askdirectory(initialdir=os.getcwd()))

    def loadGradeBook(self):
        self.rubric = rubric
        #self.displayRubric()
        self.gbLoad = True

    def loadSubmissions(self):
        pass

    def importGroups(self):
        pass

    def enableGrading(self):
        if self.gbLoad and self.assignmentsLoaded:
            self.gradeTab(self.grade)
            self.tabs.tab(1,state="normal")
            print("setState")

