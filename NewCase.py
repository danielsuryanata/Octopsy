import Tkinter
import tkMessageBox
import MainMenu
import MainPage

class NewCaseGUI:
    def __init__(self):
        # Create a main window
        self.MainWindow = Tkinter.Tk()
        self.MainWindow.title("Octopsy 0.0")

        # Create frames
        self.TitleFrame = Tkinter.Frame(self.MainWindow, bg="white")
        self.CaseNameFrame = Tkinter.Frame(self.MainWindow, bg="white")
        self.InvestigatorNameFrame = Tkinter.Frame(self.MainWindow, bg="white")
        self.PathFrame = Tkinter.Frame(self.MainWindow, bg="white")
        self.ButtonFrame = Tkinter.Frame(self.MainWindow, bg="white")

        # Add a title label to the frame
        self.TitleLabel = Tkinter.Label(self.TitleFrame, text="New Case", bg="white")
        self.TitleLabel.config(font=("Arial", 26))
        self.TitleLabel.pack(side='top')

        # Create and pack menu bar
        # self.MenuBar = Tkinter.Menu(self.MainWindow)
        # self.FileMenu = Tkinter.Menu(self.MenuBar, tearoff=0)
        # self.FileMenu.add_command(label="New Case", command=self.newCommand)
        # # To do: disable the New Case
        # self.MainWindow.config(menu=self.MenuBar)
        # self.MenuBar.add_cascade(label="File", menu=self.FileMenu)

        # Add Directory Browser's options
        self.dir_opt = options = {}
        options['initialdir'] = 'C:\\'
        options['mustexist'] = True
        options['title'] = 'Browse a directory where the project will be created'

        # Add textboxes
        self.CaseNameLabel = Tkinter.Label(self.CaseNameFrame, text="Case Name", bg="white", width=20)
        self.CaseNameEntry = Tkinter.Entry(self.CaseNameFrame)
        self.CaseNameLabel.pack(side='left')
        self.CaseNameEntry.pack(side='left')
        self.InvestigatorNameLabel = Tkinter.Label(self.InvestigatorNameFrame, text="Investigator Name", bg="white", width=20)
        self.InvestigatorNameEntry = Tkinter.Entry(self.InvestigatorNameFrame)
        self.InvestigatorNameLabel.pack(side='left')
        self.InvestigatorNameEntry.pack(side='left')
        #self.PathLabel = Tkinter.Label(self.PathFrame, text="Path", bg="white", width=20)
        #self.PathEntry = tkinter.Entry(self.PathFrame)
        #self.BrowsePath = tkinter.Button(self.PathFrame, text="Browse", command=self.browseCommand)
        #self.PathLabel.pack(side='left')
        #self.PathEntry.pack(side='left')

        # Create buttons
        self.DoneButton = Tkinter.Button(self.ButtonFrame, text="Done", command=self.newCommand)
        self.CancelButton = Tkinter.Button(self.ButtonFrame, text="Cancel", command=self.cancelCommand)
        self.DoneButton.pack(side='left')
        self.CancelButton.pack(side='left')

        # Pack all frames in the MainWindows
        self.TitleFrame.pack(side="top")
        self.CaseNameFrame.pack(side="top")
        self.InvestigatorNameFrame.pack(side="top")
        self.PathFrame.pack(side="top")
        self.ButtonFrame.pack(side="top")

        # Start the GUI
        self.MainWindow.configure(bg='white')
        self.MainWindow.mainloop()

    def newCommand(self):
        ProjectName = self.CaseNameEntry.get()
        InvestigatorName = self.InvestigatorNameEntry.get()
        self.MainWindow.destroy()
        TheGUI = MainPage.MainMenuGUI("", True, ProjectName, InvestigatorName)  # Redacted path for privacy purpose

    def doneCommand(self):
        tkMessageBox.showinfo("Test", "Done")

    def cancelCommand(self):
        Result = tkMessageBox.askquestion("Cancel", "All information will be lost if you go back to main menu. Are You Sure?", icon='warning')
        if Result == 'yes':
            self.MainWindow.destroy()
            MainMenuWindow = MainMenu.MainMenuGUI()

    #def browseCommand(self):
    #    return tkFileBrowser.askopendirname(parent='C:\\')

def main():
    TheGUI = NewCaseGUI()

# Call the main() function
#main()