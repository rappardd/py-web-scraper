#web scraper to pull data and files from websites using python

import tkinter as tk
from tkinter import messagebox, filedialog
import requests
from bs4 import BeautifulSoup

def scrape_website():
    url = url_entry.get()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')

        result_text.delete(1.0, tk.END)  # Clear previous results

        if soup.title:
            result_text.insert(tk.END, f"Title: {soup.title.string}\n\n")
        else:
            result_text.insert(tk.END, "No title found on the page.\n\n")

        result_text.insert(tk.END, "Links found:\n")
        for link in links:
            result_text.insert(tk.END, f"{link.get('href')}\n")

    except requests.RequestException as e:
        messagebox.showerror("Error", f"Failed to retrieve the page: {str(e)}")

def save_results():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if file_path:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(result_text.get(1.0, tk.END))
        messagebox.showinfo("Save", "Results saved successfully!")

def show_about():
    messagebox.showinfo("About", "Web Scraper v1.0\nCreated by Your Name")

def toggle_dark_mode():
    # Implement dark mode toggle functionality here
    pass

# Create the main window
root = tk.Tk()
root.title("Web Scraper")
root.geometry("600x400")

# Create menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Save Results", command=save_results)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Options menu
options_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Options", menu=options_menu)
options_menu.add_checkbutton(label="Dark Mode", command=toggle_dark_mode)

# Help menu
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About", command=show_about)

# Create and place the URL entry field
url_label = tk.Label(root, text="Enter URL:")
url_label.pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Create and place the submit button
submit_button = tk.Button(root, text="Scrape", command=scrape_website)
submit_button.pack(pady=10)

# Create and place the result text area
result_text = tk.Text(root, height=20, width=70)
result_text.pack(pady=10)

# Start the GUI event loop
root.mainloop()