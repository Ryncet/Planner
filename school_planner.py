import tkinter as tk
from tkinter import messagebox
import json
import os
import subprocess
from datetime import date

DATA_FILE = 'planner.json'

# --- Notifications (for MacOS) ---

def mac_notify(title, message):
    """Send MacOS notification using osascript."""
    try:
        subprocess.run([
            "osascript", "-e",
            f'display notification "{message}" with title "{title}"'
        ], check=True)
    except Exception as e:
        print(f"Notification Error: {e}")

# --- Load and Save Tasks ---

def load_tasks():
    """Load tasks from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    """Save tasks to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

# --- Main App Class ---

class SchoolPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 School Planner")
        self.tasks = load_tasks()

        # --- UI Elements ---
        self.setup_ui()

        # --- First Check for Due Tasks ---
        self.check_due_tasks()

        # --- Show Tasks ---
        self.refresh_tasks()

    def setup_ui(self):
        """Set up all the GUI components."""
        # Input Fields
        tk.Label(self.root, text="Task Title:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.title_entry = tk.Entry(self.root)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Due Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.due_entry = tk.Entry(self.root)
        self.due_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Priority (High/Medium/Low):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.priority_entry = tk.Entry(self.root)
        self.priority_entry.grid(row=2, column=1, padx=5, pady=5)

        # Buttons
        self.add_button = tk.Button(self.root, text="➕ Add Task", command=self.add_task)
        self.add_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.task_listbox = tk.Listbox(self.root, width=60)
        self.task_listbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        self.complete_button = tk.Button(self.root, text="✔️ Mark Completed", command=self.complete_task)
        self.complete_button.grid(row=5, column=0, pady=5)

        self.remove_button = tk.Button(self.root, text="🗑️ Remove Completed", command=self.remove_completed_task)
        self.remove_button.grid(row=5, column=1, pady=5)

    def add_task(self):
        """Add a new task."""
        title = self.title_entry.get()
        due_date = self.due_entry.get()
        priority = self.priority_entry.get()

        if not title or not due_date or not priority:
            messagebox.showwarning("Missing Info", "Please fill in all fields!")
            return

        task = {
            "title": title,
            "due_date": due_date,
            "priority": priority,
            "completed": False
        }
        self.tasks.append(task)
        save_tasks(self.tasks)
        self.refresh_tasks()

        # Clear input fields
        self.title_entry.delete(0, tk.END)
        self.due_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)

    def complete_task(self):
        """Mark selected task as completed."""
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a task to complete.")
            return
        index = selected[0]
        self.tasks[index]['completed'] = True
        save_tasks(self.tasks)
        self.refresh_tasks()
        messagebox.showinfo("Task Completed", "🎯 Task marked as completed!")

    def remove_completed_task(self):
        """Remove selected completed task."""
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a task to remove.")
            return
        index = selected[0]
        if not self.tasks[index]['completed']:
            messagebox.showwarning("Not Completed", "❗ Only completed tasks can be removed!")
            return

        confirm = messagebox.askyesno("Confirm Removal", "Are you sure you want to delete this completed task?")
        if confirm:
            del self.tasks[index]
            save_tasks(self.tasks)
            self.refresh_tasks()
            messagebox.showinfo("Task Removed", "🗑️ Completed task removed!")

    def refresh_tasks(self):
        """Update the displayed task list."""
        self.task_listbox.delete(0, tk.END)
        sorted_tasks = sorted(self.tasks, key=lambda x: x['due_date'])
        self.tasks = sorted_tasks

        for task in self.tasks:
            status = "✔️" if task['completed'] else "❗"
            task_text = f"{status} {task['title']} (Due: {task['due_date']}, Priority: {task['priority']})"
            self.task_listbox.insert(tk.END, task_text)

    def check_due_tasks(self):
        """Notify if there are tasks due today or overdue."""
        today = date.today().isoformat()
        due_tasks = [task for task in self.tasks if not task['completed'] and task['due_date'] <= today]

        if due_tasks:
            task_titles = "\n".join(task['title'] for task in due_tasks)
            mac_notify("📚 Tasks Due!", f"You have tasks due:\n{task_titles}")

# --- Launch the App ---

if __name__ == "__main__":
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (width, height))
    app = SchoolPlannerApp(root)
    root.mainloop()
