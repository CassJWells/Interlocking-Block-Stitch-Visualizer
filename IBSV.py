import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import re  # For hex color validation
import tkinter as tk
import os
from tkinter import ttk, Canvas, Entry, Label, Button, Text, Frame, LabelFrame, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to check if a string is a hex color
def is_hex_color(color):
    return re.fullmatch(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})", color) is not None

# Default values for input fields
default_values = {
    "height": "20",
    "width": "20",
    "stitches": "3"
}

# Function to clear placeholder text when user types
def clear_placeholder(event, entry, key):
    if entry.get() == default_values[key]:
        entry.delete(0, tk.END)
        entry.config(fg="black")  # Change text color to normal

# Function to restore placeholder if left empty
def restore_placeholder(event, entry, key):
    if entry.get().strip() == "":
        entry.insert(0, default_values[key])
        entry.config(fg="gray")  # Make placeholder text gray

# Function to get entry value or return default if empty
def get_entry_value(entry, key):
    value = entry.get().strip()
    return int(value) if value.isdigit() else int(default_values[key])

# Function to create an Entry with placeholder behavior
def create_entry(label_text, key, row):
    ttk.Label(top_frame, text=label_text).grid(row=row, column=0, sticky="w")
    entry = Entry(top_frame, fg="gray")
    entry.insert(0, default_values[key])
    entry.grid(row=row, column=1)

    # Bind events for placeholder handling
    entry.bind("<FocusIn>", lambda event, e=entry, k=key: clear_placeholder(event, e, k))
    entry.bind("<FocusOut>", lambda event, e=entry, k=key: restore_placeholder(event, e, k))

    return entry

# Function to generate and display the pattern
def generate_pattern():
    try:
        # Get input values, use default if empty
        height = get_entry_value(height_entry, "height") * 2
        width = get_entry_value(width_entry, "width")
        stitches = get_entry_value(stitches_entry, "stitches")

        border_color_name = border_entry.get().strip()
        border_enabled = bool(border_color_name)

        color_names = color_text.get("1.0", tk.END).strip().split(",")
        
        if len(color_names) < 2:
            status_label.config(text="Insufficient number of colors picked", fg="red")
            return

        # Convert color names and hex codes to RGB
        color_map = {}
        for i, color in enumerate(color_names, start=1):
            color = color.strip().lower()
            if is_hex_color(color):
                color_map[i] = mcolors.hex2color(color)
            elif color in mcolors.CSS4_COLORS:
                color_map[i] = mcolors.to_rgb(mcolors.CSS4_COLORS[color])
            else:
                status_label.config(text=f"Invalid color: {color}", fg="red")
                return

        num_colors = len(color_map)
        pixel_height, pixel_width = 3, 2 * stitches

        # Convert the border color if provided
        if border_enabled:
            if is_hex_color(border_color_name):
                border_color = mcolors.hex2color(border_color_name)
            elif border_color_name in mcolors.CSS4_COLORS:
                border_color = mcolors.to_rgb(mcolors.CSS4_COLORS[border_color_name])
            else:
                status_label.config(text=f"Invalid border color: {border_color_name}", fg="red")
                return

        # Generate the 2 × num_colors unique row cycle
        color_sequence = list(color_map.keys())
        unique_rows = [[color_sequence[0], color_sequence[1]]]

        for i in range(1, 2 * num_colors):
            first, second = unique_rows[-1]
            if i % 2 == 1:  # Rotate the first color forward by 2
                first = color_sequence[(color_sequence.index(first) + 2) % num_colors]
            else:  # Rotate the second color forward by 2
                second = color_sequence[(color_sequence.index(second) + 2) % num_colors]
            unique_rows.append([first, second])

        # Start at the last row of the cycle
        start_index = len(unique_rows) - 1

        # Border thickness is twice the pixel height
        border_thickness = 2 * pixel_height if border_enabled else 0
        scaled_height = height * pixel_height + 2 * border_thickness
        scaled_width = width * pixel_width + 2 * border_thickness

        # Create the grid
        grid = np.ones((scaled_height, scaled_width, 3))

        # Fill the grid with the pattern
        for row in range(height):
            pattern_row = unique_rows[(start_index + row) % len(unique_rows)]
            for col in range(width):
                color_choice = color_map[pattern_row[col % 2]]
                row_start = border_thickness + row * pixel_height
                col_start = border_thickness + col * pixel_width
                grid[row_start : row_start + pixel_height, col_start : col_start + pixel_width] = color_choice

        # Add border if enabled
        if border_enabled:
            grid[:border_thickness, :] = border_color  # Top border
            grid[-border_thickness:, :] = border_color  # Bottom border
            grid[:, :border_thickness] = border_color  # Left border
            grid[:, -border_thickness:] = border_color  # Right border

        # Clear previous pattern
        for widget in frame_right.winfo_children():
            widget.destroy()

        # Display the pattern in Tkinter window
        plt.clf()
        plt.imshow(grid)
        plt.axis("off")

        fig = plt.gcf()
        canvas = FigureCanvasTkAgg(fig, master=frame_right)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        status_label.config(text="Pattern generated successfully!", fg="green")

    except ValueError as e:
        status_label.config(text=f"Error: {e}", fg="red")

