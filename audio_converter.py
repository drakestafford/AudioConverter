import os
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES  # Drag-and-drop support
from tkinter import filedialog, ttk, messagebox
from pydub import AudioSegment
import threading

# Set TCLLIBPATH for the tkdnd library
os.environ['TCLLIBPATH'] = '/opt/homebrew/Cellar/tcl-tk/8.6.15/lib/tkdnd2.8'

# Supported audio formats (added .m4a support)
AUDIO_FORMATS = [("MP3 files", "*.mp3"), ("WAV files", "*.wav"), ("FLAC files", "*.flac"),
                 ("OGG files", "*.ogg"), ("M4A files", "*.m4a")]

def set_dark_theme(root):
    """Applies a dark theme to the application."""
    root.configure(bg="#2E2E2E")
    style = ttk.Style(root)
    style.theme_use("clam")

    # Dark theme configuration
    style.configure("TButton", background="#4A4A4A", foreground="white", relief="flat", padding=6, font=("Helvetica", 12))
    style.map("TButton", background=[("active", "#666666")])

    style.configure("TLabel", background="#2E2E2E", foreground="white", font=("Helvetica", 12))
    style.configure("TFrame", background="#2E2E2E")
    style.configure("TListbox", background="#404040", foreground="white")
    style.configure("TProgressbar", background="#00b300")

class AudioConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Converter")
        self.root.geometry("400x400")  # Start at the smallest size
        self.root.minsize(400, 400)
        self.root.maxsize(1000, 800)

        # Make the entire window draggable for files
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.add_files)

        # Apply dark theme
        set_dark_theme(self.root)

        # Select files button
        self.button_select_files = ttk.Button(self.root, text="Select Files", command=self.select_files)
        self.button_select_files.pack(pady=10)

        # Files list label
        self.label_files = ttk.Label(self.root, text="Drag and drop files here or use 'Select Files'")
        self.label_files.pack(pady=10)

        # Selected files display with a wider list box
        self.selected_files = []
        self.file_display = tk.Listbox(self.root, height=5, width=80, bg="#404040", fg="white", selectmode=tk.MULTIPLE)
        self.file_display.pack(pady=5)

        # Bind Delete key to remove selected files
        self.file_display.bind('<Delete>', self.remove_selected_files)

        # Output format selection
        self.label_format = ttk.Label(self.root, text="Select output format:")
        self.label_format.pack(pady=5)

        self.format_var = tk.StringVar(value="mp3")
        self.dropdown_format = ttk.OptionMenu(self.root, self.format_var, "mp3", "wav", "flac", "ogg", "m4a")
        self.dropdown_format.pack(pady=5)

        # Output directory selection
        self.label_directory = ttk.Label(self.root, text="Select output location:")
        self.label_directory.pack(pady=5)

        self.button_select_directory = ttk.Button(self.root, text="Select Output Location", command=self.select_output_directory)
        self.button_select_directory.pack(pady=5)

        self.output_directory = None

        # Convert button
        self.button_convert = ttk.Button(self.root, text="Convert Files", command=self.start_conversion)
        self.button_convert.pack(pady=20)

    def add_files(self, event):
        """Handles the drop event for file drag-and-drop."""
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file not in self.selected_files and self.is_supported_file(file):
                self.selected_files.append(file)
                self.file_display.insert(tk.END, os.path.basename(file))

    def select_files(self):
        """Opens a file dialog to select files."""
        files = filedialog.askopenfilenames(filetypes=AUDIO_FORMATS)
        for file in files:
            if file not in self.selected_files and self.is_supported_file(file):
                self.selected_files.append(file)
                self.file_display.insert(tk.END, os.path.basename(file))

    def is_supported_file(self, file_path):
        """Checks if the dropped file is in a supported audio format."""
        return any(file_path.lower().endswith(ext) for ext in ['.mp3', '.wav', '.flac', '.ogg', '.m4a'])

    def select_output_directory(self):
        """Opens a dialog for selecting the output directory."""
        self.output_directory = filedialog.askdirectory()
        if self.output_directory:
            messagebox.showinfo("Output Directory", f"Selected output directory: {self.output_directory}")

    def start_conversion(self):
        """Starts the audio conversion process in a separate thread."""
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please add some files to convert.")
            return

        if not self.output_directory:
            messagebox.showwarning("No Output Directory", "Please select an output directory.")
            return

        threading.Thread(target=self.convert_files).start()

    def convert_files(self):
        """Performs the audio conversion of the selected files."""
        for file_path in self.selected_files:
            self.convert_single_file(file_path)

        messagebox.showinfo("Conversion Complete", "All files have been converted successfully!")

    def convert_single_file(self, input_path):
        """Converts a single audio file to the selected format."""
        input_file = os.path.basename(input_path)
        input_name, _ = os.path.splitext(input_file)
        output_format = self.format_var.get()

        output_path = os.path.join(self.output_directory, f"{input_name}.{output_format}")
        try:
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format=output_format)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert {input_file}: {e}")

    def remove_selected_files(self, event):
        """Removes the selected files from the listbox and internal file list."""
        selected_indices = self.file_display.curselection()

        # Remove files from the end to the start to avoid index shift issues
        for i in reversed(selected_indices):
            file_name = self.file_display.get(i)
            # Find the full file path in the selected files list
            full_file_path = next((f for f in self.selected_files if os.path.basename(f) == file_name), None)
            
            if full_file_path:
                # Remove from internal list and listbox
                self.selected_files.remove(full_file_path)
                self.file_display.delete(i)

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Create root window with DND capabilities
    app = AudioConverterApp(root)
    root.mainloop()
