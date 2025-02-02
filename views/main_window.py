import wx
from views.book_view import BookView
from views.member_view import MemberView
from views.borrow_view import BorrowView
from views.category_view import CategoryView

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        super(MainWindow, self).__init__(parent, title=title, size=(800, 600))

        notebook = wx.Notebook(self)

        # Add tabs
        notebook.AddPage(BookView(notebook), "Books")
        notebook.AddPage(MemberView(notebook), "Members")
        notebook.AddPage(BorrowView(notebook), "Borrow/Return")
        notebook.AddPage(CategoryView(notebook), "Book Categories")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.Centre()