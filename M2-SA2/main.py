import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from simulator import MemorySimulator

#The global function that makes the application display at the center by default
def center_window(window):
    window.update_idletasks()
    width = window.winfo_reqwidth()
    height = window.winfo_reqheight()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

#GUI that acquires the input of the parameters of the First-Fit Memory Allocation Simulation
#First window the user sees when executing the program
class InputForm(tk.Tk):
    #Defines the constructor of the setup window of the program
    def __init__(self):
        super().__init__()
        self.title("First Fit Simulation Setup")
        self.geometry("650x500")
        
        self.process_data = [] 
        
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        top_container = ttk.Frame(main_frame)
        top_container.pack(fill="x", pady=5)

        top_container.grid_columnconfigure(0, weight=1)
        top_container.grid_columnconfigure(1, weight=1)

        settings_frame = ttk.LabelFrame(top_container, text="General Settings")
        settings_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        ttk.Label(settings_frame, text="Total Memory Size:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.mem_entry = ttk.Entry(settings_frame, width=10)
        self.mem_entry.grid(row=0, column=1, padx=5, pady=5)
        self.mem_entry.insert(0, "1000")
        ttk.Label(settings_frame, text="Coalescing (CH) Interval:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.ch_entry = ttk.Entry(settings_frame, width=10)
        self.ch_entry.grid(row=1, column=1, padx=5, pady=5)
        self.ch_entry.insert(0, "0")
        ttk.Label(settings_frame, text="Compaction (SC) Interval:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.sc_entry = ttk.Entry(settings_frame, width=10)
        self.sc_entry.grid(row=2, column=1, padx=5, pady=5)
        self.sc_entry.insert(0, "0")

        process_frame = ttk.LabelFrame(top_container, text="Add Processes")
        process_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        ttk.Label(process_frame, text="Process Size:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.size_entry = ttk.Entry(process_frame, width=10)
        self.size_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(process_frame, text="Burst Time:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.burst_entry = ttk.Entry(process_frame, width=10)
        self.burst_entry.grid(row=1, column=1, padx=5, pady=5)

        p_button_frame = ttk.Frame(process_frame)
        p_button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        process_frame.grid_rowconfigure(2, weight=1)
        process_frame.grid_columnconfigure(0, weight=1)
        p_button_frame.grid_columnconfigure(0, weight=1)
        p_button_frame.grid_columnconfigure(1, weight=1)


        self.add_button = ttk.Button(p_button_frame, text="Add Process", command=self.add_process)
        self.add_button.grid(row=0, column=0, padx=5, sticky="ew")

        self.clear_button = ttk.Button(p_button_frame, text="Clear All Processes", command=self.clear_processes)
        self.clear_button.grid(row=0, column=1, padx=5, sticky="ew")

        list_frame = ttk.LabelFrame(main_frame, text="Process Queue (Double-click to Edit/Delete)")
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        cols = ('pid', 'size', 'burst')
        self.process_tree = ttk.Treeview(list_frame, columns=cols, show='headings', height=5)
        
        self.process_tree.heading('pid', text='PID')
        self.process_tree.column('pid', anchor='center', width=50, stretch=False)
        self.process_tree.heading('size', text='Process Size')
        self.process_tree.column('size', anchor='center', width=150)
        self.process_tree.heading('burst', text='Burst Time')
        self.process_tree.column('burst', anchor='center', width=150)
        
        tree_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.process_tree.grid(row=0, column=0, sticky='nsew')
        tree_scroll.grid(row=0, column=1, sticky='ns')
        
        self.process_tree.bind("<Double-Button-1>", self.on_process_double_click)

        self.start_button = ttk.Button(main_frame, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack(pady=10)

        center_window(self)

    #Helper method that deletes all items currently in the Treeview and re-adds them to the process list
    def refresh_process_tree(self):
        self.process_tree.delete(*self.process_tree.get_children())
        for i, p in enumerate(self.process_data):
            pid = i + 1
            self.process_tree.insert("", "end", values=(pid, p['size'], p['burst']))

    #Opens a window for editing or deleting a process when double clicking a row
    def on_process_double_click(self, event):
        try:
            selected_item = self.process_tree.selection()[0]
            if not selected_item:
                return
            
            item_values = self.process_tree.item(selected_item, 'values')
            selected_pid = int(item_values[0])
            selected_index = selected_pid - 1
            
            if 0 <= selected_index < len(self.process_data):
                self.open_edit_window(selected_index)
            else:
                raise IndexError("Selected PID does not match data index.")
        except IndexError:
            pass 

    #Creates the window that allows users to edit or delete a process
    def open_edit_window(self, index):
        try:
            process = self.process_data[index]
        except IndexError:
            messagebox.showerror("Error", "Selected process not found. Please refresh.")
            self.refresh_process_tree()
            return

        pid = index + 1
        
        self.edit_win = tk.Toplevel(self)
        self.edit_win.title(f"Edit Process {pid}")
        self.edit_win.transient(self) 
        
        frame = ttk.Frame(self.edit_win, padding="10")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Process Size:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.edit_size_entry = ttk.Entry(frame, width=10)
        self.edit_size_entry.grid(row=0, column=1, padx=5, pady=5)
        self.edit_size_entry.insert(0, str(process['size']))

        ttk.Label(frame, text="Burst Time:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.edit_burst_entry = ttk.Entry(frame, width=10)
        self.edit_burst_entry.grid(row=1, column=1, padx=5, pady=5)
        self.edit_burst_entry.insert(0, str(process['burst']))
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        save_btn = ttk.Button(btn_frame, text="Save Changes", command=lambda: self.save_edit(index))
        save_btn.pack(side="left", padx=5)
        
        del_btn = ttk.Button(btn_frame, text="Delete Process", command=lambda: self.delete_process(index))
        del_btn.pack(side="left", padx=5)
        
        center_window(self.edit_win)
        self.edit_win.grab_set() 

        self.wait_window(self.edit_win)

    #Function that saves the edited details of a process
    def save_edit(self, index):
        try:
            new_size = int(self.edit_size_entry.get())
            new_burst = int(self.edit_burst_entry.get())
            if new_size <= 0 or new_burst <= 0:
                raise ValueError("Values must be positive.")
            
            self.process_data[index] = {'size': new_size, 'burst': new_burst}
            self.refresh_process_tree()
            self.edit_win.destroy()
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid positive numbers.\n({e})", parent=self.edit_win)

    #Function that deletes the details of a process
    def delete_process(self, index):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Process {index + 1}?", parent=self.edit_win):
            self.process_data.pop(index)
            self.refresh_process_tree()
            self.edit_win.destroy()

    #Function that clears all existing processes that has been input
    def clear_processes(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all processes?"):
            self.process_data.clear()
            self.refresh_process_tree()

    #Function that adds the input process of the user
    def add_process(self):
        try:
            size = int(self.size_entry.get())
            burst = int(self.burst_entry.get())
            if size <= 0 or burst <= 0: raise ValueError
            
            self.process_data.append({'size': size, 'burst': burst})
            self.refresh_process_tree()
            
            self.size_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            self.size_entry.focus()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid positive numbers for Size and Burst Time.")

    #Function that starts the simulation of the First-fit memory allocation algorithm
    def start_simulation(self):
        try:
            total_mem = int(self.mem_entry.get())
            ch = int(self.ch_entry.get())
            sc = int(self.sc_entry.get())
            if total_mem <= 0 or ch < 0 or sc < 0:
                raise ValueError("Settings must be valid numbers (Memory > 0, Intervals >= 0).")
            if not self.process_data:
                raise ValueError("Please add at least one process.")

            self.withdraw() 
            
            app = VisualApp(self)
            
            sim_process_data = list(self.process_data)
            sim = MemorySimulator(total_mem, ch, sc, sim_process_data, app.log_message)
            
            app.run_simulation(sim)
            
            app.mainloop()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.deiconify() 

#GUI that shows a visualization of the First-Fit Memory Allocation Simulation
class VisualApp(tk.Tk):
    #Defines the constructor of the window that visualizes the simulation
    def __init__(self, input_form):
        super().__init__()
        self.simulation = None 
        self.input_form = input_form

        self.title("First Fit Memory Visualizer")
        self.geometry("1000x500") 
        
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="both", expand=True, side="top")

        self.time_label_var = tk.StringVar()
        self.time_label = tk.Label(top_frame, textvariable=self.time_label_var, font=("Arial", 16))
        self.time_label.pack(pady=5)
        
        self.status_label_var = tk.StringVar()
        self.status_label = tk.Label(top_frame, textvariable=self.status_label_var, font=("Arial", 12))
        self.status_label.pack(pady=2)

        self.new_sim_button = ttk.Button(top_frame, text="Run New Simulation", command=self.run_new_simulation)
        self.new_sim_button.pack(pady=5)
        self.new_sim_button.pack_forget() 
        
        self.canvas = tk.Canvas(top_frame, bg="white", height=150) 
        self.canvas.pack(fill="x", expand=False, padx=10, pady=5) 

        log_frame = ttk.LabelFrame(self, text="Simulation Log")
        log_frame.pack(fill="both", expand=True, padx=10, pady=(5,10))

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical")
        self.log_text = tk.Text(log_frame, wrap="word", height=10,
                                yscrollcommand=scrollbar.set, bg="#F0F0F0", state="disabled")
        scrollbar.config(command=self.log_text.yview)
        
        scrollbar.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        center_window(self)

    #Function that defines the functionality of being able to run a new simulation after a finished simulation
    def run_new_simulation(self):
        self.destroy()
        self.input_form.deiconify()
        center_window(self.input_form) 

    #Function that closes the current window and opens up the setup window.
    def on_close(self):
        self.destroy()
        self.input_form.deiconify()
        center_window(self.input_form)

    #Function that stores the simulation object and starts the visualization of the current simulation
    def run_simulation(self, simulation):
        self.simulation = simulation
        self.after(500, self.update_simulation) 

    #Displays the current events that are happening during the simulation.
    def log_message(self, message):
        self.log_text.config(state="normal") 
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) 
        self.log_text.config(state="disabled") 
        self.update_idletasks() 

    #Helper function that gives each process allocating a memory block an unique color
    def _get_color_for_pid(self, pid):
        if pid == -1: return "#E0E0E0"
        r = (pid * 55) % 200 + 55
        g = (pid * 95) % 200 + 55
        b = (pid * 35) % 200 + 55
        return f"#{r:02x}{g:02x}{b:02x}"
    
    #Draws each process that has allocated a memory block
    def draw_memory(self):
        self.canvas.delete("all") 
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1: return
        
        if not self.simulation: return
        
        scale_factor = (canvas_width - 2) / self.simulation.total_memory_size
        self.simulation._sort_blocks()
        
        for block in self.simulation.memory_blocks:
            x1 = 1 + block.start * scale_factor
            y1 = 1
            x2 = 1 + (block.end + 1) * scale_factor
            y2 = canvas_height - 2
            color = self._get_color_for_pid(block.pid)
            
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=2)
            
            text_content = f"PID: {block.pid}\nSize: {block.size}" if not block.is_free else f"Free\nSize: {block.size}"
            
            text_fill = "black"
            if not block.is_free:
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                if brightness < 128:
                    text_fill = "white"
                
            self.canvas.create_text((x1 + x2) / 2, canvas_height / 2, text=text_content, fill=text_fill)

    #Visualizes the events of the simulation for each second in the simulation
    def update_simulation(self):
        if not self.simulation:
            return 

        is_running = self.simulation.step()
        self.time_label_var.set(f"Time: {self.simulation.timeline}")
        self.status_label_var.set(f"Processes Completed: {self.simulation.processes_completed} / {self.simulation.num_processes}")
        self.draw_memory()
        
        if is_running:
            self.after(1000, self.update_simulation)
        else:
            status_message = f"SIMULATION COMPLETE! All {self.simulation.num_processes} processes finished."
            self.time_label_var.set(f"Final Time: {self.simulation.timeline}")
            self.status_label_var.set(status_message)
            self.log_message(f"\n###### {status_message} ######") 
            
            self.new_sim_button.pack(pady=5)
            
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            self.canvas.create_text(
                canvas_width / 2,
                canvas_height / 2,
                text="Simulation Complete!",
                font=("Arial", 24, "bold"),
                fill="black"
            )

if __name__ == "__main__":
    input_app = InputForm()
    input_app.mainloop()