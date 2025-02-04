# Library Management System

A simple Library Management System built using Python, wxPython for the GUI, and SQLite3 for the database. The system allows for managing books, book categories and members, along with tracking borrowing and returning of books.

## Features

- **Books Management:** Add, view, update, and delete books.
- **Members Management:** Add, view, update, and delete members.
- **Categories Management:** Add, view, update, and delete categories.
- **Borrowing System:** Track which members have borrowed books and when they return them.

### Views

- **main_window.py:** The main window that launches the application.
- **book_view.py:** A GUI for managing books in the system.
- **member_view.py:** A GUI for managing library members.
- **borrow_view.py:** A GUI for managing the borrowing and returning of books.
- **category_view.py:** A GUI for managing book categories, users can choose a unique color for each category

### Database

The database is stored as a `.db` file (SQLite3 format) and contains tables for books, members, categories, and borrowing records.

## Installation

1. Clone the repository:

``` git clone https://github.com/jawad-elhajjami/LibraryManagementGUI.git ```
``` cd LibraryManagementGUI ```

2. Install the required dependencies:

``` pip install -r requirements.txt ```

3. Initiate the database, by running the `init_db.py` file located in the `/database` directory
4. Launch the application:

``` python app.py ```

## Requirements

- Python 3.x
- wxPython
- SQLite3

You can install the required libraries using:

``` pip install wxPython sqlite3 ```

## License

This project is licensed under the MIT License

## Acknowledgments

- wxPython documentation for the GUI framework.
- SQLite3 for lightweight database handling.