from tkinter import *
from tkinter import ttk, filedialog, simpledialog, messagebox
import os
import webbrowser
from ..dataforms.teams import Groups
from ..Grader.grader import Grader

import pandas as pd



# Variables Im using for testing
rubric = {"1":{"1_1":"fail", "2_1":"ish", "3_1":"pass"}, "2":{"1_3":"fail", "2_2":"ish", "3_2":"pass"}}

grp = {1:["jim", "bob"], 2:"carl,sam,jill".split(",")}


t_filepath = "/home/auttieb/Documents/college/TA/211LSP25/120251-PHYS-211-labs-1.csv"
t_submitpath = "/home/auttieb/Documents/college/TA/211LSP25/submissions/lab1/L3E"

DEFAULTPATH = os.path.expanduser("~")


class MainWindow:




    ###################################################################
    #######   UI Definitions and Generators (including init)    #######
    ###################################################################

    def __init__(self):

        # State variables used (non Tk)
        self.gbLoad=False
        self.assignmentsLoaded = True # This is True for testing  lm
        self.newGroups = False # Are existing groups being used or new ones created
        self.groupsLoaded = False
        self.groupGrade = True
        self.initsel = False


        # Vairables used in grading loops including groups and grader objects
        self.studentGrade = {}
        self.groups = Groups()
        self.grader = Grader()
        self.currentStudent = (None, None, None, None, None, None, None) # Stores tuple given by Grader.getCurrentStudent()

        # FOR TESTING ONLY
        #for gid, nid in grp.items():
        #    self.groups.addGroup(groupID=gid, students=nid)
    


        self.root = Tk()
        self.root.title("Grading Program!")
        self.root.geometry("900x600")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.frm = ttk.Frame(self.root)
        self.frm.grid(column=0,row=0,sticky=(N,E,S,W))       
        self.frm.grid_rowconfigure(0, weight=1)
        self.frm.grid_columnconfigure(0,weight=1)
        
        # Tk state variables

        self._newgroups_state = StringVar(value="open") # If new groups are being created 
        self._selectedGroup = [None,""] # (gid, netid)

        
        # Everything is laid out in a tabbed config
        self.tabs = ttk.Notebook(self.frm)

        self.tabs.grid(column=0, row=0, sticky=(N,E,S,W), padx=10, pady=10)

        # Each tab is a frame
        self.grade = ttk.Frame(self.tabs)
        self.grade.grid(column=0,row=0,sticky=(N,E,S,W))
        self.grade.grid_rowconfigure(0, weight=1)
        #self.grade.grid_columnconfigure(0,weight=1)


        self.config = ttk.Frame(self.tabs)
        
        self.config.grid(column=0,row=0,sticky=(N,E,S,W))
        self.config.grid_rowconfigure(0, weight=1)
        self.config.grid_columnconfigure(0, weight=1)

        
        self.tabs.add(self.config, text="Configure")

        self.tabs.add(self.grade, text="Grader", state="disable")

        # Generates the configuration tab to make the code a bit nicer
        self.configureTab(self.config)
        #self.gradeTab(self.grade)

        



    def configureTab(self, tab:ttk.Frame):
        # File Input! Yay!


        gbFrame = ttk.Frame(tab)
        gbFrame.grid(row=0, column=0,sticky="NEW")
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0,weight=1)

        ttk.Label(gbFrame, text="Gradebook CSV Path").grid(row=1, column=2, sticky="NWE")

##################################################################
        self.gbook_path = StringVar(value=t_filepath)
##################################################################
        ttk.Entry(gbFrame, textvariable=self.gbook_path, width=50).grid(row=2, column=1, columnspan = 4, sticky="NWE")
        ttk.Button(gbFrame, text="Select File", command=lambda: self.getPaths(self.gbook_path)).grid(row=2, column=6, sticky=(N,W))
        # ttk.Button(gbFrame, text="Load Gradebook", command=self.loadGradeBook).grid(row=3, column=2, columnspan=2, sticky="N")

        aFrame = ttk.Frame(tab)
        aFrame.grid(row=1, column=0, sticky=(N,W))
        tab.grid_rowconfigure(1, weight=1)


        ttk.Label(aFrame, text="Assignment Directory").grid(row=1, column=2, sticky="NWE")
