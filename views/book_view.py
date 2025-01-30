import wx
import sqlite3
from wx.lib.pubsub import pub 


class BookView(wx.Panel):
    def __init__(self, parent):
        super(BookView, self).__init__(parent)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Form to add new book
        form_sizer = wx.GridBagSizer(5, 5)

        title_label = wx.StaticText(self, label="Title:")
        self.title_input = wx.TextCtrl(self)

        author_label = wx.StaticText(self, label="Author:")
        self.author_input = wx.TextCtrl(self)

        genre_label = wx.StaticText(self, label="Genre:")
        self.genre_input = wx.TextCtrl(self)

        availability_label = wx.StaticText(self, label="Availability:")
        self.availability_input = wx.ComboBox(
            self, choices=["Available", "Not Available"], style=wx.CB_READONLY
        )

        add_button = wx.Button(self, label="Add Book")
        add_button.Bind(wx.EVT_BUTTON, self.on_add_book)

        update_button = wx.Button(self, label="Update Book")
        update_button.Bind(wx.EVT_BUTTON, self.on_update_book)
        
        form_sizer.Add(title_label, pos=(0, 0), flag=wx.ALL, border=5)
        form_sizer.Add(self.title_input, pos=(0, 1), flag=wx.EXPAND | wx.ALL, border=5)

        form_sizer.Add(author_label, pos=(1, 0), flag=wx.ALL, border=5)
        form_sizer.Add(self.author_input, pos=(1, 1), flag=wx.EXPAND | wx.ALL, border=5)

        form_sizer.Add(genre_label, pos=(2, 0), flag=wx.ALL, border=5)
        form_sizer.Add(self.genre_input, pos=(2, 1), flag=wx.EXPAND | wx.ALL, border=5)

        form_sizer.Add(availability_label, pos=(3, 0), flag=wx.ALL, border=5)
        form_sizer.Add(self.availability_input, pos=(3, 1), flag=wx.EXPAND | wx.ALL, border=5)

        form_sizer.Add(add_button, pos=(4, 0), span=(1, 2), flag=wx.CENTER | wx.ALL, border=10)
        form_sizer.AddGrowableCol(1)

        form_sizer.Add(update_button, pos=(4, 2), flag=wx.CENTER | wx.ALL,  border=5)
        
        # Table to display books
        self.book_table = wx.ListCtrl(
            self, style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.book_table.InsertColumn(0, "ID", width=50)
        self.book_table.InsertColumn(1, "Title", width=150)
        self.book_table.InsertColumn(2, "Author", width=150)
        self.book_table.InsertColumn(3, "Genre", width=100)
        self.book_table.InsertColumn(4, "Availability", width=100)
        
        # Buttons to update or delete books

        # Bind double-click event
        self.book_table.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit_book)

        delete_button = wx.Button(self, label="Delete Book")
        delete_button.Bind(wx.EVT_BUTTON, self.on_delete_book)

        # Main layout
        sizer.Add(form_sizer, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(self.book_table, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(delete_button, 0, wx.CENTER | wx.ALL, 10)

        self.SetSizer(sizer)

        # Track selected book ID for updates
        self.selected_book_id = None
        
        # Load books into the table
        self.load_books()

    def on_edit_book(self, event):
        """Load selected book details into the form for editing."""
        selected_item = event.GetIndex()

        self.selected_book_id = self.book_table.GetItemText(selected_item)  # Book ID
        title = self.book_table.GetItem(selected_item, 1).GetText()
        author = self.book_table.GetItem(selected_item, 2).GetText()
        genre = self.book_table.GetItem(selected_item, 3).GetText()
        availability = self.book_table.GetItem(selected_item, 4).GetText()
        
        # Populate the form with selected book's details
        self.title_input.SetValue(title)
        self.author_input.SetValue(author)
        self.genre_input.SetValue(genre)
        self.availability_input.SetValue(availability)
    
    def on_update_book(self, event):
        """Update the selected book in the database."""
        if not self.selected_book_id:
            wx.MessageBox("Please select a book to update by double-clicking it.", "Error", wx.OK | wx.ICON_ERROR)
            return

        title = self.title_input.GetValue()
        author = self.author_input.GetValue()
        genre = self.genre_input.GetValue()
        availability = self.availability_input.GetValue()

        if not title or not author or not genre or not availability:
            wx.MessageBox("All fields are required.", "Error", wx.OK | wx.ICON_ERROR)
            return

        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE Book SET title = ?, author = ?, genre = ?, availability = ?
            WHERE id = ?
            """,
            (title, author, genre, availability, self.selected_book_id),
        )
        conn.commit()
        conn.close()

        wx.MessageBox("Book updated successfully!", "Success", wx.OK | wx.ICON_INFORMATION)
        self.load_books()
        pub.sendMessage("update_books")
        self.clear_form()
     
    def on_add_book(self, event):
        """Add a new book to the database."""
        title = self.title_input.GetValue()
        author = self.author_input.GetValue()
        genre = self.genre_input.GetValue()
        availability = self.availability_input.GetValue()

        if not title or not author or not genre or not availability:
            wx.MessageBox("All fields are required.", "Error", wx.OK | wx.ICON_ERROR)
            return

        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO Book (title, author, genre, availability)
            VALUES (?, ?, ?, ?)
            """,
            (title, author, genre, availability),
        )

        conn.commit()
        conn.close()

        wx.MessageBox("Book added successfully!", "Success", wx.OK | wx.ICON_INFORMATION)

        self.load_books()
        pub.sendMessage("update_books")
        self.clear_form()

    def load_books(self):
        """Load books from the database into the table."""
        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        self.book_table.DeleteAllItems()
        for row in cursor.execute("SELECT * FROM Book"):
            self.book_table.Append([str(col) for col in row])

        conn.close()

    def on_delete_book(self, event):
        """Delete the selected book from the database."""
        selected_item = self.book_table.GetFirstSelected()

        if selected_item == -1:
            wx.MessageBox("Please select a book to delete.", "Error", wx.OK | wx.ICON_ERROR)
            return

        book_id = self.book_table.GetItemText(selected_item)

        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM Borrow WHERE book_id = ?", (book_id,))  
        cursor.execute("DELETE FROM Book WHERE id = ?", (book_id,))  

        conn.commit()
        conn.close()

        wx.MessageBox("Book deleted successfully!", "Success", wx.OK | wx.ICON_INFORMATION)
        pub.sendMessage("update_books")
        pub.sendMessage("update_borrow_records")  # Notify BorrowView to refresh
        self.load_books()

    def clear_form(self):
        """Clear the input form."""
        self.title_input.SetValue("")
        self.author_input.SetValue("")
        self.genre_input.SetValue("")
        self.availability_input.SetValue("")
