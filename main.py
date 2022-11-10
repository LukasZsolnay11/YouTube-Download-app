from pytube import YouTube
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import re
import threading

class Application:

    def __init__(self, root):
        self.root = root
        self.root.grid_rowconfigure(0, weight=2)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.config(bg="red")

        label_top = Label(self.root, text="YouTube Download Manager", bg="black", fg="white", font=("Ariel", 70))
        label_top.grid(pady=(0, 10))

        label_link = Label(self.root, text="Paste link", font=("Ariel", 50))
        label_link.grid(pady=(0, 20))

        self.entry = StringVar()

        self.entry = Entry(self.root, width=70, textvariable=self.entry, font=("Ariel", 25))
        self.entry.grid(pady=(0, 15), ipady=2)

        self.invalid_entry = Label(self.root,text="", font=("Ariel", 20))
        self.invalid_entry.grid(pady=(0, 15))

        self.save_label = Label(self.root, text="Please choose your directory", bg="black", fg="white", font=("Ariel", 30))
        self.save_label.grid()

        self.directory_button = Button(self.root, text="Directory", font=("Ariel", 15,), command=self.openDirectory)
        self.directory_button.grid(pady=(10, 3))

        self.fileLocation = Label(self.root, text="", font=("Ariel", 25))
        self.fileLocation.grid()

        self.choose_label = Label(self.root, text="Choose download type", font=("Ariel", 25))
        self.choose_label.grid()

        self.download = [("Audio", 1), ("Video", 2)]

        self.download_choices = StringVar()
        self.download_choices.set(1)

        for text, mode in self.download:
            self.youtubeChoices = Radiobutton(self.root, text=text, variable=self.download_choices, value=mode)
            self.youtubeChoices.grid()

        self.download_button = Button(self.root, text="Download", width=10, command=self.check_link, font=("Ariel", 20))
        self.download_button.grid(pady=(30,5))

    def check_link(self):

        self.match_link = re.match("^https://www.youtube.com/.", self.entry.get())
        if (not self.match_link):
            self.invalid_entry.config(text="Invalid link")
        elif (not self.openDirectory):
            self.fileLocation.config(text="Please Choose a Directory")
        elif (self.match_link and self.openDirectory):
            self.downloadWindow()

    def downloadWindow(self):
        self.newWindow = Toplevel(self.root)
        self.root.withdraw()
        self.newWindow.state("zoomed")
        self.newWindow.grid_rowconfigure(0, weight=0)
        self.newWindow.grid_columnconfigure(0, weight=1)

        self.app = SecondApp(self.newWindow, self.entry.get(), self.folder_name, self.download_choices.get())


    def openDirectory(self):
        self.folder_name=filedialog.askdirectory()

        if(len(self.folder_name)>0):
            self.fileLocation.config(text=self.folder_name)
            return True
        else:
            self.fileLocation.config(text="Please Choose a Directory")


class SecondApp:

    def __init__(self, downloadWindow, youtubelink, FolderName, Choices):
        self.downloadWindow = downloadWindow
        self.youtubelink = youtubelink
        self.FolderName = FolderName
        self.Choices = Choices

        self.yt = YouTube(self.youtubelink)

        if(Choices == "1"):
            self.video_type = self.yt.streams.filter(only_audio=True)
            self.MaxFileSize = self.video_type.filesize

        if(Choices == "2"):
            self.video_type = self.yt.streams.first()
            self.MaxFileSize = self.video_type.filesize

        self.loadingLabel = Label(self.downloadWindow, text="Downloading in progress..")
        self.loadingLabel.grid(pady=(100, 0))

        self.loadingPercent = Label(self.downloadWindow, text="0", fg="green")
        self.loadingPercent.grid(pady=(50, 0))

        self.progressbar = ttk.Progressbar(self.downloadWindow, length=500, orient="horizontal", mode="indeterminate")
        self.progressbar.grid(pady=(50, 0))
        self.progressbar.start()

        threading.Thread(target=self.yt.register_on_progress_callback(self.show_progress)).start()

        threading.Thread(target=self.downloadFile).start()

    def downloadFile(self):
        if(self.Choices== "1"):
            self.yt.streams.filter(only_audio=True).first().download(self.FolderName)

        if(self.Choices== "2"):
            self.yt.streams.first().download(self.FolderName)

    def show_progress(self, streams=None, Chunks=None, filehandle=None, bytes_remaining=None):
        self.percentCount = ("%0.2f"(100-(100*(bytes_remaining/self.MaxFileSize))))

        if(self.percentCount< 100):
            self.loadingLabel.config(text=self.percentCount)
        else:
            self.progressbar.stop()
            self.loadingLabel.grid_forget()
            self.progressbar.grid_forget()

            self.downloadFinished = Label(self.downloadWindow, text="Download finished")
            self.downloadFinished.grid(pady=(150, 0))

            self.downloadedFileName = Label(self.downloadWindow, text=self.yt.title)
            self.downloadedFileName.grid(pady=(50, 0))

            MB = float("%0.2f" % (self.MaxFileSize/100000))

            self.downloadFileSize = Label(self.downloadWindow, str(MB))
            self.downloadFileSize.grid(pady=(50, 0))


if __name__ == "__main__":

    window = Tk()
    window.title("Download Manager")
    window.state("zoomed")

    app = Application(window)

    mainloop()

