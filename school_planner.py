import tkinter as tk
from tkinter import messagebox, Scrollbar
import json
import os
import subprocess
from datetime import date

DATA_FILE = 'planner.json'

def mac_notify(title, message):
    try:
        subprocess.run([
            "osascript", "-e",
            f'display notification "{message}" with title "{title}"'
        ], check=True)
    except Exception as e:
        print(f"Notification Error: {e}")

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

class SchoolPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 School Planner")
        self.tasks = load_tasks()

        self.set_size_and_center()

        self.root.configure(bg="#f9f9f9")  # Softer off-white
        self.setup_ui()
        self.check_due_tasks()
        self.refresh_tasks()

    def set_size_and_center(self):
        width, height = 700, 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        input_frame = tk.Frame(self.root, bg="#f9f9f9")
        input_frame.pack(pady=15)

        label_opts = {"font": ("Arial", 11), "bg": "#f9f9f9", "fg": "black"}
        entry_opts = {"bg": "white", "fg": "black", "insertbackground": "black"}

        tk.Label(input_frame, text="Task Title:", **label_opts).grid(row=0, column=0, sticky='w', padx=5)
        self.title_entry = tk.Entry(input_frame, width=40, **entry_opts)
        self.title_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(input_frame, text="Due Date (YYYY-MM-DD):", **label_opts).grid(row=1, column=0, sticky='w', padx=5)
        self.due_entry = tk.Entry(input_frame, width=40, **entry_opts)
        self.due_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(input_frame, text="Priority (High/Medium/Low):", **label_opts).grid(row=2, column=0, sticky='w', padx=5)
        self.priority_entry = tk.Entry(input_frame, width=40, **entry_opts)
        self.priority_entry.grid(row=2, column=1, padx=10, pady=5)

        self.add_button = tk.Button(self.root, text="➕ Add Task", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", command=self.add_task)
        self.add_button.pack(pady=10)

        list_frame = tk.Frame(self.root, bg="#f9f9f9")
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.task_listbox = tk.Listbox(list_frame, width=80, height=15, font=("Arial", 10), bg="white", fg="black")
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = Scrollbar(list_frame, orient="vertical")
        scrollbar.config(command=self.task_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = tk.Frame(self.root, bg="#f9f9f9")
        button_frame.pack(pady=5)

        self.complete_button = tk.Button(button_frame, text="✔️ Mark Completed", bg="#2196F3", fg="black", command=self.complete_task)
        self.complete_button.grid(row=0, column=0, padx=10)

        self.remove_button = tk.Button(button_frame, text="🗑️ Remove Completed", bg="#f44336", fg="black", command=self.remove_completed_task)
        self.remove_button.grid(row=0, column=1, padx=10)

    def add_task(self):
        title = self.title_entry.get()
        due_date = self.due_entry.get()
        priority = self.priority_entry.get().capitalize()

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

        self.title_entry.delete(0, tk.END)
        self.due_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)

    def complete_task(self):
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
        self.task_listbox.delete(0, tk.END)
        sorted_tasks = sorted(self.tasks, key=lambda x: x['due_date'])
        self.tasks = sorted_tasks

        for task in self.tasks:
            status = "✔️" if task['completed'] else "❗"
            color = {
                "High": "🔥",
                "Medium": "⚠️",
                "Low": "💤"
            }.get(task['priority'], "")
            task_text = f"{status} {task['title']} ({task['due_date']}, {task['priority']} {color})"
            self.task_listbox.insert(tk.END, task_text)

    def check_due_tasks(self):
        today = date.today().isoformat()
        due_tasks = [task for task in self.tasks if not task['completed'] and task['due_date'] <= today]
        if due_tasks:
            task_titles = "\n".join(task['title'] for task in due_tasks)
            mac_notify("📚 Tasks Due!", f"You have tasks due:\n{task_titles}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolPlannerApp(root)
    root.mainloop()
