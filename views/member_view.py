import wx
import sqlite3


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

        form_sizer.Add(name_label, pos=(0, 0), flag=wx.ALL, border=5)
        form_sizer.Add(self.name_input, pos=(0, 1), flag=wx.EXPAND | wx.ALL, border=5)

        form_sizer.Add(email_label, pos=(1, 0), flag=wx.ALL, border=5)
        form_sizer.Add(self.email_input, pos=(1, 1), flag=wx.EXPAND | wx.ALL, border=5)

        form_sizer.Add(phone_label, pos=(2, 0), flag=wx.ALL, border=5)
        form_sizer.Add(self.phone_input, pos=(2, 1), flag=wx.EXPAND | wx.ALL, border=5)

        form_sizer.Add(add_button, pos=(3, 0), span=(1, 2), flag=wx.CENTER | wx.ALL, border=10)
        form_sizer.AddGrowableCol(1)

        # Table to display members
        self.member_table = wx.ListCtrl(
            self, style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.member_table.InsertColumn(0, "ID", width=50)
        self.member_table.InsertColumn(1, "Name", width=150)
        self.member_table.InsertColumn(2, "Email", width=200)
        self.member_table.InsertColumn(3, "Phone", width=100)

        # Buttons to delete members
        delete_button = wx.Button(self, label="Delete Member")
        delete_button.Bind(wx.EVT_BUTTON, self.on_delete_member)

        # Main layout
        sizer.Add(form_sizer, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(self.member_table, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(delete_button, 0, wx.CENTER | wx.ALL, 10)

        self.SetSizer(sizer)

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

        conn = sqlite3.connect("database/library.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO Member (name, email, phone)
            VALUES (?, ?, ?)
            """,
            (name, email, phone),
        )

        conn.commit()
        conn.close()

        wx.MessageBox("Member added successfully!", "Success", wx.OK | wx.ICON_INFORMATION)

        self.load_members()
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
        conn.commit()
        conn.close()

        wx.MessageBox("Member deleted successfully!", "Success", wx.OK | wx.ICON_INFORMATION)
        self.load_members()

    def clear_form(self):
        """Clear the input form."""
        self.name_input.SetValue("")
        self.email_input.SetValue("")
        self.phone_input.SetValue("")
