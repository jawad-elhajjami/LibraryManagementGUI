import wx
import sqlite3
from datetime import datetime


class BorrowView(wx.Panel):
    def __init__(self, parent):
        super(BorrowView, self).__init__(parent)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Form to borrow a book
        form_sizer = wx.GridBagSizer(5, 5)
        
        # choose book dropown
        choose_book_label = wx.StaticText(self, label="Choose Book:")
        self.choose_book = wx.ComboBox(self, style=wx.CB_READONLY)
        self.populate_books_dropdown()
        
        # Set event handler for book selection
        self.choose_book.Bind(wx.EVT_COMBOBOX, self.on_select_book)
        
        # choose member dropdown
        choose_member_label = wx.StaticText(self, label="Choose Member:")
        self.choose_member = wx.ComboBox(self, style=wx.CB_READONLY)
        self.populate_members_dropdown()
        
        # Set event handler for member selection
        self.choose_member.Bind(wx.EVT_COMBOBOX, self.on_select_member)
    
        borrow_button = wx.Button(self, label="Borrow Book")
        borrow_button.Bind(wx.EVT_BUTTON, self.on_borrow_book)
                
        # choose book dropown        
        form_sizer.Add(choose_book_label, pos=(0, 0), flag=wx.ALL, border=5)
        form_sizer.Add(self.choose_book, pos=(0, 1), flag=wx.EXPAND | wx.ALL, border=5)
        
        # choose members dropown        
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

    def populate_books_dropdown(self):
            conn = sqlite3.connect("database/library.db")
            cursor = conn.cursor()

            # Select all books to show in the dropdown
            cursor.execute(
                """
                SELECT id,title FROM Book
                """,
            )
            rows = cursor.fetchall()
            self.book_dict = {row[0]:row[1] for row in rows}
            self.choose_book.AppendItems(list(self.book_dict.values()))
            conn.close()

    def populate_members_dropdown(self):
        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        # Select all members to show in the dropdown
        cursor.execute(
            """
            SELECT id,name FROM Member
            """,
        )
        rows = cursor.fetchall()
        self.member_dict = {row[0]:row[1] for row in rows}
        self.choose_member.AppendItems(list(self.member_dict.values()))
        conn.close()
    
    def on_select_book(self, event):
        #Get selected value
        selected_book = self.choose_book.GetValue()
        
        # Find the corresponding key using the dictionary
        self.selected_book_id = next((key for key, value in self.book_dict.items() if value == selected_book), None)

        # Display the key-value pair
        # wx.MessageBox(f"Selected ID: {selected_id}\nSelected Title: {selected_book}", "Selection Info")
        
    def on_select_member(self, event):
        #Get selected value
        selected_member = self.choose_member.GetValue()
        
        # Find the corresponding key using the dictionary
        self.selected_member_id = next((key for key, value in self.member_dict.items() if value == selected_member), None)

        # Display the key-value pair
        # wx.MessageBox(f"Selected ID: {selected_id}\nSelected Name: {selected_member}", "Selection Info")
    
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
        cursor.execute(
            """
            SELECT id FROM Borrow WHERE book_id = ? AND return_date IS NULL
            """,
            (book_id,),
        )
        if cursor.fetchone():
            wx.MessageBox("The book is already borrowed.", "Error", wx.OK | wx.ICON_ERROR)
            conn.close()
            return

        cursor.execute(
            """
            INSERT INTO Borrow (member_id, book_id, borrow_date)
            VALUES (?, ?, ?)
            """,
            (member_id, book_id, borrow_date),
        )

        conn.commit()
        conn.close()

        wx.MessageBox("Book borrowed successfully!", "Success", wx.OK | wx.ICON_INFORMATION)

        self.load_borrow_records()
        self.clear_form()

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

        cursor.execute(
            """
            UPDATE Borrow SET return_date = ?
            WHERE id = ?
            """,
            (return_date, borrow_id),
        )
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
        self.choose_book.SetValue("")
        self.choose_member.SetValue("")
