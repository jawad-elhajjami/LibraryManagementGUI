import wx
import sqlite3
from datetime import datetime  # Import the datetime module
from wx.lib.pubsub import pub 


class MemberView(wx.Panel):
    def __init__(self, parent):
        super(MemberView, self).__init__(parent)

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Form to add new member
        form_sizer = wx.GridBagSizer(5, 5)

        name_label = wx.StaticText(self, label="Name:")
        self.name_input = wx.TextCtrl(self)

        email_label = wx.StaticText(self, label="Email:")
        self.email_input = wx.TextCtrl(self)

        phone_label = wx.StaticText(self, label="Phone:")
        self.phone_input = wx.TextCtrl(self)

        add_button = wx.Button(self, label="Add Member")
        add_button.Bind(wx.EVT_BUTTON, self.on_add_member)

        # update member button
        update_button = wx.Button(self, label="Update Member")
        update_button.Bind(wx.EVT_BUTTON, self.on_update_member)  
        
        form_sizer.Add(name_label, pos=(0, 0), flag=wx.ALL, border=5)
        form_sizer.Add(self.name_input, pos=(0, 1), flag=wx.EXPAND | wx.ALL, border=5)

        form_sizer.Add(email_label, pos=(1, 0), flag=wx.ALL, border=5)
        form_sizer.Add(self.email_input, pos=(1, 1), flag=wx.EXPAND | wx.ALL, border=5)

        form_sizer.Add(phone_label, pos=(2, 0), flag=wx.ALL, border=5)
        form_sizer.Add(self.phone_input, pos=(2, 1), flag=wx.EXPAND | wx.ALL, border=5)

        form_sizer.Add(add_button, pos=(3, 0), span=(1, 2), flag=wx.CENTER | wx.ALL, border=10)
        form_sizer.AddGrowableCol(1)

        form_sizer.Add(update_button, pos=(4, 2), flag=wx.CENTER | wx.ALL,  border=5)
              
        
        # Table to display members
        self.member_table = wx.ListCtrl(
            self, style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.member_table.InsertColumn(0, "ID", width=50)
        self.member_table.InsertColumn(1, "Name", width=150)
        self.member_table.InsertColumn(2, "Email", width=200)
        self.member_table.InsertColumn(3, "Phone", width=100)
        self.member_table.InsertColumn(4, "Membership date", width=100)

        # Bind double-click event
        self.member_table.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit_member)
        
        # Buttons to delete members
        delete_button = wx.Button(self, label="Delete Member")
        delete_button.Bind(wx.EVT_BUTTON, self.on_delete_member)

        # Main layout
        sizer.Add(form_sizer, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(self.member_table, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(delete_button, 0, wx.CENTER | wx.ALL, 10)

        self.SetSizer(sizer)

        # Track selected Member ID for updates
        self.selected_member_id = None

        # Load members into the table
        self.load_members()

    def on_add_member(self, event):
        """Add a new member to the database."""
        name = self.name_input.GetValue()
        email = self.email_input.GetValue()
        phone = self.phone_input.GetValue()

        if not name or not email or not phone:
            wx.MessageBox("All fields are required.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Get the current date as the membership_date
        membership_date = datetime.now().strftime("%Y-%m-%d")  # Format as YYYY-MM-DD
        
        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO Member (name, email, phone, membership_date)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, phone, membership_date),
        )

        conn.commit()
        conn.close()

        wx.MessageBox("Member added successfully!", "Success", wx.OK | wx.ICON_INFORMATION)

        self.load_members()
        pub.sendMessage("update_members")
        self.clear_form()

    def load_members(self):
        """Load members from the database into the table."""
        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        self.member_table.DeleteAllItems()
        for row in cursor.execute("SELECT * FROM Member"):
            self.member_table.Append([str(col) for col in row])

        conn.close()

    def on_delete_member(self, event):
        """Delete the selected member from the database."""
        selected_item = self.member_table.GetFirstSelected()

        if selected_item == -1:
            wx.MessageBox("Please select a member to delete.", "Error", wx.OK | wx.ICON_ERROR)
            return

        member_id = self.member_table.GetItemText(selected_item)

        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Member WHERE id = ?", (member_id,))
        cursor.execute("DELETE FROM Borrow WHERE member_id = ?", (member_id,))
        conn.commit()
        conn.close()

        wx.MessageBox("Member deleted successfully!", "Success", wx.OK | wx.ICON_INFORMATION)
        pub.sendMessage("update_members")
        pub.sendMessage("update_borrow_records")  # Notify BorrowView to refresh
        self.load_members()

    def on_edit_member(self, event):
        """Load selected member details into the form for editing."""
        selected_item = event.GetIndex()

        self.selected_member_id = self.member_table.GetItemText(selected_item)  # Member ID
        name = self.member_table.GetItem(selected_item, 1).GetText()
        email = self.member_table.GetItem(selected_item, 2).GetText()
        phone = self.member_table.GetItem(selected_item, 3).GetText()
        
        # Populate the form with selected member's details
        self.name_input.SetValue(name)
        self.email_input.SetValue(email)
        self.phone_input.SetValue(phone)
    
    def on_update_member(self, event):
        """Update the selected member in the database."""
        if not self.selected_member_id:
            wx.MessageBox("Please select a member to update by double-clicking it.", "Error", wx.OK | wx.ICON_ERROR)
            return

        name = self.name_input.GetValue()
        email = self.email_input.GetValue()
        phone = self.phone_input.GetValue()

        if not name or not email or not phone:
            wx.MessageBox("All fields are required.", "Error", wx.OK | wx.ICON_ERROR)
            return

        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE Member SET name = ?, email = ?, phone = ?
            WHERE id = ?
            """,
            (name, email, phone, self.selected_member_id),
        )
        conn.commit()
        conn.close()

        wx.MessageBox("Member updated successfully!", "Success", wx.OK | wx.ICON_INFORMATION)
        self.load_members()
        pub.sendMessage("update_members")
        self.clear_form()
    
    def clear_form(self):
        """Clear the input form."""
        self.name_input.SetValue("")
        self.email_input.SetValue("")
        self.phone_input.SetValue("")
