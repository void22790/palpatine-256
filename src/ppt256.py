import tkinter as tk
import os, sys
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image

rows, cols = 16, 16
cell_grid = []
palette = []
file_path = None

def resource_path(relative_path):
  if hasattr(sys, '_MEIPASS'):
      base_path = sys._MEIPASS
  else:
      base_path = os.path.abspath(".")

  return os.path.join(base_path, relative_path)

def open_file():
  global palette, file_path
  file_paths = filedialog.askopenfilenames(title="Select a Palette File", filetypes=[
    ("PNG Files", "*.png"),
    ("Palette Lump", "*.lmp"),
    ("JASC Palette", "*.pal"),
    ("Microsoft Palette", "*.pal"),
    ("Build Engine Palette", "*.DAT"),
    ("Photoshop Palette", "*.act"),
    ("GIMP Palette", "*.gpl"),
    ])
  if not file_paths: return

  palette = []
  for file_path in file_paths:
    if file_path.endswith(".png"):
      open_png(file_path)
    elif file_path.endswith(".lmp"):
      open_lmp(file_path)
    elif file_path.endswith(".pal"):
      with open(file_path, "rb") as f:
        header = f.read(12)
        if header.startswith(b"JASC-PAL"):
          open_jasc_pal(file_path)
        else:
          open_ms_pal(file_path)
    elif file_path.endswith(".DAT"):
      open_dat(file_path)
    elif file_path.endswith(".act"):
      open_act(file_path)
    elif file_path.endswith(".gpl"):
      open_gpl(file_path)

def load_palette():
  for x in range(rows):
    for y in range(cols):
      color_index = x * cols + y
      r, g, b = palette[color_index]
      hex_color = f"#{r:02x}{g:02x}{b:02x}"
      cell_grid[x][y].config(bg=hex_color)

def export_file():
  global file_path
  file_path = filedialog.asksaveasfilename(title="Select a Palette File", filetypes=[
    ("PNG Files", "*.png"),
    ("Palette Lump", "*.lmp"),
    ("JASC Palette", "*.pal"),
    ("Microsoft Palette", "*.mspal"),
    ("Build Engine Palette", "*.DAT"),
    ("Photoshop Palette", "*.act"),
    ("GIMP Palette", "*.gpl"),
    ],
    defaultextension="*.*")
  if not file_path: return

  print(file_path)
  if file_path.endswith(".png"):
    export_png()
  elif file_path.endswith(".lmp"):
    export_lmp()
  elif file_path.endswith(".pal"):
    export_jasc_pal()
  elif file_path.endswith(".mspal"):
    export_ms_pal()
  elif file_path.endswith(".act"):
    export_act()
  elif file_path.endswith(".gpl"):
    export_gpl()

def _grid():
  
  for x in range(rows):
    row = []
    for y in range(cols):
      cell = tk.Label(frame, width=4, height=2, bg="white", relief=tk.SUNKEN, bd=2 )
      cell.grid(row=x, column=y)
      row.append(cell)
    cell_grid.append(row)

def open_png(file_path):
  image = Image.open(file_path)
  image = image.convert("RGB")
  width, height = image.size

  if (width, height) != (16, 16):
    messagebox.showerror("Error", f"Invalid image size. Select an image with a size of 16x16.")
    return
  
  for x in range(rows):
    for y in range(cols):
      color = image.getpixel((y,x))
      palette.append(color)
      hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
      cell_grid[x][y].config(bg=hex_color)

def open_lmp(file_path):
    """
    Reads a Quake-format .lmp file and loads it into the palette grid.
    """
    try:
        with open(file_path, "rb") as f:
            pal_data = f.read()
    except IOError as e:
        messagebox.showerror("Error", f"Could not read file {file_path}: {e}")
        return

    if len(pal_data) != 768:
        messagebox.showerror("Error", f"Invalid Quake Palette file. Expected 768 bytes, got {len(pal_data)}.")
        return

    for i in range(0, 768, 3):
        r, g, b = pal_data[i:i+3]
        palette.append((r, g, b))

    load_palette()

