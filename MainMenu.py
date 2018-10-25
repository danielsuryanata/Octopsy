import Tkinter
import tkMessageBox
import tkFileDialog

import NewCase
import MainPage

class MainMenuGUI:
    def __init__(self):
        # Create a main window
        self.MainWindow = Tkinter.Tk()
        self.MainWindow.title("Octopsy 0.0")

        # Create the first frame to hold Program's name and logo
        self.NameLogoFrame = Tkinter.Frame(self.MainWindow)

        # Create the second frame to hold buttons
        self.CaseFrame = Tkinter.Frame(self.MainWindow, bg='white', width=600, height=50)

        # Insert logo
        #self.LogoCanvas = tkinter.Canvas(self.NameLogoFrame, width=600, height=350)
        self.LogoCanvas = Tkinter.Canvas(self.NameLogoFrame, bg='white', width=600, height=350)
        Octopsy = Tkinter.PhotoImage(file="Octopsy.gif", width=1200, height=700)
        self.LogoCanvas.create_image(0, 0, image=Octopsy)
        self.LogoCanvas.pack()

        # Create and pack menu bar
        # self.MenuBar = Tkinter.Menu(self.MainWindow)
        # self.FileMenu = Tkinter.Menu(self.MenuBar, tearoff=0)
        # self.FileMenu.add_command(label="New Case", command=self.newCommand)
        # self.MainWindow.config(menu=self.MenuBar)
        # self.MenuBar.add_cascade(label="File", menu=self.FileMenu)

        # Create buttons
        self.NewCaseButton = Tkinter.Button(self.CaseFrame, text="New Case", command=self.newCaseCommandGUI)
        self.LoadCaseButton = Tkinter.Button(self.CaseFrame, text="Load Case", command=self.loadCaseCommandGUI)
        self.NewCaseButton.pack(side='top')
        self.LoadCaseButton.pack(side='top')

        # Prepare a directory chooser
        self.dir_opt = options = {}
        options['initialdir'] = 'C:\\'
        options['title'] = "Choose the project's directory"

        # Pack all frames in the MainWindows
        self.NameLogoFrame.pack()
        self.CaseFrame.pack()

        # Start the GUI
        self.MainWindow.configure(bg='white')
        self.MainWindow.mainloop()

    def newCommand(self):
        tkMessageBox.showinfo("Test", "This is test for menu bar")

    def newCaseCommandGUI(self):
        self.MainWindow.destroy()
        NewCaseWindow = NewCase.NewCaseGUI()

    def loadCaseCommandGUI(self):
        # Get filename
        DirName = tkFileDialog.askdirectory(**self.dir_opt)
        DirName = str(DirName).replace('/', '\\')

        DirArray = DirName.split('\\')
        DirName = DirArray[len(DirArray) - 1]
        print(DirName)

        self.MainWindow.destroy()
        LoadCaseGUI = MainPage.MainMenuGUI("", False, DirName, "Daniel Suryanata")  # Redacted path for privacy purpose

def main():
    TheGUI = MainMenuGUI()

# Call the main() function
main()