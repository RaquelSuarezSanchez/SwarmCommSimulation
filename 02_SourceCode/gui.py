import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from main import main as execute_simulation

def reset_gui():
    delete_file(window.label_archivo)

    window.input_robots.config(state="normal")
    window.input_robots.delete(0, tk.END)
    window.input_robots.insert(0, 3)
    window.input_robots.config(state="readonly")

    window.input_x.delete(0, tk.END)
    add_placeholder(window.input_x, "100")
    window.input_y.delete(0, tk.END)
    add_placeholder(window.input_y, "-100")
    window.input_area.delete(0, tk.END)
    add_placeholder(window.input_area, "120")

    window.var_modo.set(2)

def load_file(label_to_edit):
    file_path = filedialog.askopenfilename(
        title="Select Configuration File",
        filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
    )
    if file_path:
        label_to_edit.config(text=f"Selected: {file_path}")

def delete_file(file_label):
    file_label.config(text="No file selected")
    print("File deleted. Going back to manual mode.")

def add_placeholder(entry, text_placeholder):
    entry.insert(0, text_placeholder)
    entry.config(fg='gray')

    def gain_focus(event):
        if entry.cget('fg') == 'gray': # I it is gray, placeholder
            entry.delete(0, tk.END) 
            entry.config(fg='black') 

    def loose_focus(event):
        if entry.get().strip() == '':  # If I leave it empty
            entry.insert(0, text_placeholder) # Put placeholder back
            entry.config(fg='gray')

    entry.bind("<FocusIn>", gain_focus)
    entry.bind("<FocusOut>", loose_focus)

def setWindowSize(window):
    window_width = 600
    window_height = 500

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    pos_x = int((screen_width / 2) - (window_width / 2))
    pos_y = int((screen_height / 2) - (window_height / 2))

    window.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

def addWindowTitle():
    title = tk.Label(
        window, 
        text="Introduce the data for the simulation:", 
        font=("Arial", 15, "bold"), 
        bg="#E0E0E0" 
    )
    title.pack(pady=(20,0))

def addRobotNumComponents(form_frame):
    label_robots = tk.Label(form_frame, text="Number of robots:", bg="#E0E0E0", font=("Arial", 11))
    label_robots.grid(row=0, column=0, sticky="e", padx=10, pady=10)
    window.input_robots = tk.Spinbox(form_frame, from_=3, to=7, width=10, font=("Arial", 11), state="readonly")
    window.input_robots.grid(row=0, column=1, sticky="w", padx=10, pady=10)

def addSVPosComponents(form_frame):
    label_sv = tk.Label(form_frame, text="Position of SV:", bg="#E0E0E0", font=("Arial", 11))
    label_sv.grid(row=1, column=0, sticky="e", padx=10, pady=10)
    position_frame = tk.Frame(form_frame, bg="#E0E0E0")
    position_frame.grid(row=1, column=1, sticky="w", padx=10, pady=10)
    
    label_x = tk.Label(position_frame, text="X:", bg="#E0E0E0", font=("Arial", 10))
    label_x.pack(side="left")
    window.input_x = tk.Entry(position_frame, width=8, font=("Arial", 11))
    add_placeholder(window.input_x, "100")
    window.input_x.pack(side="left", padx=(0, 10))
    
    label_y = tk.Label(position_frame, text="Y:", bg="#E0E0E0", font=("Arial", 10))
    label_y.pack(side="left")
    window.input_y = tk.Entry(position_frame, width=8, font=("Arial", 11))
    add_placeholder(window.input_y, "-100")
    window.input_y.pack(side="left")
    
def addAreaExplComponents(form_frame):
    label_area = tk.Label(form_frame, text="Area of exploration (m):", bg="#E0E0E0", font=("Arial", 11))
    label_area.grid(row=2, column=0, sticky="e", padx=10, pady=10)
    window.input_area = tk.Entry(form_frame, width=10, font=("Arial", 11))
    add_placeholder(window.input_area, "120")
    window.input_area.grid(row=2, column=1, sticky="w", padx=10, pady=10)
    
def addExplModesComponents(form_frame):
    label_mode = tk.Label(form_frame, text="Exploration mode:", bg="#E0E0E0", font=("Arial", 11))
    label_mode.grid(row=3, column=0, sticky="e", padx=10, pady=10)

    radio_frame = tk.Frame(form_frame, bg="#E0E0E0")
    radio_frame.grid(row=3, column=1, sticky="w", padx=10, pady=10)

    window.var_modo = tk.IntVar(value=2)
    radio_free = tk.Radiobutton(
        radio_frame, 
        text="Free Exploration Mode", 
        variable=window.var_modo, 
        value=1,
        bg="#E0E0E0", 
        font=("Arial", 11)
    )
    radio_free.pack(anchor="w") 

    radio_fixed = tk.Radiobutton(
        radio_frame, 
        text="Fixed Exploration Mode", 
        variable=window.var_modo, 
        value=2,    
        bg="#E0E0E0", 
        font=("Arial", 11)
    )
    radio_fixed.pack(anchor="w", pady=(5, 0))    

