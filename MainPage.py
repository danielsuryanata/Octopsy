import Tkinter
import tkFileDialog
import tkMessageBox
import pandas
import pyglet
import geoplotlib
from geoplotlib.colors import colorbrewer
from geoplotlib.utils import epoch_to_str, BoundingBox, read_csv
import matplotlib
import OctopsyImage
import datetime
import GPSConverter
import math
import os
import shutil

class MainMenuGUI:
    def __init__(self, ProjectPath, NewProject, ProjectName, InvestigatorName):
        # ProjectPath and ProjectName do not have the trailing '\'
        self.ProjectPath = ProjectPath
        self.ProjectName = ProjectName
        self.ListImage = []
        self.ListCamera = []
        self.ListAggregateAnomalies = []
        self.DictionaryAggregateSecondAnomaliesImage = {}
        self.DictionaryAggregateSecondAnomalies = {}
        self.ListPredictionCluster = []
        self.Log = []
        self.ListImagesName = []
        self.ListImagesDetails = []
        self.IsSaved = True
        self.CreateNewListImagesName = True
        self.Timeline = {} # a dictionary, which is directly inputed while adding, removing, or changing images
        self.FinalTimeline = [] # a list of string, which is a reflection of self.Timeline dictionary. This will be outputed to user via a textbox
        self.InvestigatorName = InvestigatorName

        # Create a main window
        self.MainWindow = Tkinter.Tk()
        self.MainWindow.title("Octopsy 0.0")

        # Create the first frames(top left) for the list of image
        self.TopFrame = Tkinter.Frame(self.MainWindow, bg='white')
        self.ListImageFrame = Tkinter.Frame(self.TopFrame, bg='white')

        # Create the second frame(top right) for the table
        self.TableFrame = Tkinter.Frame(self.TopFrame, bg='white')

        # Create a listbox and four buttons in the ListImageFrame and SecondRowButtonFrame
        self.ListBox = Tkinter.Listbox(self.ListImageFrame, bg='white', width=35, height=15)
        self.ListBox.pack(side='top')
        self.AddImageButton = Tkinter.Button(self.ListImageFrame, text="Add Image", command=self.chooseAFileGUI)
        self.AddImageButton.pack(side='left')
        self.DeleteImageButton = Tkinter.Button(self.ListImageFrame, text="Delete Image", command=self.testaja)
        self.DeleteImageButton.pack(side='left')

        # Prepare a file chooser
        self.file_opt = options = {}
        options['defaultextension'] = '.jpg'
        options['filetypes'] = [('all files', '.*'), ('JPG files', '.jpg')]
        options['initialdir'] = 'C:\\'
        options['title'] = 'Choose a file to be added'

        # Create a Text in TableFrame
        self.TableText = Tkinter.Text(self.TableFrame, width=70, height=18)
        #self.TableText.config(state="disabled")
        #self.TableText.pack(side='left')
        self.TableText.pack(side='left', fill="both", expand=True)
        self.TableText.config(wrap="word")

        self.TableScrollY = Tkinter.Scrollbar(self.TableFrame, command=self.TableText.yview)
        self.TableScrollY.grid(row=0, column=1, sticky='ns')
        self.TableText['yscrollcommand'] = self.TableScrollY.set
        self.TableScrollY.pack(side="right", fill="y", expand=False)

        # Pack all top frames in the MainWindows
        self.TopFrame.pack()
        self.ListImageFrame.pack(side='left')
        self.TableFrame.pack(side='right')

        # Create the third frame(middle) for the timeline
        self.TimelineFrame = Tkinter.Frame(self.MainWindow, bg='white')

        # Create a Text in TimelineFrame
        self.TimelineText = Tkinter.Text(self.TimelineFrame, bg='white', width=100, height=15)
        self.TimelineText.pack(side='left', fill="both", expand=True)
        self.TimelineText.config(wrap="word")

        self.TimelineScrollY = Tkinter.Scrollbar(self.TimelineFrame, command=self.TimelineText.yview)
        self.TimelineScrollY.grid(row=0, column=1, sticky='ns')
        self.TimelineText['yscrollcommand'] = self.TimelineScrollY.set
        self.TimelineScrollY.pack(side="right", fill="y", expand=False)

        self.TimelineFrame.pack()

        # Create the fourth frame (bottom) for the remaining buttons
        self.RemainingButtonsFrame = Tkinter.Frame(self.MainWindow, bg='white')

        # Create the remaining buttons (2 for predictions and 1 for visualization)
        self.FindAnomaliesButton = Tkinter.Button(self.RemainingButtonsFrame, text="Find Anomalies", command=self.generateAllAnomaliesGUI)
        self.FindAnomaliesButton.pack(side='left')
        self.PredictClusterButton = Tkinter.Button(self.RemainingButtonsFrame, text="Predict by Cluster", command=self.predictClusterGUI)
        self.PredictClusterButton.pack(side='left')
        self.PredictDistanceButton = Tkinter.Button(self.RemainingButtonsFrame, text="Predict by Distance", command=self.predictDistanceGUI)
        self.PredictDistanceButton.pack(side='left')
        self.VisualizationButton = Tkinter.Button(self.RemainingButtonsFrame, text="Visualize Map", command=self.visualizeMapGUI)
        self.VisualizationButton.pack(side='left')
        self.SaveButton = Tkinter.Button(self.RemainingButtonsFrame, text="Save Project", command=self.saveProjectGUI)
        self.SaveButton.pack(side='left')

        self.RemainingButtonsFrame.pack()

        if (NewProject):
            # Create the project directory
            NewDirectory = str(ProjectPath) + "\\" + str(ProjectName) + "\\"
            Directory = os.path.dirname(NewDirectory)
            if not os.path.exists(Directory):
                os.makedirs(Directory)
                LogContent = "Create directory " + ProjectName + " under " + ProjectPath + "."
                self.writeLog(LogContent)

                # Create the image directory
                NewDirectory += "Images\\"
                Directory = os.path.dirname(NewDirectory)
                if not os.path.exists(Directory):
                    os.makedirs(Directory)
                    LogContent = "Create Images directory for Project " + ProjectName + "."
                    self.writeLog(LogContent)

                    # Create Log file
                    self.saveLoadTextFile(False, 0)

                    # Create ListImage file
                    self.saveLoadTextFile(False, 1)
                else:
                    LogContent = "Images directory already exists."
                    self.writeLog(LogContent)
            else:
                LogContent = "Directory " + ProjectName + " already exists under " + ProjectPath + "."
                self.writeLog(LogContent)
        else:
            # Load ListImage file
            self.saveLoadTextFile(True, 1)

            # Recreate all images
            self.CreateNewListImagesName = False
            FullImagesPath = self.getImagesFullPath()

            for CurrentImageName in self.ListImagesName:
                FullPath = FullImagesPath + CurrentImageName
                self.uploadNewImage(FullPath)

            self.syncListBox()
            self.CreateNewListImagesName = True

        # Start the GUI
        self.MainWindow.configure(bg='white')
        self.MainWindow.mainloop()

    def readFullTimeline(self):
        for OneEvent in self.FinalTimeline:
            print(OneEvent)

    def syncTimeline(self):
        # Remove all items from the current timeline
        self.TimelineText.delete("1.0", "end")

        # Add text to self.TableText
        for i in range(0, len(self.FinalTimeline)):
            self.TimelineText.insert("end", self.FinalTimeline[i])
            self.TimelineText.insert("end", "\n")
        self.TimelineText.pack()

    def syncListBox(self):
        # Remove all items from the current ListBox
        self.ListBox.delete(0, "end")

        # Add all items in self.ListImagesName
        for CurrentImageName in self.ListImagesName:
            self.ListBox.insert("end", CurrentImageName)

        # Remove all items from the current table
        self.TableText.delete("1.0", "end")

        # Add text to self.TableText
        for i in range(0, len(self.ListImagesName)):
            self.TableText.insert("end", self.ListImagesName[i])
            self.TableText.insert("end", "\n")
            self.TableText.insert("end", self.ListImagesDetails[i])
            self.TableText.insert("end", "\n")
            self.TableText.insert("end", "=====================================================================")
            self.TableText.insert("end", "\n")
        self.TableText.pack()

    # The command for "Add Image" button
    def chooseAFileGUI(self):
        # Get filename
        filename = tkFileDialog.askopenfilename(**self.file_opt)
        filename = str(filename).replace('/', '\\')

        # Upload it to the project directory
        self.uploadNewImage(filename)

        # Show it in the ListBox
        self.syncListBox()

    # The command for "Find Anomalies" button
    def generateAllAnomaliesGUI(self):
        # Generate all aggregate anomalies
        self.findAggregateAnomaly()
        #self.predictLocationByCluster()
        self.generateAllTimeline()

        # Show it in the Timeline
        self.syncTimeline()

    # The command for "Predict by Cluster" button
    def predictClusterGUI(self):
        # do first prediction (by cluster)
        self.predictLocationByCluster()
        self.generateAllTimeline()

        # Show it in the Timeline
        self.syncTimeline()

    # The command for "Predict by Distance" button
    def predictDistanceGUI(self):
        # do first prediction (by cluster)
        self.predictLocationByDistance()
        self.generateAllTimeline()

        # Show it in the Timeline
        self.syncTimeline()

    # The command for "VisualizeMap" button
    def visualizeMapGUI(self):
        self.visualizeMap()

    # The command for "Save Project" button
    def saveProjectGUI(self):
        # Save Log and ListImage files
        self.saveLoadTextFile(False, 0)
        self.saveLoadTextFile(False, 1)

    def testaja(self):
        tkMessageBox.showinfo("Test", "Still in development")

    # Generate individual timeline
    def generateIndividualTimeline(self, Key, Value):
        if (Key in self.Timeline):
            del self.Timeline[Key]

        self.Timeline[Key] = Value

    # Generate all timeline -> basically calls all generateIndividualTimeline
    def generateAllTimeline(self):
        # Make FinalTimeline empty first
        self.FinalTimeline = []

        # Generate individual anomalies for each image
        self.FinalTimeline.append("Anomalies in individual images:")
        self.FinalTimeline.append("==================================================================================================")
        for Key in self.Timeline:
            if ((Key != "FirstAggregateAnomaly") and (Key!= "SecondAggregateAnomaly") and (Key != "SecondAggregateAnomalyImage")\
                and (Key!= "FirstPredictionName") and (Key!= "FirstPrediction") and (Key!= "HaveSecondPrediction") and (Key!= "SecondPrediction")):
                self.FinalTimeline.append("Image Name: " + Key)

                if (self.Timeline[Key][0] == 1): # First individual anomaly
                    self.FinalTimeline.append("Image was probably taken from inside a room (from analyzing the flash value).")

                if (self.Timeline[Key][1] == 1): # Second individual anomaly
                    self.FinalTimeline.append("Image was probably taken from from social media or the metadata has been wiped.")

                if (self.Timeline[Key][2] == 0): # Fourth individual anomaly
                    self.FinalTimeline.append("Image was probably taken from a short distance (from analyzing the zoom value).")
                elif (self.Timeline[Key][2] == 1):
                    self.FinalTimeline.append("Image was probably taken from a medium distance (from analyzing the zoom value).")
                elif (self.Timeline[Key][2] == 2):
                    self.FinalTimeline.append("Image was probably taken from a long distance (from analyzing the zoom value).")

                self.FinalTimeline.append("**************************************************************************************************")
        self.FinalTimeline.append("==================================================================================================")
        self.FinalTimeline.append("")

        # Generate first aggregate anomaly
        if ("FirstAggregateAnomaly" in self.Timeline):
            self.FinalTimeline.append("Number of Camera:")
            self.FinalTimeline.append("==================================================================================================")
            self.FinalTimeline.append("There is/are " + str(self.Timeline["FirstAggregateAnomaly"]) + " camera(s) in the project.")
            self.FinalTimeline.append("==================================================================================================")
            self.FinalTimeline.append("")
        else:
            self.FinalTimeline.append("There is no information about the number of camera yet")
            self.FinalTimeline.append("==================================================================================================")
            self.FinalTimeline.append("")

        # Generate second aggregate anomaly
        if (("SecondAggregateAnomalyImage" in self.Timeline) and ("SecondAggregateAnomaly" in self.Timeline)):
            self.FinalTimeline.append("Distance and Time Comparison Anomalies for Each Camera:")
            self.FinalTimeline.append("==================================================================================================")
            for Key in self.Timeline["SecondAggregateAnomalyImage"]:
                self.FinalTimeline.append("Camera: " + Key)
                TempListImage = self.Timeline["SecondAggregateAnomalyImage"][Key]
                TempListAnomaly = self.Timeline["SecondAggregateAnomaly"][Key]

                if (TempListAnomaly[0] == -2):
                    self.FinalTimeline.append("Not enough information to derive from this camera")
                else:
                    i = 0
                    j = 1
                    Limit = len(TempListImage)
                    while(j < Limit):
                        TransportMode = TempListAnomaly[i]
                        if (TransportMode == 0):
                            self.FinalTimeline.append("The mode of transportation from " + TempListImage[i].getShortName() + " to " + TempListImage[j].getShortName() + " is IMPOSSIBLE. Someone may be very likely to change the metadata (either time or location).")
                        elif (TransportMode == 1):
                            self.FinalTimeline.append("The mode of transportation from " + TempListImage[i].getShortName() + " to " + TempListImage[j].getShortName() + " is walking or two images have been separated for a long time.")
                        elif (TransportMode == 2):
                            self.FinalTimeline.append("The mode of transportation from " + TempListImage[i].getShortName() + " to " + TempListImage[j].getShortName() + " is car.")
                        elif (TransportMode == 3):
                            self.FinalTimeline.append("The mode of transportation from " + TempListImage[i].getShortName() + " to " + TempListImage[j].getShortName() + " is car")
                        else: # TransportMode == -1
                            self.FinalTimeline.append("Cannot determine mode of transportation due to incomplete metadata in either " + TempListImage[i].getShortName() + " or "  + TempListImage[j].getShortName())

                        i += 1
                        j += 1
                self.FinalTimeline.append("**************************************************************************************************")

            self.FinalTimeline.append("==================================================================================================")
            self.FinalTimeline.append("")
        else:
            self.FinalTimeline.append("There is no Distance and Time Comparison Anomalies for Each Camera yet")
            self.FinalTimeline.append("==================================================================================================")
            self.FinalTimeline.append("")

        # Generate the first prediction (prediction by cluster), if exist
        if (("FirstPredictionName" in self.Timeline) and ("FirstPrediction" in self.Timeline)):
            self.FinalTimeline.append("Location Prediction Based on Cluster:")
            self.FinalTimeline.append("==================================================================================================")
            for i in range(0, len(self.Timeline["FirstPredictionName"])):
                print("haha")
                self.FinalTimeline.append("Image " + self.Timeline["FirstPredictionName"][i] + " was located in " + self.Timeline["FirstPrediction"][i])

            self.FinalTimeline.append("==================================================================================================")
            self.FinalTimeline.append("")
        else:
            self.FinalTimeline.append("There is no Location Prediction Based on Cluster yet.")
            self.FinalTimeline.append("==================================================================================================")
            self.FinalTimeline.append("")

        # Generate the second prediction (prediction by distance), if exist
        if (("HaveSecondPrediction" in self.Timeline) and ("SecondPrediction" in self.Timeline)):
            self.FinalTimeline.append("Location Prediction Based on Distance and Time:")
            self.FinalTimeline.append("==================================================================================================")

            if (self.Timeline["HaveSecondPrediction"] == True):
                self.FinalTimeline.append("The next event occurence will be on " + self.Timeline["SecondPrediction"][0] + " at location (" + self.Timeline["SecondPrediction"][1] +", " + self.Timeline["SecondPrediction"][2] + ").")
            else:
                self.FinalTimeline.append("Cannot make prediction. Make sure to provide two valid images that contain timestamp and location data")
        else:
            self.FinalTimeline.append("There is no Location Prediction Based on Distance and Time yet.")
            self.FinalTimeline.append("==================================================================================================")
            self.FinalTimeline.append("")

    # Write to the log file with timestamp
    def writeLog(self, Content):
        FinalContent = str(datetime.datetime.now())
        FinalContent += ": "
        FinalContent += Content
        self.Log.append(FinalContent)

    # Return the full path to the Images folder of current project
    def getImagesFullPath(self):
        return (self.ProjectPath + "\\" + self.ProjectName + "\\Images\\")

    def generateImageDetails(self, CurrentImage):
        ImageDetails = "Vendor: " + str(CurrentImage.getMake()) + "\n"
        ImageDetails += "Model: " + str(CurrentImage.getModel()) + "\n"
        ImageDetails += "Date-Time: " + str(CurrentImage.getDateTimeOriginal()) + "\n"
        ImageDetails += "ISO Speed: " + str(CurrentImage.getISOSpeedRatings()) + "\n"
        if (CurrentImage.getFlash() == 0):
            ImageDetails += "Flash: off\n"
        else:
            ImageDetails += "Flash: on\n"
        ImageDetails += "Digital Zoom: " + str(CurrentImage.getDigitalZoomRatio())
        return ImageDetails

    # Create a new Octopsy's image
    def uploadNewImage(self, Path):
        # Create a new instance of image
        NewImage = OctopsyImage.OctopsyImage(Path)

        # Get only the image's name
        TempImageNameList = str(Path).split('\\')
        ImageNameOnly = TempImageNameList[len(TempImageNameList) - 1]

        # Get FullImagesPath
        FullImagesPath = self.getImagesFullPath()

        # Sort by timeline ascending
        if ((len(self.ListImage) == 0) or (NewImage.getListIndividualAnomalies()[1] == 1)): # Change if Individual List of Anomaly's order changes
            self.ListImage.append(NewImage)
            self.ListImagesDetails.append(self.generateImageDetails(NewImage))
            self.generateIndividualTimeline(ImageNameOnly, NewImage.getListIndividualAnomalies())
            if (self.CreateNewListImagesName == True):
                LogContent = "Add image " + ImageNameOnly + " to the project"
                self.writeLog(LogContent)
                self.ListImagesName.append(ImageNameOnly)
                shutil.copyfile(Path, FullImagesPath + ImageNameOnly)
        else:
            Placed = False
            Limit = len(self.ListImage)
            i = 0
            CurrentImage = self.ListImage[i]

            # Convert NewImage to TimeDate
            NewImageTimeDate = str(NewImage.getDateTimeOriginal())
            ListTemp1 = NewImageTimeDate.split(' ')
            ListTemp2 = ListTemp1[1].split(':')
            NewImageTime = datetime.time(hour=int(ListTemp2[0]), minute=int(ListTemp2[1]), second=int(ListTemp2[2]))
            ListTemp3 = ListTemp1[0].split(':')
            NewImageDate = datetime.date(year=int(ListTemp3[0]), month=int(ListTemp3[1]), day=int(ListTemp3[2]))

            while (Placed == False) and (i < Limit):
                CurrentImage = self.ListImage[i]

                if (CurrentImage.getListIndividualAnomalies()[1] == 1): # Change if Individual List of Anomaly's order changes+
                    self.ListImage.insert(i, NewImage)
                    self.ListImagesDetails.insert(i, self.generateImageDetails(NewImage))
                    self.generateIndividualTimeline(ImageNameOnly, NewImage.getListIndividualAnomalies())
                    if (self.CreateNewListImagesName == True):
                        LogContent = "Add image " + ImageNameOnly + " to the project"
                        self.writeLog(LogContent)
                        self.ListImagesName.insert(i, ImageNameOnly)
                        shutil.copyfile(Path, FullImagesPath + ImageNameOnly)
                    Placed = True
                else:
                    # Convert CurrentImage to TimeDate
                    CurrentImageTimeDate = str(CurrentImage.getDateTimeOriginal())
                    ListTemp1 = CurrentImageTimeDate.split(' ')
                    ListTemp2 = ListTemp1[1].split(':')
                    CurrentImageTime = datetime.time(hour=int(ListTemp2[0]), minute=int(ListTemp2[1]), second=int(ListTemp2[2]))
                    ListTemp3 = ListTemp1[0].split(':')
                    CurrentImageDate = datetime.date(year=int(ListTemp3[0]), month=int(ListTemp3[1]), day=int(ListTemp3[2]))

                    if (NewImageDate < CurrentImageDate):
                        self.ListImage.insert(i, NewImage)
                        self.ListImagesDetails.insert(i, self.generateImageDetails(NewImage))
                        self.generateIndividualTimeline(ImageNameOnly, NewImage.getListIndividualAnomalies())
                        if (self.CreateNewListImagesName == True):
                            LogContent = "Add image " + ImageNameOnly + " to the project"
                            self.writeLog(LogContent)
                            self.ListImagesName.insert(i, ImageNameOnly)
                            shutil.copyfile(Path, FullImagesPath + ImageNameOnly)
                        Placed = True
                    elif (NewImageDate > CurrentImageDate):
                        i += 1
                    else:
                        if (NewImageTime < CurrentImageTime):
                            self.ListImage.insert(i, NewImage)
                            self.ListImagesDetails.insert(i, self.generateImageDetails(NewImage))
                            self.generateIndividualTimeline(ImageNameOnly, NewImage.getListIndividualAnomalies())
                            if (self.CreateNewListImagesName == True):
                                LogContent = "Add image " + ImageNameOnly + " to the project"
                                self.writeLog(LogContent)
                                self.ListImagesName.insert(i, ImageNameOnly)
                                shutil.copyfile(Path, FullImagesPath + ImageNameOnly)
                            Placed = True
                        else:
                            i += 1

            if (Placed == False):
                self.ListImage.append(NewImage)
                self.ListImagesDetails.append(self.generateImageDetails(NewImage))
                self.generateIndividualTimeline(ImageNameOnly, NewImage.getListIndividualAnomalies())
                if (self.CreateNewListImagesName == True):
                    LogContent = "Add image " + ImageNameOnly + " to the project"
                    self.writeLog(LogContent)
                    self.ListImagesName.append(ImageNameOnly)
                    shutil.copyfile(Path, FullImagesPath + ImageNameOnly)

        self.modifyListCamera(NewImage)

    # Write to a text file -> used when saving the project (save log file or ListImage file)
    def saveLoadTextFile(self, Mode, FileType):
        # Mode = True -> load file
        # Mode = False -> save file
        # Filetype = 0 -> Log.txt
        # Filetype = 1 -> ListImage.txt

        FileName = ""
        CurrentList = []

        if (FileType == 0):
            FileName = "Log.txt"
            CurrentList = self.Log
        elif (FileType == 1):
            FileName = "ListImage.txt"
            CurrentList = self.ListImagesName
        else:
            if (Mode == True):
                LogContent = "Fail to load either Log.txt or ListImage.txt."
                self.writeLog(LogContent)
            else:
                LogContent = "Fail to save either Log.txt or ListImage.txt."
                self.writeLog(LogContent)

        if ((FileType == 0) or (FileType == 1)):
            try:
                NewProjectPath = str(self.ProjectPath) + "\\" + str(self.ProjectName) + "\\" + FileName
                if (Mode == True):
                    OutputFile = open(NewProjectPath, 'r')
                else:
                    if (FileType == 0):
                        OutputFile = open(NewProjectPath, 'a')
                    else:
                        OutputFile = open(NewProjectPath, 'w')

                # Read/Write all the lines to the file
                i = 0
                LastLine = len(CurrentList) - 1

                if (Mode == True):
                    CurrentList = []
                    Row = OutputFile.readline().rstrip('\n')
                    while (Row != ""):
                        CurrentList.append(Row)
                        Row = OutputFile.readline().rstrip('\n')

                    if (FileType == 0):
                        self.Log = CurrentList
                    elif (FileType == 1):
                        self.ListImagesName = CurrentList
                    else:
                        LogContent = "Error trying to read to either Log or ListImage file."
                        self.writeLog(LogContent)
                else:
                    for Row in CurrentList:
                        OutputFile.write(Row)
                        if (i != LastLine):
                            OutputFile.write('\n')
                        else:
                            i += 1

                    # Delete the content of the log list
                    if (FileType == 0):
                        self.Log = []
            except IOError:
                LogContent = "Error while trying to read/write to " + FileName + "."
                self.writeLog(LogContent)
            finally:
                OutputFile.close()

    # Visualize a map with a perfectly readable CSV file. Cast writeToCsv() first
    def showMap(self, CsvFile):
        data = read_csv(CsvFile)
        geoplotlib.dot(data, 'r')
        geoplotlib.labels(data, 'name', color=[0,0,255,255], font_size=10, anchor_x='center')
        geoplotlib.set_bbox(BoundingBox.KBH)
        geoplotlib.show()

    # Create a perfectly readable CSV file with the input of a list with comma separated value
    def writeToCsv(self, CsvFile, LocationList):
        OutputFile = open(CsvFile, 'w')

        # Write the CSV header first
        OutputFile.write("name,lat,lon")
        OutputFile.write('\n')

        # Write all the lines
        for Location in LocationList:
            OutputFile.write(Location)
            OutputFile.write('\n')

        OutputFile.close()

    # Create an ID for the camera by appending Make and Model
    # Return "Make-Model"
    def createImageID(self, CurrentImage):
        ListID = []
        ListID.append(str(CurrentImage.getMake()))
        ListID.append("-")
        ListID.append(str(CurrentImage.getModel()))
        StringID = "".join(ListID)
        return StringID

    # Modify ListCamera to anticipate new camera
    def modifyListCamera(self, CurrentImage):
        if ((CurrentImage.getMake()!="null") and (CurrentImage.getModel()!="null")):
            CurrentID = self.createImageID(CurrentImage)
            if (CurrentID not in self.ListCamera):
                self.ListCamera.append(CurrentID)

    # Append a location data to the list of location
    # Also do file ordering
    def createLocationList(self, LocationList, Number, Name, Latitude, Longitude):
        OutputLocation = Number + " - " + Name + "," + Latitude + "," + Longitude
        LocationList.append(OutputLocation)
        return LocationList

    # Determine what anomalies occurs in all pictures
    def findAggregateAnomaly(self):
        # First Anomaly: Compare model and make to determine whether there is more than 1 camera
        if (len(self.ListCamera) > 1):
            self.ListAggregateAnomalies.append(1)
            self.generateIndividualTimeline("FirstAggregateAnomaly", len(self.ListCamera))
        else:
            self.ListAggregateAnomalies.append(0)
            self.generateIndividualTimeline("FirstAggregateAnomaly", len(self.ListCamera))

        # Second Anomaly: Compare time difference and geographic location difference
        # ListAnomaly return 1 if in a short time difference, the geographic location difference is huge (return value from compareTwoTimeDistance = 0
        # Return 0 if there is one or less image
        # Return 2 if the return value from compareTwoTimeDistance is 1 or 2 or 3
        self.DictionaryAggregateSecondAnomaliesImage = {}
        # First, create the first dictionary (The dictionary of ListImage for each camera)
        for CurrentImage in self.ListImage:
            CurrentImageID = self.createImageID(CurrentImage)
            if (CurrentImage.getListIndividualAnomalies()[1] == 0):
                if (CurrentImageID not in self.DictionaryAggregateSecondAnomaliesImage):
                    TempListImage = []
                else:
                    TempListImage = self.DictionaryAggregateSecondAnomaliesImage[CurrentImageID]

                TempListImage.append(CurrentImage)
                self.DictionaryAggregateSecondAnomaliesImage[CurrentImageID] = TempListImage

        # Second, create the second dictionary (The dictionary of ListSecondAggregateAnomaly for each camera)
        self.DictionaryAggregateSecondAnomalies = {}

        for Key in self.DictionaryAggregateSecondAnomaliesImage:
            TempListImage = self.DictionaryAggregateSecondAnomaliesImage[Key]
            TempListAnomaly = []
            # -2 means that there is less than 2 images
            # -1 means that the metadata is not available
            # 0 means that IMPOSSIBLE (metadata changed)
            # 1 means walk or inconclusive
            # 2 means car
            # 3 means plane

            if ((len(TempListImage) == 0) or (len(TempListImage) == 1)):
                TempListAnomaly.append(-2)
            else:
                Image1Index = 0
                Image2Index = 1
                Limit = len(TempListImage)

                while (Image2Index < Limit):
                    Anomaly = self.compareTwoTimeDistance(TempListImage[Image1Index], TempListImage[Image2Index])
                    TempListAnomaly.append(Anomaly)
                    Image1Index += 1
                    Image2Index += 1

            # Add list to self.DictionaryAggregateSecondAnomalies
            self.DictionaryAggregateSecondAnomalies[Key] = TempListAnomaly

        # Add both dictionaries of second anomaly to timeline
        self.Timeline["SecondAggregateAnomalyImage"] = self.DictionaryAggregateSecondAnomaliesImage
        self.Timeline["SecondAggregateAnomaly"] = self.DictionaryAggregateSecondAnomalies

    # DO NOT CALL THIS ONE, BECAUSE THE DATA STRUCTURE OF THE SECOND AGGREGATE ANOMALY CHANGES
    def interpretAggregateAnomalyResult(self):
        if (self.ListAggregateAnomalies[0] == 1):
            print ("There is more than 1 camera")
        else:
            print ("There is only 1 camera")

        if (self.ListAggregateAnomalies[1] == 1):
            print ("There were metadata change(s), probably the timestamp or location")
        elif (self.ListAggregateAnomalies[1] ==2):
            print ("Transportation method detected")
        else:
            print ("No anomaly on the metadata")

    # Convert GPS format from OctopsyImage Datastructure to Decimal
    def convertGPS(self, ImageDMS, ImageDirection):
        GPSDMS = str(ImageDMS).replace('[', '')
        GPSDMS = GPSDMS.replace(']', '')
        GPSDMS = GPSDMS.replace(' ', '')

        Degrees = GPSDMS.split(',')[0]
        Minutes = GPSDMS.split(',')[1]
        SecondsTemp = GPSDMS.split(',')[2]
        Seconds = float(SecondsTemp.split('/')[0]) / float(SecondsTemp.split('/')[1])

        Direction = str(ImageDirection)

        dd = GPSConverter.dms2dd(Degrees, Minutes, Seconds, Direction)
        return dd

    def calculateDelta(self, Float1, Float2):
        return abs(Float1 - Float2)

    # Compare two images for the possibility of reaching the delta difference in delta time
    def compareTwoTimeDistance(self, Image1, Image2):
        # Change if Individual List of Anomaly's order changes
        Image1Anomaly = Image1.getListIndividualAnomalies()[1]
        Image2Anomaly = Image2.getListIndividualAnomalies()[1]

        if ((Image1Anomaly == 1) or (Image2Anomaly == 1)):
            return -1
        else:
            if ((Image1.getGPSLatitude() != "null") and (Image1.getGPSLatitudeRef() != "null") and (Image1.getGPSLongitude() != "null") and (Image1.getGPSLongitudeRef() != "null") \
                and (Image2.getGPSLatitude() != "null") and (Image2.getGPSLatitudeRef() != "null") and (Image2.getGPSLongitude() != "null") and (Image2.getGPSLongitudeRef() != "null")\
                and (Image1.getDateTimeOriginal() != "null") and (Image2.getDateTimeOriginal() != "null")):
                # Convert Image1 GPS
                Image1Latitude = self.convertGPS(Image1.getGPSLatitude(), Image1.getGPSLatitudeRef())
                Image1Longitude = self.convertGPS(Image1.getGPSLongitude(), Image1.getGPSLongitudeRef())
                #print("Image1 Lat: " + str(Image1Latitude))
                #print("Image1 Long: " + str(Image1Longitude))

                # Convert Image1 to TimeDate
                Image1TimeDate = str(Image1.getDateTimeOriginal())
                ListTemp1 = Image1TimeDate.split(' ')
                ListTemp2 = ListTemp1[1].split(':')
                ListTemp3 = ListTemp1[0].split(':')
                Image1FinalDateTime = datetime.datetime(year=int(ListTemp3[0]), month=int(ListTemp3[1]), day=int(ListTemp3[2]), hour=int(ListTemp2[0]), minute=int(ListTemp2[1]), second=int(ListTemp2[2]))
                #print("Image1 Final Date Time: " + str(Image1FinalDateTime))

                # Convert Image2 GPS
                Image2Latitude = self.convertGPS(Image2.getGPSLatitude(), Image2.getGPSLatitudeRef())
                Image2Longitude = self.convertGPS(Image2.getGPSLongitude(), Image2.getGPSLongitudeRef())
                #print("Image2 Lat: " + str(Image2Latitude))
                #print("Image2 Long: " + str(Image2Longitude))

                # Convert Image2 to TimeDate
                Image2TimeDate = str(Image2.getDateTimeOriginal())
                ListTemp1 = Image2TimeDate.split(' ')
                ListTemp2 = ListTemp1[1].split(':')
                ListTemp3 = ListTemp1[0].split(':')
                Image2FinalDateTime = datetime.datetime(year=int(ListTemp3[0]), month=int(ListTemp3[1]), day=int(ListTemp3[2]), hour=int(ListTemp2[0]), minute=int(ListTemp2[1]), second=int(ListTemp2[2]))
                #print("Image2 Final Date Time: " + str(Image2FinalDateTime))

                LatitudeDistance = self.calculateDelta(Image1Latitude, Image2Latitude)
                LongitudeDistance = self.calculateDelta(Image1Longitude, Image2Longitude)
                #print("Delta Latitude: " + str(LatitudeDistance))
                #print("Delta Longitude: " + str(LongitudeDistance))

                # Begin Comparison
                if (Image1FinalDateTime > Image2FinalDateTime):
                    TimeDelta = Image1FinalDateTime - Image2FinalDateTime
                else:
                    TimeDelta = Image2FinalDateTime - Image1FinalDateTime
                #print("Time Delta: " + str(TimeDelta))

                TimeDeltaTotalSeconds = TimeDelta.total_seconds()
                #print("Time Delta in seconds: " + str(TimeDeltaTotalSeconds))

                Distance = self.calculateDiagonal(LatitudeDistance, LongitudeDistance)
                #print("Distance: " + str(Distance))

                # To handle division by zero
                if (self.compareTwoSmallFloats(0.0, TimeDeltaTotalSeconds)):
                    if (self.compareTwoSmallFloats(0.0, Distance)):
                        return 1
                    else:
                        return 0
                else:
                    Speed = Distance / TimeDeltaTotalSeconds
                    #print("Speed: " + str(Speed))

                    # Comparison
                    # Walk/run/cycle or long difference in time (Min 5 minutes from Hamburg to PNC): up to 1.31573891364848250006434192009e-5/second
                    # Car (Min 30 seconds from Hamburg to PNC): up to 1.31573891364848250006434192009e-4/second
                    # Plane (Min 2 seconds from Hamburg to PNC): up to 0.00197360837047272375009651288014/second
                    if (Speed <= 1.31573891364848250006434192009e-5):
                        return 1
                    elif (Speed <= 1.31573891364848250006434192009e-4):
                        return 2
                    elif (Speed <= 0.00197360837047272375009651288014):
                        return 3
                    else:
                        return 0
            else:
                return -1

    def calculateDiagonal(self, DeltaLatitude, DeltaLongitude):
        TotalDiagonal = DeltaLatitude**2 + DeltaLongitude**2
        return math.sqrt(TotalDiagonal)

    # Create one prediction cluster from the text file
    def createPredictionCluster(self, TheClusterFile):
        try:
            ListCluster = []
            User_file_object = open(TheClusterFile, 'r')
            TheCluster = User_file_object.readline().rstrip('\n')

            while (TheCluster != ""):
                ListCluster.append(TheCluster)
                TheCluster = User_file_object.readline().rstrip('\n')

            return ListCluster
        except IOError:
            print('An error occured trying to read from the file')
        finally:
            User_file_object.close()

    # The first GPS Prediction
    def predictLocationByCluster(self):
        # Preloaded prediction Clusters
        self.ListPredictionCluster.append("") # Redacted path for privacy purpose
        ListAllClusters = []

        # Load all clusters
        NumOfCluster = len(self.ListPredictionCluster)
        for i in range(0, NumOfCluster):
            ListAllClusters.append(self.createPredictionCluster(self.ListPredictionCluster[0]))

        # Match all images in ListImage to all points in each cluster
        ListResultName = []
        ListResultPlace = []
        ImageLimit = len(self.ListImage)
        for i in range(0, ImageLimit):
            # Get GPS information of the Image
            CurrentImage = self.ListImage[i]

            # Check Second Individual Anomaly
            if ((CurrentImage.getListIndividualAnomalies()[1] != 1) and (CurrentImage.getGPSLatitude() != "null") \
                and (CurrentImage.getGPSLatitudeRef() != "null") and (CurrentImage.getGPSLongitude() != "null")\
                and (CurrentImage.getGPSLongitudeRef() != "null")):
                #print("Nih: " + CurrentImage.getPath())
                ImageLatitude = self.convertGPS(CurrentImage.getGPSLatitude(), CurrentImage.getGPSLatitudeRef())
                ImageLongitude = self.convertGPS(CurrentImage.getGPSLongitude(), CurrentImage.getGPSLongitudeRef())
                #print("Lat: " + str(ImageLatitude))
                #print("Long: " + str(ImageLongitude))

                for j in range(0, NumOfCluster):
                    ListCurrentCluster = ListAllClusters[j]
                    Match = False
                    k = 0

                    while ((k < len(ListCurrentCluster)) and (Match == False)):
                        PlaceName = str(ListCurrentCluster[k]).split(',')[0]

                        # Sort latitude and Longitude
                        SmallerLatitude = 0.0
                        BiggerLatitude = 0.0
                        SmallerLongitude = 0.0
                        BiggerLongitude = 0.0

                        if (self.compareTwoSmallFloats(float(str(ListCurrentCluster[k]).split(',')[1]), float(str(ListCurrentCluster[k]).split(',')[3]))):
                            SmallerLatitude = float(str(ListCurrentCluster[k]).split(',')[1])
                            BiggerLatitude = float(str(ListCurrentCluster[k]).split(',')[3])
                        else:
                            SmallerLatitude = float(str(ListCurrentCluster[k]).split(',')[3])
                            BiggerLatitude = float(str(ListCurrentCluster[k]).split(',')[1])

                        if (self.compareTwoSmallFloats(float(str(ListCurrentCluster[k]).split(',')[2]), float(str(ListCurrentCluster[k]).split(',')[4]))):
                            SmallerLongitude = float(str(ListCurrentCluster[k]).split(',')[2])
                            BiggerLongitude = float(str(ListCurrentCluster[k]).split(',')[4])
                        else:
                            SmallerLongitude = float(str(ListCurrentCluster[k]).split(',')[4])
                            BiggerLongitude = float(str(ListCurrentCluster[k]).split(',')[2])

                        if (self.compareTwoSmallFloats(SmallerLatitude, ImageLatitude) and self.compareTwoSmallFloats(ImageLatitude, BiggerLatitude) and self.compareTwoSmallFloats(SmallerLongitude, ImageLongitude) and self.compareTwoSmallFloats(ImageLongitude, BiggerLongitude)):
                            Match = True
                            ListResultName.append(CurrentImage.getShortName())
                            ListResultPlace.append(PlaceName)
                        else:
                            k += 1

        # Write to timeline
        self.generateIndividualTimeline("FirstPredictionName", ListResultName)
        self.generateIndividualTimeline("FirstPrediction", ListResultPlace)

        # # Delete both keys from timeline if exist
        # if ("FirstPredictionName" in self.Timeline):
        #     del self.Timeline["FirstPredictionName"]
        #
        # if ("FirstPrediction" in self.Timeline):
        #     del self.Timeline["FirstPrediction"]
        #
        # # Replace with the new ones
        # self.Timeline["FirstPredictionName"] = ListResultName
        # self.Timeline["FirstPrediction"] = ListResultPlace

    # Whether Float1 <= Float2
    def compareTwoSmallFloats(self, Float1, Float2):
        if (Float2 - Float1 <= 0.000001):
            return True
        else:
            return False

    # The second GPS Prediction
    # The method is by averaging all images that have GPS and time information
    def predictLocationByDistance(self):
        TotalImages = len(self.ListImage)
        TotalLatitudeAccumulated = 0.0
        TotalLongitudeAccumulated = 0.0
        TotalTimeAccumulated = 0.0
        TotalValidDistance = 0
        LastValidImage = 0
        FirstValidImage = False

        # For Visualization
        ListValidImage = []
        ListValidLatitude = []
        ListValidLongitude = []

        if ((TotalImages == 0) or (TotalImages == 1)):
            self.generateIndividualTimeline("HaveSecondPrediction", False)
            #return "Cannot make prediction. Make sure to provide two valid images that contain timestamp and location data"
        else:
            Image1Index = 0
            Image2Index = 1
            Image1 = self.ListImage[Image1Index]
            Image2 = self.ListImage[Image2Index]
            Stop = False

            while (Stop == False):
                # Change if Individual List of Anomaly's order changes
                Image1Anomaly = Image1.getListIndividualAnomalies()[1]
                Image2Anomaly = Image2.getListIndividualAnomalies()[1]

                if ((Image1Anomaly == 1) or (Image2Anomaly == 1)):
                    Stop = True
                else:
                    if ((Image1.getGPSLatitude() != "null") and (Image1.getGPSLatitudeRef() != "null") and (Image1.getGPSLongitude() != "null") and (Image1.getGPSLongitudeRef() != "null") \
                        and (Image2.getGPSLatitude() != "null") and (Image2.getGPSLatitudeRef() != "null") and (Image2.getGPSLongitude() != "null") and (Image2.getGPSLongitudeRef() != "null")\
                        and (Image1.getDateTimeOriginal() != "null") and (Image2.getDateTimeOriginal() != "null")):
                        # Convert Image1 GPS
                        Image1Latitude = self.convertGPS(Image1.getGPSLatitude(), Image1.getGPSLatitudeRef())
                        Image1Longitude = self.convertGPS(Image1.getGPSLongitude(), Image1.getGPSLongitudeRef())

                        # Convert Image1 to TimeDate
                        Image1TimeDate = str(Image1.getDateTimeOriginal())
                        ListTemp1 = Image1TimeDate.split(' ')
                        ListTemp2 = ListTemp1[1].split(':')
                        ListTemp3 = ListTemp1[0].split(':')
                        Image1FinalDateTime = datetime.datetime(year=int(ListTemp3[0]), month=int(ListTemp3[1]), day=int(ListTemp3[2]), hour=int(ListTemp2[0]), minute=int(ListTemp2[1]), second=int(ListTemp2[2]))

                        # Convert Image2 GPS
                        Image2Latitude = self.convertGPS(Image2.getGPSLatitude(), Image2.getGPSLatitudeRef())
                        Image2Longitude = self.convertGPS(Image2.getGPSLongitude(), Image2.getGPSLongitudeRef())

                        # Convert Image2 to TimeDate
                        Image2TimeDate = str(Image2.getDateTimeOriginal())
                        ListTemp1 = Image2TimeDate.split(' ')
                        ListTemp2 = ListTemp1[1].split(':')
                        ListTemp3 = ListTemp1[0].split(':')
                        Image2FinalDateTime = datetime.datetime(year=int(ListTemp3[0]), month=int(ListTemp3[1]), day=int(ListTemp3[2]), hour=int(ListTemp2[0]), minute=int(ListTemp2[1]), second=int(ListTemp2[2]))

                        LatitudeDistance = Image2Latitude - Image1Latitude
                        LongitudeDistance = Image2Longitude - Image1Longitude

                        if (Image1FinalDateTime > Image2FinalDateTime):
                            TimeDelta = Image1FinalDateTime - Image2FinalDateTime
                        else:
                            TimeDelta = Image2FinalDateTime - Image1FinalDateTime

                        TimeDeltaTotalSeconds = TimeDelta.total_seconds()

                        TotalLatitudeAccumulated += LatitudeDistance
                        TotalLongitudeAccumulated += LongitudeDistance
                        TotalTimeAccumulated += TimeDeltaTotalSeconds
                        TotalValidDistance += 1
                        LastValidImage = Image2Index

                        if (FirstValidImage == False):
                            ListValidImage.append(Image1Index)
                            ListValidLatitude.append(Image1Latitude)
                            ListValidLongitude.append(Image1Longitude)
                            FirstValidImage = True

                        ListValidImage.append(Image2Index)
                        ListValidLatitude.append(Image2Latitude)
                        ListValidLongitude.append(Image2Longitude)

                        Image1Index += 1
                        Image2Index += 1
                    else:
                        Image1Index += 1
                        Image2Index += 1

                    if (Image2Index == TotalImages):
                        Stop = True
                    else:
                        Image1 = self.ListImage[Image1Index]
                        Image2 = self.ListImage[Image2Index]

            if (TotalValidDistance >= 1):
                AverageLatitude = TotalLatitudeAccumulated / TotalValidDistance
                AverageLongitude = TotalLongitudeAccumulated / TotalValidDistance
                AverageTime = TotalTimeAccumulated // TotalValidDistance
                #print("Average Latitude: " + str(AverageLatitude))
                #print("Average Longitude: " + str(AverageLongitude))
                #print("Average Time: " + str(AverageTime))

                # Add the average distance and time to the prediction
                PredictionImage = self.ListImage[LastValidImage]
                PredictionLatitude = self.convertGPS(PredictionImage.getGPSLatitude(), PredictionImage.getGPSLatitudeRef())
                PredictionLongitude = self.convertGPS(PredictionImage.getGPSLongitude(), PredictionImage.getGPSLongitudeRef())
                #print("Prediction Latitude: " + str(PredictionLatitude))
                #print("Prediction Longitude: " + str(PredictionLongitude))
                PredictionLatitude += AverageLatitude
                PredictionLongitude += AverageLongitude
                #print("Prediction Latitude: " + str(PredictionLatitude))
                #print("Prediction Longitude: " + str(PredictionLongitude))

                PredictionImageTimeDate = str(PredictionImage.getDateTimeOriginal())
                ListTemp1 = PredictionImageTimeDate.split(' ')
                ListTemp2 = ListTemp1[1].split(':')
                ListTemp3 = ListTemp1[0].split(':')
                PredictionImageFinalDateTime = datetime.datetime(year=int(ListTemp3[0]), month=int(ListTemp3[1]), day=int(ListTemp3[2]), hour=int(ListTemp2[0]), minute=int(ListTemp2[1]), second=int(ListTemp2[2]))
                PredictionTimeDelta = datetime.timedelta(seconds=AverageTime)
                PredictionDateTime = PredictionImageFinalDateTime + PredictionTimeDelta
                #print("Prediction Date Time: " + str(PredictionDateTime))

                # Insert into timeline
                self.generateIndividualTimeline("HaveSecondPrediction", True)
                ListTempPrediction = []
                ListTempPrediction.append(str(PredictionDateTime))
                ListTempPrediction.append(str(PredictionLatitude))
                ListTempPrediction.append(str(PredictionLongitude))
                self.generateIndividualTimeline("SecondPrediction", ListTempPrediction)

                # Visualize Map
                LocationList = []

                # Write all the prediction's inputs to the CSV file
                i = 0
                while(i < len(ListValidImage)):
                    CurrentImageIndex = ListValidImage[i]
                    LocationList = self.createLocationList(LocationList, str(i+1), self.ListImage[CurrentImageIndex].getShortName(), str(ListValidLatitude[i]), str(ListValidLongitude[i]))
                    i += 1

                # Write the prediction to the CSV file
                LocationList = self.createLocationList(LocationList, "Prediction", str(PredictionDateTime), str(PredictionLatitude), str(PredictionLongitude))

                self.writeToCsv("", LocationList) # Redacted path for privacy purpose
                self.showMap("") # Redacted path for privacy purpose

                return ("Prediction generated.")
            else:
                self.generateIndividualTimeline("HaveSecondPrediction", False)
                #return "Cannot make prediction. Make sure to provide two valid images that contain timestamp and location data"

    def visualizeMap(self):
        # Visualize Map
        LocationList = []

        # Write all the prediction's inputs to the CSV file
        i = 0
        while(i < len(self.ListImage)):
            CurrentImage = self.ListImage[i]
            if ((CurrentImage.getGPSLatitude() != "null") and (CurrentImage.getGPSLongitude() != "null") and (CurrentImage.getGPSLatitudeRef() != "null") and (CurrentImage.getGPSLongitudeRef() != "null")):
                CurrentImageLatitude = self.convertGPS(CurrentImage.getGPSLatitude(), CurrentImage.getGPSLatitudeRef())
                CurrentImageLongitude = self.convertGPS(CurrentImage.getGPSLongitude(), CurrentImage.getGPSLongitudeRef())
                LocationList = self.createLocationList(LocationList, str(i+1), CurrentImage.getShortName(), str(CurrentImageLatitude), str(CurrentImageLongitude))

            i += 1

        MapPath = "" + self.ProjectName + ".csv"  # Redacted path for privacy purpose
        self.writeToCsv(MapPath, LocationList)
        self.showMap(MapPath)

    #def deleteImage(self):

def main():
    # Create New Project
    TheGUI = MainMenuGUI("", True, "TestProject", "Daniel Suryanata")  # Redacted path for privacy purpose


def main1():
    TheGUI = MainMenuGUI("", True, "TestProject", "Daniel Suryanata")  # Redacted path for privacy purpose

# Call the main() function
#main()