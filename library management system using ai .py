import tkinter as tk
from tkinter import messagebox, Toplevel
from tkinter.ttk import Treeview
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta

# -------------------------------
# Initialize Data
# -------------------------------
books = pd.DataFrame([
    {"id": 1, "title": "Introduction to AI", "author": "John Doe", "genre": "AI", "availability": True},
    {"id": 2, "title": "Data Science Basics", "author": "Jane Smith", "genre": "Data Science", "availability": True},
    {"id": 3, "title": "Deep Learning Insights", "author": "Geoff Hinton", "genre": "Deep Learning", "availability": True},
    {"id": 4, "title": "Machine Learning Advanced", "author": "Andrew Ng", "genre": "Machine Learning", "availability": True},
    {"id": 5, "title": "Neural Networks Uncovered", "author": "Ian Goodfellow", "genre": "Deep Learning", "availability": True},
])

users = pd.DataFrame([
    {"id": 1, "name": "Alice", "password": "alice123", "borrowed_books": []},
    {"id": 2, "name": "Bob", "password": "bob123", "borrowed_books": []},
    {"id": 3, "name": "Charlie", "password": "charlie123", "borrowed_books": []},
])

logged_in_user = None

# -------------------------------
# Functions
# -------------------------------
def authenticate_user(username, password):
    """Authenticate user credentials."""
    global logged_in_user
    user = users[(users['name'] == username) & (users['password'] == password)]
    if not user.empty:
        logged_in_user = user.iloc[0]
        messagebox.showinfo("Login Successful", f"Welcome, {logged_in_user['name']}!")
        open_user_dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def recommend_books(query):
    """AI-based book recommendation using TF-IDF and Cosine Similarity."""
    corpus = books['title'] + " " + books['genre']
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    books['similarity'] = similarities
    recommendations = books[books['availability']].sort_values(by='similarity', ascending=False).head(3)
    return recommendations[['id', 'title', 'author', 'genre']]

def borrow_book(book_id):
    """Borrow a selected book."""
    if logged_in_user is None:
        messagebox.showerror("Error", "Please log in first.")
        return
    book = books.loc[books['id'] == book_id]
    if book.empty:
        messagebox.showerror("Error", "Invalid book ID.")
        return
    if not book.iloc[0]['availability']:
        messagebox.showerror("Error", "Book is not available.")
        return

    borrowed_books = logged_in_user['borrowed_books']
    borrowed_books.append({"book_id": book_id, "due_date": datetime.now() + timedelta(days=14)})
    users.loc[users['id'] == logged_in_user['id'], 'borrowed_books'] = [borrowed_books]
    books.loc[books['id'] == book_id, 'availability'] = False
    messagebox.showinfo("Success", f"Book '{book.iloc[0]['title']}' successfully borrowed.")

