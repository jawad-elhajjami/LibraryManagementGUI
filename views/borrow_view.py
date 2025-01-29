import wx
import sqlite3
from datetime import datetime
from wx.lib.pubsub import pub 


class BorrowView(wx.Panel):
    def __init__(self, parent):
        super(BorrowView, self).__init__(parent)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Form to borrow a book
        form_sizer = wx.GridBagSizer(5, 5)
        
        # Choose book dropdown
        choose_book_label = wx.StaticText(self, label="Choose Book:")
        self.choose_book = wx.ComboBox(self, style=wx.CB_READONLY)
        
        # Choose member dropdown
        choose_member_label = wx.StaticText(self, label="Choose Member:")
        self.choose_member = wx.ComboBox(self, style=wx.CB_READONLY)
        
        borrow_button = wx.Button(self, label="Borrow Book")
        borrow_button.Bind(wx.EVT_BUTTON, self.on_borrow_book)
                
        # Add to layout        
        form_sizer.Add(choose_book_label, pos=(0, 0), flag=wx.ALL, border=5)
        form_sizer.Add(self.choose_book, pos=(0, 1), flag=wx.EXPAND | wx.ALL, border=5)
        
        form_sizer.Add(choose_member_label, pos=(1,0), flag=wx.ALL, border=5)
        form_sizer.Add(self.choose_member, pos=(1,1), flag=wx.EXPAND | wx.ALL, border=5)
        
        form_sizer.Add(borrow_button, pos=(2, 0), span=(2, 1), flag=wx.CENTER | wx.ALL, border=10)
        form_sizer.AddGrowableCol(1)

        # Table to display borrow records
        self.borrow_table = wx.ListCtrl(
            self, style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.borrow_table.InsertColumn(0, "Borrow ID", width=70)
        self.borrow_table.InsertColumn(1, "Member ID", width=100)
        self.borrow_table.InsertColumn(2, "Book ID", width=100)
        self.borrow_table.InsertColumn(3, "Borrow Date", width=150)
        self.borrow_table.InsertColumn(4, "Return Date", width=150)

        # Buttons for returning books
        return_button = wx.Button(self, label="Return Book")
        return_button.Bind(wx.EVT_BUTTON, self.on_return_book)

        # Main layout
        sizer.Add(form_sizer, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(self.borrow_table, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(return_button, 0, wx.CENTER | wx.ALL, 10)

        self.SetSizer(sizer)
        
        self.selected_book_id = None
        self.selected_member_id = None
        
        # Load borrow records into the table
        self.load_borrow_records()
        
        # Populate dropdowns
        self.populate_books_dropdown()
        self.populate_members_dropdown()

        # Subscribe to updates
        pub.subscribe(self.populate_books_dropdown, "update_books")
        pub.subscribe(self.populate_members_dropdown, "update_members")
        
        # Auto-refresh on show
        self.Bind(wx.EVT_SHOW, self.on_show)
        self.choose_book.Bind(wx.EVT_COMBOBOX, self.on_select_book)
        self.choose_member.Bind(wx.EVT_COMBOBOX, self.on_select_member)

    def on_show(self, event):
        """Refresh data when the panel is shown."""
        if event.IsShown():
            wx.CallAfter(self.populate_books_dropdown)
            wx.CallAfter(self.populate_members_dropdown)
            wx.CallAfter(self.load_borrow_records)
    
    def on_select_book(self, event):
        """Update selected book ID when a book is chosen."""
        selected_title = self.choose_book.GetValue()
        for book_id, title in self.book_dict.items():
            if title == selected_title:
                self.selected_book_id = book_id
                break

    def on_select_member(self, event):
        """Update selected member ID when a member is chosen."""
        selected_name = self.choose_member.GetValue()
        for member_id, name in self.member_dict.items():
            if name == selected_name:
                self.selected_member_id = member_id
                break

    
    def populate_books_dropdown(self):
        """Load books into the dropdown."""
        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        self.choose_book.Clear()  # Clear previous items
        self.book_dict = {}

        cursor.execute("SELECT id, title FROM Book")
        rows = cursor.fetchall()
        
        for row in rows:
            self.book_dict[row[0]] = row[1]

        self.choose_book.AppendItems(list(self.book_dict.values()))
        conn.close()

    def populate_members_dropdown(self):
        """Load members into the dropdown."""
        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        self.choose_member.Clear()  # Clear previous items
        self.member_dict = {}

        cursor.execute("SELECT id, name FROM Member")
        rows = cursor.fetchall()

        for row in rows:
            self.member_dict[row[0]] = row[1]

        self.choose_member.AppendItems(list(self.member_dict.values()))
        conn.close()
    
    def on_borrow_book(self, event):
        """Borrow a book."""
        member_id = self.selected_member_id
        book_id = self.selected_book_id
        borrow_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not member_id or not book_id:
            wx.MessageBox("All fields are required.", "Error", wx.OK | wx.ICON_ERROR)
            return

        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        # Check if the book is already borrowed
        cursor.execute("SELECT id FROM Borrow WHERE book_id = ? AND return_date IS NULL", (book_id,))
        if cursor.fetchone():
            wx.MessageBox("The book is already borrowed.", "Error", wx.OK | wx.ICON_ERROR)
            conn.close()
            return

        cursor.execute("INSERT INTO Borrow (member_id, book_id, borrow_date) VALUES (?, ?, ?)", 
                       (member_id, book_id, borrow_date))
        conn.commit()
        conn.close()

        wx.MessageBox("Book borrowed successfully!", "Success", wx.OK | wx.ICON_INFORMATION)

        self.load_borrow_records()
        self.clear_form()

        # Notify other views to update
        pub.sendMessage("update_books")

    def on_return_book(self, event):
        """Mark a book as returned."""
        selected_item = self.borrow_table.GetFirstSelected()

        if selected_item == -1:
            wx.MessageBox("Please select a record to mark as returned.", "Error", wx.OK | wx.ICON_ERROR)
            return

        borrow_id = self.borrow_table.GetItemText(selected_item)
        return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE Borrow SET return_date = ? WHERE id = ?", (return_date, borrow_id))
        conn.commit()
        conn.close()

        wx.MessageBox("Book marked as returned!", "Success", wx.OK | wx.ICON_INFORMATION)

        self.load_borrow_records()

    def load_borrow_records(self):
        """Load borrow records from the database into the table."""
        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        self.borrow_table.DeleteAllItems()
        for row in cursor.execute("SELECT * FROM Borrow"):
            self.borrow_table.Append([str(col) for col in row])

        conn.close()

    def clear_form(self):
        """Clear the input form."""
        self.choose_book.SetSelection(wx.NOT_FOUND)
        self.choose_member.SetSelection(wx.NOT_FOUND)
        self.selected_book_id = None
        self.selected_member_id = None
