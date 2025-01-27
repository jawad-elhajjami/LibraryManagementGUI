import wx
from views.main_window import MainWindow

class LibraryApp(wx.App):
    def OnInit(self):
        frame = MainWindow(None, title="Library Management System")
        frame.Show()
        return True

if __name__ == "__main__":
    app = LibraryApp()
    app.MainLoop()