def view_borrowed_books():
    """Display borrowed books for the logged-in user."""
    if logged_in_user is None:
        messagebox.showerror("Error", "Please log in first.")
        return
    borrowed_books = logged_in_user['borrowed_books']
    if not borrowed_books:
        messagebox.showinfo("Borrowed Books", "No books borrowed.")
        return

    result_window = Toplevel()
    result_window.title(f"Borrowed Books - {logged_in_user['name']}")
    tree = Treeview(result_window, columns=("ID", "Title", "Due Date"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Title", text="Title")
    tree.heading("Due Date", text="Due Date")
    
    for book in borrowed_books:
        book_details = books.loc[books['id'] == book['book_id']].iloc[0]
        due_date_str = book['due_date'].strftime("%Y-%m-%d")
        tree.insert("", tk.END, values=(book_details['id'], book_details['title'], due_date_str))
    tree.pack(fill="both", expand=True)

def add_new_book(title, author, genre):
    """Add a new book to the inventory."""
    new_id = books['id'].max() + 1 if not books.empty else 1
    books.loc[len(books)] = {"id": new_id, "title": title, "author": author, "genre": genre, "availability": True}
    messagebox.showinfo("Success", f"Book '{title}' added successfully!")

def view_stock_status():
    """View the current stock of all books."""
    stock_window = Toplevel()
    stock_window.title("Stock Status")
    tree = Treeview(stock_window, columns=("ID", "Title", "Author", "Genre", "Availability"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Title", text="Title")
    tree.heading("Author", text="Author")
    tree.heading("Genre", text="Genre")
    tree.heading("Availability", text="Availability")
    
    for _, row in books.iterrows():
        tree.insert("", tk.END, values=(row['id'], row['title'], row['author'], row['genre'], "Yes" if row['availability'] else "No"))
    tree.pack(fill="both", expand=True)

# -------------------------------
# Windows
# -------------------------------
def open_login_window():
    """Create the login window."""
    def login_action():
        username = entry_username.get()
        password = entry_password.get()
        authenticate_user(username, password)

    login_window = tk.Tk()
    login_window.title("Library Login")
    tk.Label(login_window, text="Username").grid(row=0, column=0, pady=10, padx=10)
    entry_username = tk.Entry(login_window)
    entry_username.grid(row=0, column=1, pady=10, padx=10)
    tk.Label(login_window, text="Password").grid(row=1, column=0, pady=10, padx=10)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.grid(row=1, column=1, pady=10, padx=10)
    tk.Button(login_window, text="Login", command=login_action).grid(row=2, column=0, columnspan=2, pady=20)
    login_window.mainloop()

def open_user_dashboard():
    """Create the user dashboard."""
    dashboard_window = Toplevel()
    dashboard_window.title("User Dashboard")
    tk.Button(dashboard_window, text="Borrow Book", command=open_recommendation_window).pack(pady=10)
    tk.Button(dashboard_window, text="View Borrowed Books", command=view_borrowed_books).pack(pady=10)

def open_recommendation_window():
    """Create the book recommendation window."""
    def get_recommendations():
        query = entry_query.get()
        recommendations = recommend_books(query)
        if recommendations.empty:
            messagebox.showinfo("Recommendations", "No recommendations found.")
            return
        for widget in tree.get_children():
            tree.delete(widget)
        for _, row in recommendations.iterrows():
            tree.insert("", tk.END, values=(row['id'], row['title'], row['author'], row['genre']))

    def borrow_selected_book():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No book selected.")
            return
        book_id = tree.item(selected_item)['values'][0]
        borrow_book(book_id)

    recommendation_window = Toplevel()
    recommendation_window.title("Book Recommendations")
    tk.Label(recommendation_window, text="Enter a topic to search for books:").grid(row=0, column=0, padx=10, pady=10)
    entry_query = tk.Entry(recommendation_window, width=40)
    entry_query.grid(row=0, column=1, padx=10, pady=10)
    tk.Button(recommendation_window, text="Search", command=get_recommendations).grid(row=0, column=2, padx=10, pady=10)

    tree = Treeview(recommendation_window, columns=("ID", "Title", "Author", "Genre"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Title", text="Title")
    tree.heading("Author", text="Author")
    tree.heading("Genre", text="Genre")
    tree.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    tk.Button(recommendation_window, text="Borrow Book", command=borrow_selected_book).grid(row=2, column=0, pady=20)

def open_librarian_dashboard():
    """Create the librarian dashboard."""
    def add_book():
        title = entry_title.get()
        author = entry_author.get()
        genre = entry_genre.get()
        if not title or not author or not genre:
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        add_new_book(title, author, genre)

    dashboard_window = Toplevel()
    dashboard_window.title("Librarian Dashboard")
    tk.Label(dashboard_window, text="Title").grid(row=0, column=0, padx=10, pady=10)
    entry_title = tk.Entry(dashboard_window)
    entry_title.grid(row=0, column=1, padx=10, pady=10)
    tk.Label(dashboard_window, text="Author").grid(row=1, column=0, padx=10, pady=10)
    entry_author = tk.Entry(dashboard_window)
    entry_author.grid(row=1, column=1, padx=10, pady=10)
    tk.Label(dashboard_window, text="Genre").grid(row=2, column=0, padx=10, pady=10)
    entry_genre = tk.Entry(dashboard_window)
    entry_genre.grid(row=2, column=1, padx=10, pady=10)
    tk.Button(dashboard_window, text="Add Book", command=add_book).grid(row=3, column=0, columnspan=2, pady=20)
    tk.Button(dashboard_window, text="View Stock", command=view_stock_status).grid(row=4, column=0, columnspan=2, pady=20)

# -------------------------------
# Main Program
# -------------------------------
def main():
    root = tk.Tk()
    root.title("Library Management System")
    tk.Label(root, text="Welcome to the Library Management System!", font=("Arial", 16)).pack(pady=20)
    tk.Button(root, text="User Login", command=open_login_window, width=20).pack(pady=10)
    tk.Button(root, text="Librarian Dashboard", command=open_librarian_dashboard, width=20).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    main()
import tkinter as tk
from tkinter import messagebox, Toplevel
from tkinter.ttk import Treeview
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta

# -------------------------------
# Initialize Data
# -------------------------------
books = pd.DataFrame([
    {"id": 1, "title": "Introduction to AI", "author": "John Doe", "genre": "AI", "availability": True},
    {"id": 2, "title": "Data Science Basics", "author": "Jane Smith", "genre": "Data Science", "availability": True},
    {"id": 3, "title": "Deep Learning Insights", "author": "Geoff Hinton", "genre": "Deep Learning", "availability": True},
    {"id": 4, "title": "Machine Learning Advanced", "author": "Andrew Ng", "genre": "Machine Learning", "availability": True},
    {"id": 5, "title": "Neural Networks Uncovered", "author": "Ian Goodfellow", "genre": "Deep Learning", "availability": True},
])

users = pd.DataFrame([
    {"id": 1, "name": "Alice", "password": "alice123", "borrowed_books": []},
    {"id": 2, "name": "Bob", "password": "bob123", "borrowed_books": []},
    {"id": 3, "name": "Charlie", "password": "charlie123", "borrowed_books": []},
])

logged_in_user = None

# -------------------------------
# Functions
# -------------------------------
def authenticate_user(username, password):
    """Authenticate user credentials."""
    global logged_in_user
    user = users[(users['name'] == username) & (users['password'] == password)]
    if not user.empty:
        logged_in_user = user.iloc[0]
        messagebox.showinfo("Login Successful", f"Welcome, {logged_in_user['name']}!")
        open_user_dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def recommend_books(query):
    """AI-based book recommendation using TF-IDF and Cosine Similarity."""
    corpus = books['title'] + " " + books['genre']
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    books['similarity'] = similarities
    recommendations = books[books['availability']].sort_values(by='similarity', ascending=False).head(3)
    return recommendations[['id', 'title', 'author', 'genre']]

def borrow_book(book_id):
    """Borrow a selected book."""
    if logged_in_user is None:
        messagebox.showerror("Error", "Please log in first.")
        return
    book = books.loc[books['id'] == book_id]
    if book.empty:
        messagebox.showerror("Error", "Invalid book ID.")
        return
    if not book.iloc[0]['availability']:
        messagebox.showerror("Error", "Book is not available.")
        return

    borrowed_books = logged_in_user['borrowed_books']
    borrowed_books.append({"book_id": book_id, "due_date": datetime.now() + timedelta(days=14)})
    users.loc[users['id'] == logged_in_user['id'], 'borrowed_books'] = [borrowed_books]
    books.loc[books['id'] == book_id, 'availability'] = False
    messagebox.showinfo("Success", f"Book '{book.iloc[0]['title']}' successfully borrowed.")

def view_borrowed_books():
    """Display borrowed books for the logged-in user."""
    if logged_in_user is None:
        messagebox.showerror("Error", "Please log in first.")
        return
    borrowed_books = logged_in_user['borrowed_books']
    if not borrowed_books:
        messagebox.showinfo("Borrowed Books", "No books borrowed.")
        return

    result_window = Toplevel()
    result_window.title(f"Borrowed Books - {logged_in_user['name']}")
    tree = Treeview(result_window, columns=("ID", "Title", "Due Date"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Title", text="Title")
    tree.heading("Due Date", text="Due Date")
    
    for book in borrowed_books:
        book_details = books.loc[books['id'] == book['book_id']].iloc[0]
        due_date_str = book['due_date'].strftime("%Y-%m-%d")
        tree.insert("", tk.END, values=(book_details['id'], book_details['title'], due_date_str))
    tree.pack(fill="both", expand=True)

def add_new_book(title, author, genre):
    """Add a new book to the inventory."""
    new_id = books['id'].max() + 1 if not books.empty else 1
    books.loc[len(books)] = {"id": new_id, "title": title, "author": author, "genre": genre, "availability": True}
    messagebox.showinfo("Success", f"Book '{title}' added successfully!")

def view_stock_status():
    """View the current stock of all books."""
    stock_window = Toplevel()
    stock_window.title("Stock Status")
    tree = Treeview(stock_window, columns=("ID", "Title", "Author", "Genre", "Availability"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Title", text="Title")
    tree.heading("Author", text="Author")
    tree.heading("Genre", text="Genre")
    tree.heading("Availability", text="Availability")
    
    for _, row in books.iterrows():
        tree.insert("", tk.END, values=(row['id'], row['title'], row['author'], row['genre'], "Yes" if row['availability'] else "No"))
    tree.pack(fill="both", expand=True)

# -------------------------------
# Windows
# -------------------------------
def open_login_window():
    """Create the login window."""
    def login_action():
        username = entry_username.get()
        password = entry_password.get()
        authenticate_user(username, password)

    login_window = tk.Tk()
    login_window.title("Library Login")
    tk.Label(login_window, text="Username").grid(row=0, column=0, pady=10, padx=10)
    entry_username = tk.Entry(login_window)
    entry_username.grid(row=0, column=1, pady=10, padx=10)
    tk.Label(login_window, text="Password").grid(row=1, column=0, pady=10, padx=10)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.grid(row=1, column=1, pady=10, padx=10)
    tk.Button(login_window, text="Login", command=login_action).grid(row=2, column=0, columnspan=2, pady=20)
    login_window.mainloop()

def open_user_dashboard():
    """Create the user dashboard."""
    dashboard_window = Toplevel()
    dashboard_window.title("User Dashboard")
    tk.Button(dashboard_window, text="Borrow Book", command=open_recommendation_window).pack(pady=10)
    tk.Button(dashboard_window, text="View Borrowed Books", command=view_borrowed_books).pack(pady=10)

def open_recommendation_window():
    """Create the book recommendation window."""
    def get_recommendations():
        query = entry_query.get()
        recommendations = recommend_books(query)
        if recommendations.empty:
            messagebox.showinfo("Recommendations", "No recommendations found.")
            return
        for widget in tree.get_children():
            tree.delete(widget)
        for _, row in recommendations.iterrows():
            tree.insert("", tk.END, values=(row['id'], row['title'], row['author'], row['genre']))

    def borrow_selected_book():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No book selected.")
            return
        book_id = tree.item(selected_item)['values'][0]
        borrow_book(book_id)

    recommendation_window = Toplevel()
    recommendation_window.title("Book Recommendations")
    tk.Label(recommendation_window, text="Enter a topic to search for books:").grid(row=0, column=0, padx=10, pady=10)
    entry_query = tk.Entry(recommendation_window, width=40)
    entry_query.grid(row=0, column=1, padx=10, pady=10)
    tk.Button(recommendation_window, text="Search", command=get_recommendations).grid(row=0, column=2, padx=10, pady=10)

    tree = Treeview(recommendation_window, columns=("ID", "Title", "Author", "Genre"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Title", text="Title")
    tree.heading("Author", text="Author")
    tree.heading("Genre", text="Genre")
    tree.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    tk.Button(recommendation_window, text="Borrow Book", command=borrow_selected_book).grid(row=2, column=0, pady=20)

def open_librarian_dashboard():
    """Create the librarian dashboard."""
    def add_book():
        title = entry_title.get()
        author = entry_author.get()
        genre = entry_genre.get()
        if not title or not author or not genre:
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        add_new_book(title, author, genre)

    dashboard_window = Toplevel()
    dashboard_window.title("Librarian Dashboard")
    tk.Label(dashboard_window, text="Title").grid(row=0, column=0, padx=10, pady=10)
    entry_title = tk.Entry(dashboard_window)
    entry_title.grid(row=0, column=1, padx=10, pady=10)
    tk.Label(dashboard_window, text="Author").grid(row=1, column=0, padx=10, pady=10)
    entry_author = tk.Entry(dashboard_window)
    entry_author.grid(row=1, column=1, padx=10, pady=10)
    tk.Label(dashboard_window, text="Genre").grid(row=2, column=0, padx=10, pady=10)
    entry_genre = tk.Entry(dashboard_window)
    entry_genre.grid(row=2, column=1, padx=10, pady=10)
    tk.Button(dashboard_window, text="Add Book", command=add_book).grid(row=3, column=0, columnspan=2, pady=20)
    tk.Button(dashboard_window, text="View Stock", command=view_stock_status).grid(row=4, column=0, columnspan=2, pady=20)

# -------------------------------
# Main Program
# -------------------------------
def main():
    root = tk.Tk()
    root.title("Library Management System")
    tk.Label(root, text="Welcome to the Library Management System!", font=("Arial", 16)).pack(pady=20)
    tk.Button(root, text="User Login", command=open_login_window, width=20).pack(pady=10)
    tk.Button(root, text="Librarian Dashboard", command=open_librarian_dashboard, width=20).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    main()