############################################################################################
        self.submission_path = StringVar(value=t_submitpath)
############################################################################################
        ttk.Entry(aFrame, textvariable=self.submission_path, width=50).grid(row=2, column=1, columnspan = 4, sticky="NWE")
        ttk.Button(aFrame, text="Select Directory", command=lambda: self.getPaths(self.submission_path, mode="dir")).grid(row=2, column=6, sticky=(N,W))
        # ttk.Button(aFrame, text="Load Submissions", command=self.loadSubmissions).grid(row=3, column=2, columnspan=2, sticky="N")

        grFrame = ttk.Frame(tab)
        grFrame.grid(row=2, column=0, sticky="NEW")
        tab.grid_rowconfigure(2, weight=1)

        ttk.Label(grFrame, text="Group Import").grid(row=1, column=2, sticky="NWE")
        self.groups_path = StringVar(value=os.getcwd())

        # If we are creating new groups this will change the behavior of the 


        ttk.Entry(grFrame, textvariable=self.groups_path, width=50).grid(row=2, column=1, columnspan = 4, sticky="NWE")
        ttk.Button(grFrame, text="Select CSV File", command=lambda: self.getPaths(self.groups_path, mode="csv")).grid(row=2, column=6, sticky=(N,W))
        # ttk.Button(grFrame, text="Load Groups", command=self.genGroups).grid(row=3, column=2, sticky="NEW")
        self.groupButton = ttk.Checkbutton(grFrame)
        self.groupButton.grid(row=3, column=4, sticky="NW")
        ttk.Label(grFrame, text="Generate New Groups").grid(row=3, column=2, columnspan=2, sticky=E)


        ttk.Button(tab, text="Start Grading", command=self.enableGrading).grid(row=3, column=0, sticky="NW")
        tab.grid_rowconfigure(3, weight=1)

        self.groupGradeBtn = ttk.Checkbutton(tab, text="Grade by Group ")
        self.groupGradeBtn.grid(row=3, column=2, sticky="nw")

        

    def gradeTab(self, tab):

        # Going to be a grid of frames here!
        # First the rubric Section !

        tab.grid_columnconfigure(0, weight=6)
        tab.grid_columnconfigure(1, weight=4)
        tab.grid_columnconfigure(2, weight=4)
        tab.grid_columnconfigure(3, weight=1) 

        rFrame = ttk.Labelframe(tab, text="Rubric")
        #tab.add(rFrame)

        rFrame.grid(row=0, column=0, sticky="NSWE")
        rFrame.grid_columnconfigure(0, weight=1)
        rFrame.grid_columnconfigure(1, weight=2)
        
        self.displayRubric(rFrame)

        # Then display student info
        iFrame = ttk.Labelframe(tab, text="Student Info")
        #tab.add(iFrame)

        iFrame.grid(row=0, column=1, sticky="NSWE")
        #tab.grid_columnconfigure(1,weight=1)
        iFrame.grid_columnconfigure(0, weight=1)
        iFrame.grid_columnconfigure(1, weight=1, minsize=100)     

        self.studentName = StringVar(value="N/A")
        ttk.Label(iFrame, text="Name:").grid(row=0, column=0, sticky='ne')
        ttk.Label(iFrame, textvariable=self.studentName).grid(row=0, column=1, sticky='nw')
        
        self.netID = StringVar(value="N/A")
        ttk.Label(iFrame, text="NetID:").grid(row=1, column=0, sticky='ne')
        ttk.Label(iFrame, textvariable=self.netID).grid(row=1, column=1, sticky='nw')
       
        self.studentSection = StringVar(value="N/A")
        ttk.Label(iFrame, text="Section:").grid(row=2, column=0, sticky="NE")
        ttk.Label(iFrame, textvariable=self.studentSection).grid(row=2, column=1, sticky="NW")

        self.studentGroup = StringVar(value="")
        ttk.Label(iFrame, text="Group:").grid(row=3, column=0, sticky="NE")
        ttk.Label(iFrame, textvariable=self.studentGroup).grid(row=3, column=1, sticky="NW")
        
        self.groupMembers = StringVar(value="")
        ttk.Label(iFrame, text="Group Members:").grid(row=4, column=0, sticky="NE")
        ttk.Label(iFrame, textvariable=self.groupMembers).grid(row=5, column=0, columnspan=2, sticky="NWE")

        ttk.Label(iFrame, text="Submission Selection").grid(row=6, column=0, sticky="ne")
        self.currentSelectSubmit = StringVar()
        self.selectSubmission = ttk.Combobox(iFrame, state="readonly", textvariable=self.currentSelectSubmit)
        self.selectSubmission.grid(row=6, column=0, columnspan=2)
        self.selectSubmission.bind("<<ComboboxSelected>>", self.openSelectedSubmission)

        
        # Group information!

        gFrame = ttk.Labelframe(tab, text="Groups")
        #tab.add(gFrame)
        gFrame.grid(row=0, column=2, sticky="NSWE")
        #tab.grid_columnconfigure(2,weight=1)
        gFrame.grid_columnconfigure(0,weight=1)
        gFrame.grid_columnconfigure(1,weight=1)
        gFrame.grid_rowconfigure(0,weight=1)

        # Instantiate the treeview
        self.groupTree = ttk.Treeview(gFrame)
        self.groupTree.grid(row=0, column=0, columnspan=2, sticky="NSWE")
        # Add a scroll bar!
        self.vscroll = ttk.Scrollbar(gFrame, orient="vertical", command=self.groupTree.yview)
        self.groupTree.configure(yscrollcommand=self.vscroll.set)
        self.vscroll.grid(row=0, column=2, sticky="ns")

        # Add a binding for selected group
        self.groupTree.bind("<ButtonRelease-1>", self.selectGroup)

        self.genGroupTree(self.groupTree)

        #self.displayStudentInfo()

        
        self.addCurSelB = ttk.Button(gFrame, text="Assign Current", command=self.assignToGroup, state='disabled')
        self.addCurSelB.grid(row=1, column=0, sticky="WEN")

        self.addNetCurB = ttk.Button(gFrame, text="Add NetID", command=self.addByNet, state='disabled')
        self.addNetCurB.grid(row=1, column=1, sticky="WEN")

        ttk.Button(gFrame, text="New Group", command=self.addNewGroup).grid(row=2, column=0, sticky="WEN")
        ttk.Button(gFrame, text="Save Groups", command=self.saveGroups).grid(row=2, column=1, sticky="WEN")
        self.delCurSel = ttk.Button(gFrame, text="Delete", command=self.deleteGroup, state="disabled")
        self.delCurSel.grid(row=3, column=1, sticky="WN")


        #tab.grid_rowconfigure(0, weight=1)
        #tab.grid_columnconfigure(3, weight=1)

        # # Display the class roster!
        # rosterFrm = ttk.Labelframe(tab, text="Roster")
        # #tab.add(rosterFrm)
        # rosterFrm.grid(row=0, column=3, sticky="NSWE")      
 

        # rosterFrm.grid_rowconfigure(0, weight=1)
        # rosterFrm.grid_columnconfigure(0, weight=1)
        # #rosterFrm.grid_columnconfigure(1,weight=1)


        # self.rosterTree = ttk.Treeview(rosterFrm, columns=("First", "Last", "NetID"), show="headings")
        # self.rosterTree.grid(row=0, column=0, sticky="NSWE")

        # self.vscroll1 = ttk.Scrollbar(rosterFrm, orient="vertical", command=self.rosterTree.yview)
        # self.rosterTree.configure(yscrollcommand=self.vscroll1.set)
        # self.vscroll1.grid(row=0, column=1, sticky="NS")

        # #self.displayRoster()

        ttk.Button(tab,text="prev", command=self.gradePrev).grid(row = 1, column=0, sticky=W)
        ttk.Button(tab, text="next", command=self.gradeNext).grid(row=1, column=2, sticky=E)

        self.currentSubmission = StringVar(value="?/?")
        ttk.Label(tab, textvariable=self.currentSubmission).grid(row=1, column = 1, sticky=N)
 
        # ttk.Label(iFrame, text="test").grid(column=0, row=0, sticky="w")
        # ttk.Label(gFrame, text="this").grid(column=0, row=0)

    def displayRoster(self):

        for row in self.grader.getRoster():
            self.rosterTree.insert("", END, values=(row[0], row[1], row[2]))
       
    def displayRubric(self, root):
        # Create UI elements
        # Thanks chatGPT!
        row = 0
        for (outer_key, inner_dict) in self.grader.rubric.items():
            
            ttk.Label(root, text=f"{outer_key}:").grid(row=row, column=0, sticky=W)
            row+=1
            # Variable to store selected option for this category {cat:[grade:comment]}
            self.studentGrade[outer_key] = [StringVar(value=""), StringVar(value="")]
            for (inner_key, value) in inner_dict.items():
                ttk.Radiobutton(root, text="", variable=self.studentGrade[outer_key][0], value=inner_key, ).grid(row=row, column=0, sticky=W)
                ttk.Label(root, text=value, wraplength=200).grid(row=row, column=1, sticky="WE", columnspan=2, pady=(0,10))
                row+= 1

            ttk.Label(root, text="Comments?").grid(row=row+1, column=0, columnspan=2, sticky="w")
            ttk.Entry(root, textvariable=self.studentGrade[outer_key][1], width=50).grid(row=row+2, column=1, columnspan=2, sticky=W)
            row += 3
            



    def genGroupTree(self, tree:ttk.Treeview):
        """Generates group tree

        Args:
            tree (ttk.Treeview): Treeview items
            groups (dict, optional): groups to display. Defaults to empty dictionary.
        """
        # Itterates over the groups 
        for gid, netids in self.groups.getGroupDict().items():
            # Inserts parent group, labeled with group number prefixed with parent
            tree.insert('', END, text=str(gid), iid=f"p_{gid}")
            # Add the students, labeled with c_<group #>_<NetID>, c_ prefix is useful later
            for nid in netids:
                tree.insert(f"p_{gid}", END, text=nid, iid=f"c_{gid}_{nid}")

    def updateStudentInfo(self):
        """Updates student information display and opens the most recent submission 
        """
        self.netID.set(self.currentStudent[0])
        self.studentName.set(f"{self.currentStudent[2]} {self.currentStudent[3]}")
        self.studentSection.set(self.currentStudent[4])
        self.currentSubmission.set(self.currentStudent[5])
        #self.studentGroup.set(self.groups.group(self.currentStudent[0]))
        #self.groupMembers.set(str(self.groups.students(self.groups.group(self.currentStudent[0]))))
        self.genSubmissionCombo()
        self.openSelectedSubmission()

    def genSubmissionCombo(self):
        """Generates the combobox used to select submissions 
        """
        # This is nasty formatting but basically just makes the timestamp easy to read and (importantly) keeps the
        #  idexing the same as for the paths
        datetimes = []
        for j in self.currentStudent[1]:
            i = str(j[0])
            datetimes.append(f"{i[0:2]}/{i[2:4]}/{i[4:8]} {i[8:10]}:{i[10:12]}:{i[12:]}") 
        self.selectSubmission["values"] = datetimes
        self.selectSubmission.current(0)
    

    





    ###########################################
    ####### Getter and setter functions #######
    ###########################################

    def assignToGroup(self, groupID:int=None, NetID:str=None):
        """Assign netID to group groupID, if group does not exist it will be created 

        Args:
            groupID (int): group ID
            netID (str): student NetID
        """
        if groupID is None:
            groupID = int(self._selectedGroup[0])

        if NetID is None:
            #print(self.currentStudent)
            NetID = str(self.currentStudent[0])
        # Ensure we have the parent group in the tree
        if self.groups.students(groupID) is None:
            self.groupTree.insert("", END, text=str(groupID), iid=f"p_{groupID}")
        # Add Student and display
        self.groups.addStudent(groupID, NetID)
        self.groupTree.insert(f"p_{groupID}", END, text=NetID, iid=f"c_{groupID}_{NetID}")

    def addNewGroup(self):
        """Add a new group with default numbering 
        """
        gid = self.groups.addGroup()
        self.groupTree.insert("", END, text=str(gid), iid=f"p_{gid}")

    def addByNet(self):
        """add NetID to selected group
        """
        netID = simpledialog.askstring(parent= self.root, title=f"Add NetID to group {self._selectedGroup}", prompt="NetID: ")
        # Check if the student is in the gradebook, if not prompt for confirmation
        if not self.grader.getStudentInfo(netID):
            if not messagebox.askyesno(parent=self.root, message="NetID not in gradebook, add anyway?"):
                return
        self.assignToGroup(groupID=self._selectedGroup[0], NetID=netID)
    
    def deleteGroup(self):
        # Check to make sure you want to delete the group (if its a group)

        if self._selectedGroup[1] is None:
            if not messagebox.askokcancel(message=f"Delete group {self._selectedGroup[0]} and all members?"):
                return
            self.groups.deleteGroup(self._selectedGroup[0])
            for itm in self.groupTree.get_children([f"p_{self._selectedGroup[0]}"]):
                self.groupTree.delete(itm)
            self.groupTree.delete(f"p_{self._selectedGroup[0]}")
        else:
            self.groups.removeStudent(str(self._selectedGroup[1]))
            self.groupTree.delete(f"c_{self._selectedGroup[0]}_{self._selectedGroup[1]}")


    
    def getPaths(self, stvar:StringVar, mode:str="csv", ):
        """Get path to open a file

        Args:
            stvar (StringVar): Variable to store it in 
            mode (str, optional): csv file or directory. Defaults to "csv".
        """
        allowedFiles=(("Comma Seperated Value", "*.csv"), ("all files", "*.*"))
        if mode == "csv":
            stvar.set(filedialog.askopenfilename(parent=self.root, filetypes=allowedFiles, initialdir=DEFAULTPATH))
        elif mode == "dir":
            stvar.set(filedialog.askdirectory(parent=self.root, initialdir=DEFAULTPATH))
    
    def getSavePath(self):
        """Path to save output to 

        Returns:
            _type_: _description_
        """
        return filedialog.asksaveasfilename(parent=self.root, initialdir=DEFAULTPATH)

    def resetRubric(self):
        """Resets the rubric THIS WILL DELETE CURRENT VALUES BE CAREFUL PLZ
        """
        for sel  in self.studentGrade.values():
            sel[0].set("")
            sel[1].set("")

    def getCurrentGrades(self):
        for cat in self.studentGrade.keys():
            self.studentGrade[cat][0].set(self.currentStudent[6][cat][0])
            self.studentGrade[cat][1].set(self.currentStudent[6][cat][1])

    def formatGrades(self):
        """Returns formatted dictionary of grades as strings

        Returns:
            dict: {category:[grade, comments]}
        """
        return {str(itm):[val[0].get(), val[1].get()] for (itm, val) in self.studentGrade.items()}


    def selectGroup(self, event):
        """Selects the group from the tree and saves in self._selectedGroup=[groupID, netID]

        Args:
            event (_type_): _description_
        """
        if not self.initsel:
            self.addCurSelB.state(["!disabled"])
            self.addNetCurB.state(["!disabled"])
            self.delCurSel.state(["!disabled"])
            self.initsel = True

        selection = str(self.groupTree.focus()).split("_")
        if selection[0] == "p":
            self._selectedGroup[0] = int(selection[1])
            self._selectedGroup[1] = None
        elif selection[0] == "c":
            self._selectedGroup[0] = int(selection[1])
            self._selectedGroup[1] = selection[2]
        else:
            self._selectedGroup = [None,None]
    

    def getSelectedPath(self):
        return self.currentStudent[1][self.selectSubmission.current()][1]

    ###############################
    ###### Driver functions #######
    ###############################

    def run(self):
        self.root.mainloop()


    def enableGrading(self):
        gradebookpth = self.gbook_path.get()
        submissiondir = self.submission_path.get()


        #we are opening the groups
        if not self.groupButton.instate(["selected"]) and self.groupGradeBtn.instate(["selected"]):
            try:
                self.groups.importGroups(self.groups_path.get())
            except RuntimeError as e:
                self.displayError(f"Error loading groups, ensure correct file selected:\n{e}")
                return
        # Setting groupGrade state
        print(self.groupGradeBtn.instate(["selected"]))
        self.groupGrade = bool(self.groupGradeBtn.instate(["selected"]))
        # Loading gradebook
        try:
            self.grader.importGradebook(gradebookpth)
        except RuntimeError as e:
            self.displayError(f"Invalid gradebook import:\n {e}")
            return
        try:
            self.grader.GenSubmitList(submitPath=submissiondir, recursive=True)
        except RuntimeError as e:
            self.displayError(f"Invalid submission path!\n{e}")
            return
        # Generate the grader
        self.gradeTab(self.grade)
        # If all that works we get ready to grade!
        self.currentStudent = self.grader.getCurrentStudent()
        self.updateStudentInfo()
        self.getCurrentGrades()
        self.tabs.tab(1,state="normal")

    
    def openSelectedSubmission(self, *args):
        pth = self.getSelectedPath()
        webbrowser.open(pth)

    
    def gradeNext(self):
        # First save the current values
        if self.groupGrade:
            print(f"groupGrade {self.currentStudent[0]} in group {self.groups.group(self.currentStudent[0])}")
            for nid in self.groups.students(self.groups.group(self.currentStudent[0])):
                self.grader.assignGradeStudent(netID=nid, grade = self.formatGrades())
        else:
            self.grader.assignGradeStudent(netID=self.currentStudent[0], grade = self.formatGrades())

        self.grader.exportGrades()
        self.currentStudent = self.grader.getNextStudent()
        # This should also open the submission 
        self.updateStudentInfo()
        self.getCurrentGrades()

    def gradePrev(self):
        # First save the current grades
        Errored = False
        if self.groupGrade:
            print(f"groupGrade {self.currentStudent[0]} in group {self.groups.group(self.currentStudent[0])}")
            try:
                for nid in self.groups.students(self.groups.group(self.currentStudent[0])):
                    self.grader.assignGradeStudent(netID=nid, grade = self.formatGrades())
            except TypeError:
                Errored = True 
        if (not self.groupGrade) or Errored:
            self.grader.assignGradeStudent(netID=self.currentStudent[0], grade = self.formatGrades())

        self.grader.exportGrades()

        self.currentStudent = self.grader.getPrevStudent()
        # This should also open the submission
        self.updateStudentInfo()
        self.getCurrentGrades()

    def genGroups(self, path:str=None):
        if path:
            self.importGroups(path)
        self.newGroups = True

    def saveGroups(self):
        """Save created groups to a csv file!
        """
        savepth = filedialog.asksaveasfilename(initialdir=DEFAULTPATH, filetypes=(("Comma Seperated Value", "*.csv"), ("all files", "*.*")))
        self.groups.exportGroups(savepth)

    def displayError(self, msg:str, title:str="Attention!"):
        messagebox.showerror(title=title, message=msg)
