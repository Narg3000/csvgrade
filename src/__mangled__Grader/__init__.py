import os
import pandas as pd
import webbrowser



class Groups:
    def __init__(self, groupFile=None):
        if groupFile:
            self.readGroupJson()
            return
        self.grps = {}

    def addStudent(self, group, netID):
        self.grps[group].append(netID)

    def initGroup(self, group:int, netID:list):
        self.grps[group]=netID


    def readGroupJson(self):
        pass


class Grader:
    def __init__(self, gradebookPath:str, submitPath:str):

        self.gradebookPath = gradebookPath
        self.submitPath = submitPath
        # Import the gradebook from MyPhysics
        self.gradebook  = pd.read_csv(gradebookPath, dtype=str)
        self.rubric = self.GenRubric()
        self.GenSubmitList()

    def GenSubmitList(self):
        """Sorts submissions by timestamp and netID for easy indexing 

        Args:
            submitpth (str): path tp submissions, should be a dir

        Raises:
            RuntimeError: path supplied is not a directory

        Returns:
            dict: {NetID:[ordered list of submissions of form [timestamp, path]]}
        """
        if not os.path.isdir(self.submitPath):
            raise RuntimeError("Not a directory and/or does not exist")
        submitlist = []
        for i in os.listdir(self.submitPath):
            if os.path.isdir(os.path.join(self.submitPath,i)): 
                continue
            split = i.split("_")
            #print(split)
            submitlist.append([split[0],int(split[1].split(".")[0]), i])
        submitlist = pd.DataFrame(submitlist,columns=["NetID","timestamp","path"])
        self.submitList = {netid:submitlist[submitlist["NetID"] == netid][["timestamp", "path"]].sort_values(by="timestamp").values.tolist() for netid in submitlist.NetID.unique()}

    def GenRubric(self):
        crit = self.gradebook[pd.notna(pd.to_numeric(self.gradebook["Rubric Section"], errors="coerce"))]
        # Extract the rucric chriteria from the assignment gradebook
        return {i : crit[crit["Rubric Section"] == i][["Version", "Student Section"]].set_index("Version").to_dict() for i in crit["Rubric Section"].unique()}

    def gradeClass(self):
        if input("start? ") == "n":
            print("nope")
            return
        for netid in self.submitList.keys():
            try:
                print(f"NetID: {netid}, Name: {self.gradebook.loc[self.gradebook["Student NetID"] == netid,"Student First Name"].values[0]}")
            except:
                print(f"NetID {netid} not in gradebook, skipping...")
                continue
            webbrowser.open(os.path.join(self.submitPath,self.submitList[netid][-1][1]))
            gradeIn = input("Enter Assigned Grade for contract (1/0 pass fail): ") 
            while True:
                if gradeIn == "1":
                    grade = "2_1"
                    break
                elif gradeIn == "0":
                    grade = "1_1"
                    break
                elif gradeIn == 'x':
                    raise RuntimeError("lol fuck you")
                else:
                    gradeIn = input("Enter Assigned Grade for contract u bitch (1/0 pass fail): ")
            comment = input("Comments?: ")
            self.gradebook.loc[self.gradebook["Student NetID"] == netid,"Q#1: The contract..."] = grade
            self.gradebook.loc[self.gradebook["Student NetID"] == netid, "Q#1 Comments"] = comment

    
    def exportGrades(self):
        self.gradebook.to_csv(str(self.gradebookPath[:-4]+"mod.csv"))
