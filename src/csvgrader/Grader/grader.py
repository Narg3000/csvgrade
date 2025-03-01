"""This handles the 

    Raises:
        RuntimeError: _description_
        RuntimeError: _description_

    Returns:
        _type_: _description_
    
    @author Autumn Bauman 
    """

import os
import pandas as pd

pd.options.mode.copy_on_write = True

class Grader:
    def __init__(self, gradebookPath:str=None, submitPath:str=None):

        # STATE VARIABLES
        self.currentStudent = 0
        self.studentsSubmitted = []
        self.numStudents = 0

        
        # Holds objects useful to this code
        self.rubric = None
        self.gradebook = None
        self.gradebookPath = gradebookPath
        self.submitPath = submitPath
        self.outPath = ""
        self.submitList = None
        # Convert to rubric index to grade column 
        self.columnIndex = {}
        # If we point to a gradebook it will load it automatically 
        if self.gradebookPath:
            self.importGradebook()
        else:
            self.gradebook=None
        if self.submitPath:
            self.GenSubmitList()




    def importGradebook(self, gradebookPath:str=None):
        """Imports gradebook from a csv file. THIS ASSUMES STANDARD MyPhysics Formatting and as a result is NOT GENERAL

        Args:
            gradebookPath (str, optional): Path to gradebook csv. Defaults to None.

        Raises:
            RuntimeError: No path specified on class creation or now
        """
        if gradebookPath:
            self.gradebookPath = gradebookPath
        if not self.gradebookPath:
            raise RuntimeError("No path specified!")
        try:
            self.gradebook = pd.read_csv(self.gradebookPath, dtype=str)
        except Exception as e:
            raise RuntimeError(f"Invalid gradebook format at path!:\n{e}")

        self.GenRubricItems()
        self.setRubricColumn()

        self.outPath = f"{self.gradebookPath[:-4]}_graded.csv"

    def GenSubmitList(self, submitPath:str=None, recursive:bool = False):
        """Sorts submissions by timestamp and netID for easy indexing 

        Args:
            submitpth (str): path tp submissions, should be a dir
            recursive (bool): Recursively loads submissions from subdirectories. This can only go one layer deep because I am lazy. Defaults to False

        Raises:
            RuntimeError: No submission path specified
            RuntimeError: path supplied is not a directory

        Returns:
            dict: {NetID:[ordered list of submissions of form [timestamp, path]]}
        """
        if submitPath: 
            self.submitPath = submitPath
        if not self.submitPath:
            raise RuntimeError("No submission directory provided")

        # Ensure we are pointed at a directory 
        if not os.path.isdir(self.submitPath):
            raise RuntimeError("Not a directory and/or does not exist")
        
        submitlist = [] # stores the list of strudent submissions 
        for f in os.listdir(self.submitPath):
            # Loads one dir deep (i.e. late submissions)
            if os.path.isdir(os.path.join(self.submitPath,f)) and recursive: 
                for i in os.listdir(os.path.join(self.submitPath,f)):
                    # Recusion stinky
                    if os.path.isdir:
                        continue

                    split = i.split("_")
                    #print(split)
                    submitlist.append([split[0],int(split[1].split(".")[0]), os.path.join(self.submitPath, f,i)])
                    
            elif os.path.isdir(os.path.join(self.submitPath,f)) and not recursive: 
                continue
            else:
                split = f.split("_")
                #print(split)
                submitlist.append([split[0],int(split[1].split(".")[0]), os.path.join(self.submitPath, f)])
        
        # converts to dataframe to make manipulation easier    
        submitlist = pd.DataFrame(submitlist,columns=["NetID","timestamp","path"])
        # Dictionary of netID:[list of submissions]. Most recent submission accessible at [0]
        self.submitList = {netid:submitlist[submitlist["NetID"] == netid][["timestamp", "path"]].sort_values(by="timestamp", ascending=False).values.tolist() for netid in submitlist.NetID.unique()}
        
        # We use this to itterate over the class later on, helps keep it nice and encapsulated
        self.studentsSubmitted = []
        # Make sure the student is in the gradebook, if not we skip them!
        for netid in self.submitList.keys():
            #print(netid)
            try:
                self.gradebook.loc[self.gradebook["Student NetID"] == netid,"Student First Name"].values[0]
                self.studentsSubmitted.append(netid)
            except:
                print(f"failed NID{netid}")
        self.numStudents = len(self.studentsSubmitted)
        print(self.numStudents, self.currentStudent)
        if self.numStudents == 0:
            raise RuntimeError("Can't start grading with no submissions in folder")

    def GenRubricItems(self):
        """Generate a rubric from the gradebook file as formatted by MyPhysics. 
        If you want this to be better you could add in the ability to specifiy arbitrary formatting
        but im a grad student and I ain't getting paid to use this

        Args:
            gradebookPath (str, optional): Path to gradebook csv file. Defaults to None.
        
        Raises: 
            RuntimeError: No path specified
        """
        if self.gradebook is None:
            return 
        # Extracts the rubric information from the gradebook file! 
        crit = self.gradebook[pd.notna(pd.to_numeric(self.gradebook["Rubric Section"], errors="coerce"))]
        # Extract the rucric chriteria from the assignment gradebook and makes a dictionary
        self.rubric = {str(i) : crit[crit["Rubric Section"] == i][["Version", "Student Section"]].set_index("Version").to_dict()["Student Section"] for i in crit["Rubric Section"].unique()}
        print(self.rubric)

    def setRubricColumn(self, columnIndex:dict=None):
        """Generates a mapping from rubric item to the column of the gradebook
        {item:(gradecol, comcol)}

        Args:
            columnIndex (dict, optional): If you want it can take a dictionary of these explicitly. 
            Why you would do this idfk but I support your right to. Defaults to None.
        """
        # dictionary of <rubricitem>:<gradebook column> used when exporting
        if columnIndex:
            self.columnIndex = columnIndex
            return
        # First column for grade input is 7 usually, but it is the one after the netID
        idx = self.gradebook.columns.get_loc("Student NetID")+1
        for q in self.rubric.keys():
            self.columnIndex[q] = (self.gradebook.columns[idx], self.gradebook.columns[idx+1])
            idx +=2 # inc by 2 to account for comments line 




    def getCurrentStudent(self):
        """returns information about the currently selected student

        Returns:
            _type_: _description_
        """
        netID = self.studentsSubmitted[self.currentStudent]
        submission = self.submitList[netID]
        first = self.gradebook.loc[self.gradebook["Student NetID"]==netID, "Student First Name"].values[0]
        last = self.gradebook.loc[self.gradebook["Student NetID"]==netID, "Student Last Name"].values[0]
        sec = self.gradebook.loc[self.gradebook["Student NetID"]==netID, "Student Section"].values[0]
        return (netID, submission, first, last, sec, f"{self.currentStudent+1}/{self.numStudents}", self.getStudentGrades())


    def getNextStudent(self):
        """Get submission and student information for the next student

        Returns:
            tuple: (netID, submissionsList, firstName, lastName, Section)
        """
        # Gives us wrapping 
        self.currentStudent += 1
        if self.currentStudent >= self.numStudents:
            self.currentStudent = 0
        # Increment
        return self.getCurrentStudent()

    def getPrevStudent(self):
        """Get submission and student information for the previous student

        Returns:
            tuple: (netID, submissionsList, firstName, lastName, Section)
        """
        # decrement
        self.currentStudent -= 1
        # Gives us wrapping 
        if self.currentStudent <= 0:
            self.currentStudent = self.numStudents-1
        return self.getCurrentStudent()


    def assignGradeStudent(self, netID:str, grade:dict):
        """Assigns grade to student, if the student has an EX this won't overwrite it

        Args:
            netID (str): Student NetID
            grade (dict): {<rubric category>:[<grade>, <comments>]}
        """
        #assigns a grade to a student across all categories. If ABS or EX is entered it will leave unchanged
        #print(self.rubric)
        #print(grade)

        # Ensure we don't overwrite abs or ex grades
        for cat in self.rubric.keys():
            cg = str(self.gradebook.loc[self.gradebook["Student NetID"] == netID,self.columnIndex[cat][0]].values[0]).upper()
            if  cg == "EX" or cg == "ABS":
                return

        for cat, grd in grade.items():

            self.gradebook.loc[self.gradebook["Student NetID"] == netID,self.columnIndex[cat][0]] = grd[0]
            self.gradebook.loc[self.gradebook["Student NetID"] == netID, self.columnIndex[cat][1]] = grd[1]
            

    
    def exportGrades(self, inplace:bool=True,):
        """Exports assigned grades to the file. If `inplace` it will overwrite the file and if customPath is set
        it will export to this.

        Args:
            inplace (bool, optional): Overwrites the file, if false it will strip the extension and append 'mod.csv' to the end. Defaults to True.
            customPath (str, optional): If you want to write it out . Defaults to gradebookPath.
        """
        
        self.gradebook.to_csv(self.outPath, index=False)

    def getStudentGrades(self):
        """Gets the current grade of currently selected student

        Returns:
            _type_: dictionary of grades
        """
        netID = self.studentsSubmitted[self.currentStudent]
        grades = {}
        for cat in self.rubric.keys():
            grd = str(self.gradebook.loc[self.gradebook["Student NetID"] == netID,self.columnIndex[cat][0]].values[0])
            com = str(self.gradebook.loc[self.gradebook["Student NetID"] == netID,self.columnIndex[cat][1]].values[0])
            grades[cat] = [grd if grd != "nan" else "", com if com !="nan" else ""]
        return grades


    def getStudentInfo(self, netID:str):
        """Return student info by netID, if netID not in gradebook returns None

        Args:
            netID (str): student NetID

        Returns:
            tuple: (firstname, lastname, section)
        """
        print(netID)
        if not (netID in self.gradebook["Student NetID"].values):
            #print(self.gradebook["Student NetID"].values)
            return None

        first = self.gradebook.loc[self.gradebook["Student NetID"]==netID, "Student First Name"]
        last = self.gradebook.loc[self.gradebook["Student NetID"]==netID, "Student Last Name"]
        sec = self.gradebook.loc[self.gradebook["Student NetID"]==netID, "Student Section"]
        return (first, last, sec)
    
    def getRoster(self):
        return self.gradebook[self.gradebook["Student NetID"] != ""][["Student First Name", "Student Last Name", "Student NetID"]].values
        
        

