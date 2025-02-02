import wx
import sqlite3
from wx.lib.pubsub import pub 

class CategoryView(wx.Panel):
    def __init__(self, parent):
        super(CategoryView, self).__init__(parent)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Form to add new category
        form_sizer = wx.GridBagSizer(5, 5)

        name_label = wx.StaticText(self, label="Category name:")
        self.name_input = wx.TextCtrl(self)

        # Create a color picker control
        self.color_picker = wx.ColourPickerCtrl(self)
        
        
        add_button = wx.Button(self, label="Add Category")
        add_button.Bind(wx.EVT_BUTTON, self.on_add_category)

        # update member button
        update_button = wx.Button(self, label="Update Category")
        update_button.Bind(wx.EVT_BUTTON, self.on_update_category)  
        
        form_sizer.Add(name_label, pos=(0, 0), flag=wx.ALL, border=5)
        form_sizer.Add(self.name_input, pos=(0, 1), flag=wx.EXPAND | wx.ALL, border=5)
        
        form_sizer.Add(self.color_picker, pos=(1, 0), flag=wx.EXPAND | wx.ALL, border=5)

        form_sizer.Add(add_button, pos=(3, 0), span=(1, 2), flag=wx.CENTER | wx.ALL, border=10)
        form_sizer.AddGrowableCol(1)

        form_sizer.Add(update_button, pos=(4, 2), flag=wx.CENTER | wx.ALL,  border=5)
              
        
        # Table to display members
        self.category_table = wx.ListCtrl(
            self, style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.category_table.InsertColumn(0, "ID", width=50)
        self.category_table.InsertColumn(1, "Name", width=150)
        self.category_table.InsertColumn(2, "Color", width=200)
        self.category_table.InsertColumn(3, "Number of Books", width=100)

        # Bind double-click event
        self.category_table.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit_category)
        
        # Buttons to delete categories
        delete_button = wx.Button(self, label="Delete Category")
        delete_button.Bind(wx.EVT_BUTTON, self.on_delete_category)

        # Main layout
        sizer.Add(form_sizer, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(self.category_table, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(delete_button, 0, wx.CENTER | wx.ALL, 10)

        self.SetSizer(sizer)

        # Track selected Category ID for updates
        self.selected_category_id = None
        self.selected_color = None

        # Load categories into the table
        self.load_categories()

        
    def load_categories(self):
        """Load categories from the database into the table, including book counts."""
        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        self.category_table.DeleteAllItems()

        # Query to get category name and book count
        query = """
            SELECT BookCategory.id, BookCategory.name, BookCategory.color, 
                COUNT(Book.id) AS book_count
            FROM BookCategory
            LEFT JOIN Book ON Book.category_id = BookCategory.id
            GROUP BY BookCategory.id
        """

        for row in cursor.execute(query):
            self.category_table.Append([str(row[0]), row[1], row[2], str(row[3])])

        conn.close()

    
    def on_add_category(self, event):
        """Add a new category to the database."""
        name = self.name_input.GetValue()
        color = self.color_picker.GetColour()
        hexCode = color.GetAsString(wx.C2S_HTML_SYNTAX)

        if not name or not hexCode:
            wx.MessageBox("All fields are required.", "Error", wx.OK | wx.ICON_ERROR)
            return

        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO BookCategory (name, color)
            VALUES (?, ?)
            """,
            (name, hexCode)
        )

        conn.commit()
        conn.close()

        wx.MessageBox("Category added successfully!", "Success", wx.OK | wx.ICON_INFORMATION)

        self.load_categories()
        # pub.sendMessage("update_books")
        pub.sendMessage("update_categories")
        self.clear_form()
        
    def on_update_category(self, event):
        """Update the selected category in the database."""
        if not self.selected_category_id:
            wx.MessageBox("Please select a category to update by double-clicking it.", "Error", wx.OK | wx.ICON_ERROR)
            return

        name = self.name_input.GetValue()
        color = self.color_picker.GetColour()
        hexCode = color.GetAsString(wx.C2S_HTML_SYNTAX)

        if not name or not hexCode:
            wx.MessageBox("All fields are required.", "Error", wx.OK | wx.ICON_ERROR)
            return

        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE BookCategory SET name = ?, color = ? WHERE id = ?
            """,
            (name, hexCode, self.selected_category_id),
        )
        conn.commit()
        conn.close()

        wx.MessageBox("Category updated successfully!", "Success", wx.OK | wx.ICON_INFORMATION)
        self.load_categories()
        pub.sendMessage("update_books")
        self.clear_form()
        
    def on_edit_category(self, event):
        """Load selected category details into the form for editing."""
        selected_item = event.GetIndex()

        self.selected_category_id = self.category_table.GetItemText(selected_item)  # Category ID
        name = self.category_table.GetItem(selected_item, 1).GetText()
        color = self.category_table.GetItem(selected_item, 2).GetText()
        
        # Populate the form with selected book's details
        self.name_input.SetValue(name)
        self.color_picker.SetColour(color);

    def on_delete_category(self, event):
        """Delete the selected record from the database."""
        selected_item = self.category_table.GetFirstSelected()

        if selected_item == -1:
            wx.MessageBox("Please select a record to delete.", "Error", wx.OK | wx.ICON_ERROR)
            return

        record_id = self.category_table.GetItemText(selected_item)

        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()
        
        # First, delete all books associated with the category
        cursor.execute("DELETE FROM Book WHERE category_id = ?", (record_id,))
        
        cursor.execute("DELETE FROM BookCategory WHERE id = ?", (record_id,))  

        conn.commit()
        conn.close()
        wx.MessageBox("Category deleted successfully!", "Success", wx.OK | wx.ICON_INFORMATION)
        self.load_categories()
        pub.sendMessage("update_books")
        
    def clear_form(self):
        """Clear the input form."""
        self.name_input.SetValue("")
        self.color_picker.SetColour("")
