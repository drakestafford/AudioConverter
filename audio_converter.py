import os
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES  # Drag-and-drop support
from tkinter import filedialog, ttk, messagebox
from pydub import AudioSegment
import threading
from ttkbootstrap import Style

# Set TCLLIBPATH for the tkdnd library
os.environ["TCLLIBPATH"] = "/opt/homebrew/Cellar/tcl-tk/8.6.15/lib/tkdnd2.8"

# Supported audio formats (added .m4a support)
AUDIO_FORMATS = [
    ("MP3 files", "*.mp3"),
    ("WAV files", "*.wav"),
    ("FLAC files", "*.flac"),
    ("OGG files", "*.ogg"),
    ("M4A files", "*.m4a"),
]


class AudioConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Converter")
        # Increase the default window size so that all widgets are visible
        self.root.geometry("600x550")
        self.root.minsize(400, 400)
        self.root.maxsize(1000, 800)

        # Make the entire window draggable for files
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.add_files)

        # Apply ttkbootstrap theme
        self.style = Style(theme="superhero")
        self.root.configure(bg=self.style.colors.bg)

        # Theme selection stored in a menu bar instead of the main GUI
        self.theme_var = tk.StringVar(value="superhero")
        self.menubar = tk.Menu(self.root)
        self.theme_menu = tk.Menu(self.menubar, tearoff=0)
        for theme in self.style.theme_names():
            self.theme_menu.add_radiobutton(
                label=theme,
                variable=self.theme_var,
                command=lambda t=theme: self.change_theme(t),
            )
        self.menubar.add_cascade(label="Themes", menu=self.theme_menu)
        self.root.config(menu=self.menubar)

        # Select files button
        self.button_select_files = ttk.Button(
            self.root, text="Select Files", command=self.select_files
        )
        self.button_select_files.pack(pady=10)

        # Files list label
        self.label_files = ttk.Label(
            self.root, text="Drag and drop files here or use 'Select Files'"
        )
        self.label_files.pack(pady=10)

        # Selected files display using a centered Treeview
        self.selected_files = []
        self.file_display = ttk.Treeview(
            self.root,
            columns=("file",),
            show="headings",
            height=8,
        )
        self.file_display.heading("file", text="Selected Files", anchor="center")
        self.file_display.column("file", anchor="center", width=350)
        self.file_display.pack(pady=5, fill="both", expand=True)

        # Bind Delete key to remove selected files
        self.file_display.bind("<Delete>", self.remove_selected_files)

        # Output format selection
        self.label_format = ttk.Label(self.root, text="Select output format:")
        self.label_format.pack(pady=5)

        self.format_var = tk.StringVar(value="mp3")
        self.dropdown_format = ttk.OptionMenu(
            self.root, self.format_var, "mp3", "wav", "flac", "ogg", "m4a"
        )
        self.dropdown_format.pack(pady=5)

        # Output directory selection
        self.label_directory = ttk.Label(self.root, text="Select output location:")
        self.label_directory.pack(pady=5)

        self.button_select_directory = ttk.Button(
            self.root,
            text="Select Output Location",
            command=self.select_output_directory,
        )
        self.button_select_directory.pack(pady=5)

        self.output_directory = None

        # Convert button
        self.button_convert = ttk.Button(
            self.root, text="Convert Files", command=self.start_conversion
        )
        self.button_convert.pack(pady=20)

    def add_files(self, event):
        """Handles the drop event for file drag-and-drop."""
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file not in self.selected_files and self.is_supported_file(file):
                self.selected_files.append(file)
                self.file_display.insert("", tk.END, values=(os.path.basename(file),))

    def select_files(self):
        """Opens a file dialog to select files."""
        files = filedialog.askopenfilenames(filetypes=AUDIO_FORMATS)
        for file in files:
            if file not in self.selected_files and self.is_supported_file(file):
                self.selected_files.append(file)
                self.file_display.insert("", tk.END, values=(os.path.basename(file),))

    def is_supported_file(self, file_path):
        """Checks if the dropped file is in a supported audio format."""
        return any(
            file_path.lower().endswith(ext)
            for ext in [".mp3", ".wav", ".flac", ".ogg", ".m4a"]
        )

    def select_output_directory(self):
        """Opens a dialog for selecting the output directory."""
        self.output_directory = filedialog.askdirectory()
        if self.output_directory:
            messagebox.showinfo(
                "Output Directory",
                f"Selected output directory: {self.output_directory}",
            )

    def start_conversion(self):
        """Starts the audio conversion process in a separate thread."""
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please add some files to convert.")
            return

        if not self.output_directory:
            messagebox.showwarning(
                "No Output Directory", "Please select an output directory."
            )
            return

        threading.Thread(target=self.convert_files).start()

    def convert_files(self):
        """Performs the audio conversion of the selected files."""
        for file_path in self.selected_files:
            self.convert_single_file(file_path)

        messagebox.showinfo(
            "Conversion Complete", "All files have been converted successfully!"
        )

    def convert_single_file(self, input_path):
        """Converts a single audio file to the selected format."""
        input_file = os.path.basename(input_path)
        input_name, _ = os.path.splitext(input_file)
        output_format = self.format_var.get()

        output_path = os.path.join(
            self.output_directory, f"{input_name}.{output_format}"
        )
        export_format = "mp4" if output_format == "m4a" else output_format
        try:
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format=export_format)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert {input_file}: {e}")

    def change_theme(self, themename):
        """Callback for theme selection."""
        self.style.theme_use(themename)
        self.root.configure(bg=self.style.colors.bg)

    def remove_selected_files(self, event):
        """Removes the selected files from the display and internal list."""
        selected_items = self.file_display.selection()

        for item in selected_items:
            file_name = self.file_display.item(item, "values")[0]
            full_file_path = next(
                (f for f in self.selected_files if os.path.basename(f) == file_name),
                None,
            )

            if full_file_path:
                self.selected_files.remove(full_file_path)
                self.file_display.delete(item)


if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Create root window with DND capabilities
    app = AudioConverterApp(root)
    root.mainloop()