def import_pattern():
    try:
        # Check if format.txt exists
        if not os.path.exists("format.txt"):
            status_label.config(text="No format.txt file found!", fg="red")
            return

        # Read file content
        with open("format.txt", "r") as file:
            lines = file.readlines()

        # Ensure file has at least 2 lines
        if len(lines) < 2:
            status_label.config(text="Invalid format.txt structure!", fg="red")
            return

        # Parse first line: height, width, stitches, border color (if any)
        first_line = [x.strip() for x in lines[0].strip().split(",")]
        if len(first_line) < 3:
            status_label.config(text="Invalid format.txt structure!", fg="red")
            return
        
        height, width, stitches = first_line[:3]
        border_color = first_line[3] if len(first_line) > 3 else ""

        # Strip spaces and ensure they are valid integers
        if not height.isdigit() or not width.isdigit() or not stitches.isdigit():
            status_label.config(text="Invalid height, width, or stitches in format.txt!", fg="red")
            return

        # Convert to integers after validation
        height = int(height)
        width = int(width)
        stitches = int(stitches)

        # Parse second line: colors
        colors = [color.strip().lower() for color in lines[1].strip().split(",") if color.strip()]

        # Validate colors: must have at least 2 and be valid
        if len(colors) < 2:
            status_label.config(text="At least two valid colors are required!", fg="red")
            return
        
        for color in colors:
            if not (is_hex_color(color) or color in mcolors.CSS4_COLORS):
                status_label.config(text=f"Invalid color in format.txt: {color}", fg="red")
                return

        # Validate border color if provided
        if border_color and not (is_hex_color(border_color) or border_color in mcolors.CSS4_COLORS):
            status_label.config(text=f"Invalid border color in format.txt: {border_color}", fg="red")
            return

        # Load values into UI
        height_entry.delete(0, tk.END)
        height_entry.insert(0, str(height))

        width_entry.delete(0, tk.END)
        width_entry.insert(0, str(width))

        stitches_entry.delete(0, tk.END)
        stitches_entry.insert(0, str(stitches))

        border_entry.delete(0, tk.END)
        if border_color:
            border_entry.insert(0, border_color)

        color_text.delete("1.0", tk.END)
        color_text.insert("1.0", ", ".join(colors))

        # Show success message
        status_label.config(text="Import successful!", fg="green")

        # Generate pattern with loaded values
        generate_pattern()

    except Exception as e:
        status_label.config(text=f"Import failed: {e}", fg="red")


def export_pattern():
    try:
        # Extract values from input fields
        height = height_entry.get().strip()
        width = width_entry.get().strip()
        stitches = stitches_entry.get().strip()
        border_color = border_entry.get().strip()

        # Get colors from the text box and clean input
        colors = color_text.get("1.0", tk.END).strip().replace("\n", "").split(",")
        colors = [color.strip().lower() for color in colors if color.strip()]  # Remove extra spaces

        # Ensure required fields have values
        if not height or not width or not stitches:
            status_label.config(text="Height, Width, and Stitches are required!", fg="red")
            return

        # Validate colors: must have at least 2 and be valid
        if len(colors) < 2:
            status_label.config(text="At least two valid colors are required!", fg="red")
            return
        
        for color in colors:
            if not (is_hex_color(color) or color in mcolors.CSS4_COLORS):
                status_label.config(text=f"Invalid color: {color}", fg="red")
                return

        # Validate border color if provided
        if border_color and not (is_hex_color(border_color) or border_color in mcolors.CSS4_COLORS):
            status_label.config(text=f"Invalid border color: {border_color}", fg="red")
            return

        # Format the content
        border_value = border_color if border_color else ""  # If no border, keep it blank
        formatted_data = f"{height}, {width}, {stitches}, {border_value}\n{', '.join(colors)}"

        # Write to file
        with open("format.txt", "w") as file:
            file.write(formatted_data)

        status_label.config(text="Export successful! Saved as format.txt", fg="green")

    except Exception as e:
        status_label.config(text=f"Export failed: {e}", fg="red")


# Create Tkinter window
root = tk.Tk()
root.title("Interlocking Block Stitch Visualizer (IBSV)")

# Left panel for inputs
frame_left = tk.Frame(root, padx=20, pady=20)
frame_left.pack(side=tk.LEFT, fill=tk.Y)

# Top section (2 columns)
top_frame = tk.Frame(frame_left)
top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

# Create height, width, and stitches fields with placeholders
height_entry = create_entry("Height:", "height", 0)
width_entry = create_entry("Width:", "width", 1)
stitches_entry = create_entry("Stitches Wide:", "stitches", 2)

# Border Box
ttk.Label(top_frame, text="Border (leave blank for none):").grid(row=3, column=0, sticky="w")
border_entry = Entry(top_frame)
border_entry.grid(row=3, column=1)

# Colors Label Frame
color_frame = LabelFrame(top_frame, text="Colors", padx=5, pady=5)
color_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")
color_text = Text(color_frame, height=5, width=30, wrap=tk.WORD)
color_text.pack()

# Bottom section (3 columns)
bottom_frame = tk.Frame(frame_left)
bottom_frame.grid(row=1, column=0, columnspan=2, pady=10)

# Import button
import_button = Button(bottom_frame, text="Import", command=import_pattern)
import_button.grid(row=0, column=0, padx=5)

# Export button
export_button = Button(bottom_frame, text="Export", command=export_pattern)
export_button.grid(row=0, column=1, padx=5)

# Submit button
submit_button = Button(bottom_frame, text="Generate Pattern", command=generate_pattern)
submit_button.grid(row=0, column=2, padx=5)

# Status label
status_label = Label(frame_left, text="")
status_label.grid(row=2, column=0, columnspan=2)

# Right panel for image
frame_right = tk.Frame(root, padx=20, pady=20)
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Run the Tkinter app
root.mainloop()
