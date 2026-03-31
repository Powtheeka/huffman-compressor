# Huffman Compressor

A Python file compressor using Huffman Coding, with an interactive browser-based tree visualizer.

## Project Structure

```
huffman_project/
│
├── huffman_tree.py   # Node class, tree building, code generation
├── codec.py          # Encode, decode, compress, decompress logic
├── visualizer.py     # Generates & opens interactive HTML tree in browser
├── gui.py            # Tkinter GUI — run this to start the app
└── README.md
```

## How to Run

```bash
python gui.py
```

## Dependencies

Only the Python standard library is needed:
- `tkinter`  — GUI
- `heapq`, `collections` — tree building
- `json`, `tempfile`, `webbrowser` — tree visualizer

No `pip install` required.

## Features

| Feature | Description |
|---|---|
| Compress | Select any `.txt` file → produces `_compressed.bin` + `_codes.txt` |
| Decompress | Select a `.bin` file → produces `_decompressed.txt` |
| Tree Viewer | Opens in browser — zoom, pan, hover nodes for details |
| Code Table | See every character's Huffman code, sorted by length |
| Encoder | Type text, see live Huffman bit encoding |

## File Descriptions

**`huffman_tree.py`**  
Core data structures. Contains the `Node` class, `build_tree()` to construct the Huffman tree from character frequencies, `generate_codes()` to produce the prefix code table, and `tree_to_dict()` to serialize the tree for the visualizer.

**`codec.py`**  
All encoding/decoding logic. `compress()` takes a `.txt` path and returns `(tree, codes, stats)`. `decompress()` takes a `.bin` path and the original tree root.

**`visualizer.py`**  
Builds a self-contained HTML file using D3.js and opens it in your default browser. Fully interactive — scroll to zoom, drag to pan, hover nodes for character info.

**`gui.py`**  
The entry point. Tkinter window with a stats dashboard that updates after each compression.
