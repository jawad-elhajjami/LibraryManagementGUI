# LibraryManagementGUI
# Library Management System

A simple Library Management System built using Python, wxPython for the GUI, and SQLite3 for the database. The system allows for managing books, members, and staff, along with tracking borrowing and returning of books.

## Features

- **Books Management:** Add, view, update, and delete books.
- **Members Management:** Add, view, update, and delete members.
- **Borrowing System:** Track which members have borrowed books and when they return them.
- **Staff Management:** Manage staff details for library operations.

### Models

- **book.py:** Contains the Book class with attributes like title, author, ISBN, etc.
- **member.py:** Contains the Member class with attributes like name, email, phone, etc.
- **borrow.py:** Handles the borrowing and returning of books, including due dates.
- **staff.py:** Manages the staff members of the library.

### Views

- **main_window.py:** The main window that launches the application.
- **book_view.py:** A GUI for managing books in the system.
- **member_view.py:** A GUI for managing library members.
- **borrow_view.py:** A GUI for managing the borrowing and returning of books.

### Database

The database is stored as a `.db` file (SQLite3 format) and contains tables for books, members, staff, and borrowing records.

## Installation

1. Clone the repository:

git clone https://github.com/your-username/LibraryManagement.git cd LibraryManagement

2. Install the required dependencies:

pip install -r requirements.txt

3. Launch the application:

python app.py

## Requirements

- Python 3.x
- wxPython
- SQLite3

You can install the required libraries using:

pip install wxPython sqlite3

markdown
Copier
Modifier

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- wxPython documentation for the GUI framework.
- SQLite3 for lightweight database handling.