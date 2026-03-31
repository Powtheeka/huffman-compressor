import tkinter as tk
from tkinter import filedialog, messagebox
from codec import compress, decompress
from visualizer import show_tree

# ── State
tree_root  = None
last_codes = {}
last_stats = {}

# ── Colors
BG       = "#0d0d0f"
SURFACE  = "#16161a"
SURFACE2 = "#1e1e24"
BORDER   = "#2a2a35"
ACCENT   = "#7c6af7"
ACCENT2  = "#f97066"
GREEN    = "#34d399"
TEXT     = "#e8e8f0"
MUTED    = "#6b6b80"


# ─────────────────────────────────────────
# Actions
# ─────────────────────────────────────────
def on_compress():
    global tree_root, last_codes, last_stats
    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not path:
        return
    try:
        tree_root, last_codes, last_stats = compress(path)
        update_dashboard()
        messagebox.showinfo("✅ Done",
            f"Compressed successfully!\n\n"
            f"Original:    {last_stats['original_kb']} KB\n"
            f"Compressed: {last_stats['compressed_kb']} KB\n"
            f"Saved:        {last_stats['ratio']}%\n\n"
            f"Saved to: {last_stats['out_path']}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def on_decompress():
    if tree_root is None:
        messagebox.showwarning("No tree", "Please compress a file first.")
        return
    path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])
    if not path:
        return
    try:
        out = decompress(path, tree_root)
        messagebox.showinfo("✅ Done", f"Decompressed!\nSaved to: {out}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def on_show_tree():
    if tree_root is None:
        messagebox.showwarning("No tree", "Please compress a file first.")
        return
    show_tree(tree_root, last_codes, last_stats)


# ─────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────
dash_labels = {}

def update_dashboard():
    if not last_stats:
        return
    dash_labels["original"].config(text=f"{last_stats['original_kb']} KB")
    dash_labels["compressed"].config(text=f"{last_stats['compressed_kb']} KB")
    dash_labels["ratio"].config(text=f"{last_stats['ratio']}%", fg=ACCENT2)
    dash_labels["chars"].config(text=str(last_stats['unique_chars']))


# ─────────────────────────────────────────
# Build GUI
# ─────────────────────────────────────────
def build_gui():
    win = tk.Tk()
    win.title("Huffman Compressor")
    win.geometry("500x520")
    win.configure(bg=BG)
    win.resizable(True, True)

    # ── Title bar
    title = tk.Frame(win, bg=SURFACE, pady=14)
    title.pack(fill="x")
    tk.Label(title, text="◈  HUFFMAN COMPRESSOR",
             font=("Courier", 14, "bold"), bg=SURFACE, fg=ACCENT).pack()
    tk.Label(title, text="lossless file compression · optimal prefix codes",
             font=("Courier", 9), bg=SURFACE, fg=MUTED).pack()

    # ── Stats dashboard
    dash = tk.Frame(win, bg=SURFACE2, padx=20, pady=14)
    dash.pack(fill="x", padx=16, pady=(16, 0))
    tk.Label(dash, text="COMPRESSION STATS", font=("Courier", 9, "bold"),
             bg=SURFACE2, fg=MUTED).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

    for i, (key, label, col) in enumerate([
        ("original",   "Original",    0),
        ("compressed", "Compressed",  2),
        ("ratio",      "Ratio",       0),
        ("chars",      "Unique Chars",2),
    ]):
        row = (i // 2) * 2 + 1
        tk.Label(dash, text=label, font=("Courier", 9),
                 bg=SURFACE2, fg=MUTED).grid(row=row, column=col, sticky="w", padx=(0, 4))
        lbl = tk.Label(dash, text="—", font=("Courier", 14, "bold"),
                       bg=SURFACE2, fg=GREEN)
        lbl.grid(row=row + 1, column=col, sticky="w", padx=(0, 28), pady=(0, 6))
        dash_labels[key] = lbl

    # ── Buttons
    btn_frame = tk.Frame(win, bg=BG, pady=10)
    btn_frame.pack(fill="x", padx=16)

    def make_btn(text, cmd, hover_color):
        b = tk.Button(btn_frame, text=text, command=cmd,
                      font=("Courier", 11, "bold"),
                      bg=SURFACE2, fg=TEXT, activebackground=hover_color,
                      activeforeground="white", relief="flat", bd=0,
                      padx=16, pady=10, cursor="hand2",
                      highlightthickness=1, highlightbackground=BORDER)
        b.pack(fill="x", pady=4)
        b.bind("<Enter>", lambda e: b.config(bg=hover_color, fg="white"))
        b.bind("<Leave>", lambda e: b.config(bg=SURFACE2, fg=TEXT))
        return b

    make_btn("📂  Compress File",       on_compress,    ACCENT)
    make_btn("📤  Decompress File",     on_decompress,  "#4a9eff")
    make_btn("🌲  View Tree (Browser)", on_show_tree,   GREEN)

    # ── Footer
    tk.Label(win,
             text="Scroll/drag to pan tree  •  Hover nodes for details  •  Use ⌂ to reset",
             font=("Courier", 8), bg=BG, fg=MUTED).pack(side="bottom", pady=8)

    win.mainloop()


if __name__ == "__main__":
    build_gui()