def open_jasc_pal(file_path):
  with open(file_path, "r") as f:
    data = f.readlines()

  if data[0].strip() != "JASC-PAL" or data[1].strip() != "0100":
    messagebox.showerror("Error", "Invalid JASC Palette file.")

  for line in data[3:]:
    line = line.strip()
    parts = line.split()
    if len(parts) == 1 and parts[0].startswith("#"):
      hex_color = line.lstrip("#")
      r = int(hex_color[0:2], 16)
      g = int(hex_color[2:4], 16)
      b = int(hex_color[4:6], 16)
    elif len(parts) == 3 and all(part.isdigit() for part in parts):
      r, g, b = map(int, parts)
    elif len(parts) == 4 and all(parts[i].isdigit() for i in [0, 1, 2]) and parts[3].startswith("#"):
      r, g, b = map(int, parts[:3])
      
    palette.append((r, g, b))
  
  load_palette()

def open_dat(file_path):
  with open(file_path, "rb") as f:
    data = f.read()

  for i in range(256):
    r = data[i * 3] * 4
    g = data[i * 3 + 1] * 4
    b = data[i * 3 + 2] * 4
    palette.append((r, g, b))

  load_palette()

def open_act(file_path):
  with open(file_path, "rb") as f:
    data = f.read()

  for i in range(0, 768, 3):
    r, g, b = data[i:i+3]
    palette.append((r, g, b))

  load_palette()

def open_ms_pal(file_path):
  with open(file_path, "rb") as f:
    data = f.read()
  
  if data[:4] != b"RIFF":
    messagebox.showerror("Error", "Invalid Microsoft PAL file.")
    return

  offset = 24
  for _ in range(256):
    r = data[offset]
    g = data[offset + 1]
    b = data[offset + 2]
    palette.append((r, g, b))
    offset += 4
  
  load_palette()

def open_gpl(file_path):
  with open(file_path, "r") as f:
    data = f.readlines()

  if data[0].strip() != "GIMP Palette":
    messagebox.showerror("Error", "Invalid GIMP Palette file.")

  for line in data[4:]:
    line = line.strip()
    parts = line.split()
    r = int(parts[0])
    g = int(parts[1])
    b = int(parts[2])
    palette.append((r, g, b))
  
  load_palette()

def export_gpl():
  global file_path

  file_name = os.path.basename(file_path)
  file_name_ne, _ = os.path.splitext(file_name)
  flat_palette = [component for color in palette for component in color]

  with open(file_path, "w") as f:
    f.write("GIMP Palette\n")
    f.write(f"Name: {file_name_ne}\n")
    f.write("Columns: 16\n")
    f.write("#\n")
  
    for i in range(0, len(flat_palette), 3):
        r = flat_palette[i]
        g = flat_palette[i + 1]
        b = flat_palette[i + 2]
        f.write(f"{r}\t{g}\t{b}\n")
  
def export_jasc_pal():
  global file_path

  flat_palette = [component for color in palette for component in color]

  with open(file_path, "w") as f:
    f.write("JASC-PAL\n")
    f.write("0100\n")
    f.write("256\n")
  
    for i in range(0, len(flat_palette), 3):
      r = flat_palette[i]
      g = flat_palette[i + 1]
      b = flat_palette[i + 2]
      f.write(f"{r}\t{g}\t{b}\n")

def export_ms_pal():
  global file_path

  if file_path.endswith(".mspal"): 
    file_path = file_path[:-5] + "pal"

  with open(file_path, "wb") as f:
    f.write(b"RIFF")
    file_size = 20 + len(palette) * 4
    f.write((file_size - 8).to_bytes(4, "little"))
    f.write(b"PAL ")
    f.write(b"data")
    f.write((file_size - 20).to_bytes(4, "little"))
    f.write(b"\x03\x00")
    f.write(len(palette).to_bytes(2, "little"))
    
    for r, g, b in palette:
      f.write(bytes([r, g, b, 0]))

def export_act():
  global file_path

  flat_palette = [component for color in palette for component in color]

  with open(file_path, "wb") as f:
    f.write(bytes(flat_palette))

