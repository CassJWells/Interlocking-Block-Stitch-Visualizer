import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import re  # For hex color validation
import tkinter as tk
from tkinter import ttk, Canvas, Entry, Label, Button, Text, Frame, LabelFrame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to check if a string is a hex color
def is_hex_color(color):
    return re.fullmatch(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})", color) is not None

# Function to generate and display the pattern
def generate_pattern():
    try:
        # Read user inputs
        height = int(height_entry.get()) * 2
        width = int(width_entry.get())
        stitches = int(stitches_entry.get())

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

# Create Tkinter window
root = tk.Tk()
root.title("Pattern Generator")

# Left panel for inputs
frame_left = tk.Frame(root, padx=20, pady=20)
frame_left.pack(side=tk.LEFT, fill=tk.Y)

# Arrange input fields properly
ttk.Label(frame_left, text="Height:").grid(row=0, column=0, sticky="w")
height_entry = Entry(frame_left)
height_entry.grid(row=0, column=1)

ttk.Label(frame_left, text="Width:").grid(row=1, column=0, sticky="w")
width_entry = Entry(frame_left)
width_entry.grid(row=1, column=1)

ttk.Label(frame_left, text="Stitches Wide:").grid(row=2, column=0, sticky="w")
stitches_entry = Entry(frame_left)
stitches_entry.grid(row=2, column=1)

ttk.Label(frame_left, text="Border (leave blank for none):").grid(row=3, column=0, sticky="w")
border_entry = Entry(frame_left)
border_entry.grid(row=3, column=1)

# Colors Section using LabelFrame
color_frame = LabelFrame(frame_left, text="Colors", padx=5, pady=5)
color_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")
color_text = Text(color_frame, height=5, width=30, wrap=tk.WORD)
color_text.pack()

# Submit button
submit_button = Button(frame_left, text="Generate Pattern", command=generate_pattern)
submit_button.grid(row=5, column=0, columnspan=2, pady=10)

# Status label
status_label = Label(frame_left, text="")
status_label.grid(row=6, column=0, columnspan=2)

# Right panel for image
frame_right = tk.Frame(root, padx=20, pady=20)
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Run the Tkinter app
root.mainloop()