def addORSeparator(form_frame):
    label_or = tk.Label(form_frame, text="— OR —", bg="#E0E0E0", font=("Arial", 14, "bold"))
    label_or.grid(row=4, column=0, columnspan=2, pady=15) 

def addUploadBtn(form_frame):
    window.label_archivo = tk.Label(
        form_frame, text="No file selected", bg="#E0E0E0", 
        font=("Arial", 9, "italic"), fg="gray", wraplength=400, justify="center"
    )
    upload_btn_frame = tk.Frame(form_frame, bg="#E0E0E0")
    upload_btn_frame.grid(row=5, column=0, columnspan=2, pady=5)

    btn_upload = tk.Button(
        upload_btn_frame, text="↑ Upload JSON", 
        command=lambda: load_file(window.label_archivo),
        font=("Arial", 10), bg="white", width=20
    )
    btn_upload.pack(side="left", padx=5)

    btn_clear = tk.Button(
        upload_btn_frame, text="X Clear File", 
        command=lambda: delete_file(window.label_archivo),
        font=("Arial", 10), bg="#FFCDD2", fg="#B71C1C", width=15
    )
    btn_clear.pack(side="left", padx=5)
    window.label_archivo.grid(row=6, column=0, columnspan=2, pady=(0, 5))

def addStartBtn(window):
    lower_frame = tk.Frame(window, bg="#E0E0E0")
    lower_frame.pack(side="bottom", fill="x", pady=20)

    btn_start = tk.Button(
        lower_frame, 
        text="Start Simulation", 
        command=gatherData_and_start,
        font=("Arial", 12, "bold"), 
        bg="#2196F3", 
        fg="white",
        padx=20, 
        pady=10
    )
    btn_start.pack(side="right", padx=30)

def addComponents(window):
    addWindowTitle()

    form_frame = tk.Frame(window, bg="#E0E0E0")
    form_frame.pack(pady=(5,10))

    addRobotNumComponents(form_frame)
    addSVPosComponents(form_frame)
    addAreaExplComponents(form_frame)
    addExplModesComponents(form_frame)
    addORSeparator(form_frame)
    addUploadBtn(form_frame)

    addStartBtn(window)

def gatherData_and_start():
    file_path_text = window.label_archivo.cget("text")
    file_path = file_path_text.replace("Selected: ", "")
    has_upload = (file_path_text != "No file selected")
    
    num_robots = window.input_robots.get()

    pos_x = window.input_x.get().strip()
    if window.input_x.cget("fg") == "gray": pos_x = ""

    pos_y = window.input_y.get().strip()
    if window.input_y.cget("fg") == "gray": pos_y = ""

    area = window.input_area.get().strip()
    if window.input_area.cget("fg") == "gray": area = ""

    mode = window.var_modo.get()
    
    has_manual_input = (pos_x != "" or pos_y != "" or area != "")

    if has_upload:
        if has_manual_input:
            messagebox.showwarning("Notice", "A file is selected. Manual inputs will be ignored.")
        
        window.withdraw()
        state, msj = execute_simulation(config_file=file_path)
        endSimulation(state, msj)
        return

    if has_manual_input:
        if pos_x == "" or pos_y == "" or area == "":
            messagebox.showerror("Error", "Please fill in ALL manual fields (X, Y, and Area).")
            return
        try:
            val_x = float(pos_x)
            val_y = float(pos_y)
            val_area = float(area)
            
            if val_area < 0:
                messagebox.showerror("Error", "The exploration area cannot be a negative number.")
                return
                
        except ValueError:
            messagebox.showerror("Error", "X, Y, and Area must be valid numbers, not text.")
            return

        data_package = (int(num_robots), val_x, val_y, val_area, mode)
        window.withdraw()
        state, msj = execute_simulation(config_file=None, gui_data=data_package)
        endSimulation(state, msj)
        return

    messagebox.showerror("Missing Data", "Please upload a file or fill all the manual fields.")

def endSimulation(state, msj):
        reset_gui()
        window.deiconify()
        window.lift()
        window.focus_force()
        window.update()
        show_final_msg(state, msj)

def show_final_msg(estado, mensaje):
    if estado == "SUCCESS":
        messagebox.showinfo("Simulation Finished", mensaje)
    elif estado == "DISCONNECTED":
        messagebox.showerror("Connection Lost", mensaje)
    elif estado == "CANCELED":
        messagebox.showwarning("Canceled", mensaje)

window = tk.Tk()
window.title("Simulation of comunication between robots")
window.configure(bg="#E0E0E0")

setWindowSize(window)
addComponents(window)

window.mainloop()