def export_lmp():
    """
    Writes the current palette data to a Quake-format .lmp file.
    """
    global file_path

    # Flatten the list of (r, g, b) tuples into a single bytes object.
    pal_data = bytes([component for color in palette for component in color])

    if len(pal_data) != 768:
        messagebox.showerror("Error", f"Palette data is incorrect size for .lmp file. Expected 768 bytes, got {len(pal_data)}.")
        return
        
    try:
        with open(file_path, "wb") as f_lmp:
            f_lmp.write(pal_data)
    except IOError as e:
        messagebox.showerror("Error", f"Error writing to {file_path}: {e}")

def export_png():
  global file_path

  image = Image.new("P", (16,16))

  flat_palette = [component for color in palette for component in color]

  image.putpalette(flat_palette)

  for x in range(rows):
    for y in range(cols):
      color_index = x * rows + y
      image.putpixel((y,x), color_index)

  image.save(file_path, format="PNG")

def about():
    message = """
        Palpatine 256
        v1.1
        © 2025 voidsrc
        contact@voidsrc.com
    """
    about_window = tk.Toplevel()
    about_window.title("About Palpatine 256")
    about_window.geometry("350x100")
    about_window.resizable(False, False)
    about_window.attributes('-toolwindow', True)
  
    frame = tk.Frame(about_window)
    frame.pack(padx=5, pady=5)

    icon_image = tk.PhotoImage(file=resource_path("icon.png"))

    icon_label = tk.Label(frame, image=icon_image)
    icon_label.image = icon_image
    icon_label.grid(row=0, column=0)

    text_label = tk.Label(frame, text=message, justify="left", anchor="w")
    text_label.grid(row=0, column=1, sticky="w")

    ok_button = tk.Button(frame, text="Ok", padx=30, pady=2, command=about_window.destroy)
    ok_button.grid(row=0, column=2, padx=5)

def help():
  message = """
Palpatine 256 supports the conversion of PNG, Quake Palette,
Microsoft Palette, JASC Palette, Build Engine PALETTE.DAT,
GIMP GPL, and Photoshop ACT palettes to 8-bit PNG, 
Quake Palette, Microsoft Palette, JASC Palette, GIMP GPL, 
or Photoshop ACT, while preserving the original index order of 
the source file.

You can create a source image in any graphics editor and save it
as a 16×16 PNG file for use with Palpatine 256.

Importing a Palette
1. Go to File > Import File.
2. Choose the appropriate file extension to load as a source palette.

Exporting a Palette
1. Go to File > Export File.
2. Select the desired file extension to save the palette in.

Example
If you have a PNG palette file named my_palette.png (16×16), choose 
PNG as the extension when importing. To convert it into a GIMP .gpl 
file, select File > Export File and choose GIMP .gpl.
"""
  help_window = tk.Toplevel()
  help_window.title("Help Palpatine 256")
  help_window.geometry("600x320")
  help_window.resizable(False, False)
  help_window.iconbitmap(resource_path("icon.ico"))

  frame = tk.Frame(help_window)
  frame.pack(padx=5, pady=5)

  text = scrolledtext.ScrolledText(frame, wrap="none")
  text.pack()
  text.tag_configure("margin", lmargin1=10)
  text.insert("1.0", message, "margin")

root = tk.Tk()
root.title("Palpatine 256")
root.geometry("570x620")
root.iconbitmap(resource_path("icon.ico"))

frame = tk.Frame(root)
frame.pack(expand=True)

menu = tk.Menu(root)
file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=file_menu)
import_file = tk.Menu(file_menu, tearoff=0)
file_menu.add_command(label="Import File...", command=open_file, accelerator="Ctrl+O")
file_menu.add_separator()
file_menu.add_command(label="Export File...", command=export_file, accelerator="Ctrl+S")
file_menu.add_separator()
file_menu.add_command(label="Exit", command=lambda: root.destroy(), accelerator="Ctrl+H")
help_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Help", command=help, accelerator="Ctrl+Q")
help_menu.add_separator()
help_menu.add_command(label="About", command=about)

root.config(menu=menu)

_grid()

root.bind("<Control-o>", lambda event: open_file())
root.bind("<Control-s>", lambda event: export_file())
root.bind("<Control-h>", lambda event: help())
root.bind("<Control-q>", lambda event: root.destroy())

root.mainloop()