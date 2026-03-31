import os
from huffman_tree import build_tree, generate_codes


# ─────────────────────────────────────────
# Encode text → binary string
# ─────────────────────────────────────────
def encode(text, codes):
    return ''.join(codes[char] for char in text)


# ─────────────────────────────────────────
# Binary string → bytes (with padding)
# ─────────────────────────────────────────
def to_bytes(encoded_text):
    extra_padding = 8 - len(encoded_text) % 8
    if extra_padding == 8:
        extra_padding = 0
    encoded_text += "0" * extra_padding
    padded_info = "{0:08b}".format(extra_padding)
    encoded_text = padded_info + encoded_text

    byte_array = bytearray()
    for i in range(0, len(encoded_text), 8):
        byte_array.append(int(encoded_text[i:i+8], 2))
    return byte_array


# ─────────────────────────────────────────
# Remove padding from binary string
# ─────────────────────────────────────────
def remove_padding(padded_text):
    extra_padding = int(padded_text[:8], 2)
    padded_text = padded_text[8:]
    if extra_padding == 0:
        return padded_text
    return padded_text[:-extra_padding]


# ─────────────────────────────────────────
# Decode binary string → original text
# ─────────────────────────────────────────
def decode(encoded_text, root):
    decoded  = ""
    current  = root
    for bit in encoded_text:
        current = current.left if bit == "0" else current.right
        if current.char is not None:
            decoded += current.char
            current  = root
    return decoded


# ─────────────────────────────────────────
# Compress a .txt file → .bin file
# Returns (tree_root, codes, stats_dict)
# ─────────────────────────────────────────
def compress(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    if not text:
        raise ValueError("File is empty!")

    tree  = build_tree(text)
    codes = generate_codes(tree)

    encoded_text = encode(text, codes)
    byte_data    = to_bytes(encoded_text)

    out_path = file_path.replace(".txt", "_compressed.bin")
    with open(out_path, "wb") as f:
        f.write(byte_data)

    # Save codes table alongside the binary
    codes_path = file_path.replace(".txt", "_codes.txt")
    with open(codes_path, "w") as f:
        for char, code in codes.items():
            f.write(f"{repr(char)}:{code}\n")

    stats = {
        "original_bits":   os.path.getsize(file_path) * 8,
        "compressed_bits": len(encoded_text),
        "ratio":           round((1 - len(encoded_text) / (os.path.getsize(file_path) * 8)) * 100, 1),
        "unique_chars":    len(codes),
        "total_chars":     len(text),
        "original_kb":     round(os.path.getsize(file_path) / 1024, 2),
        "compressed_kb":   round(len(byte_data) / 1024, 2),
        "out_path":        out_path,
    }

    return tree, codes, stats


# ─────────────────────────────────────────
# Decompress a .bin file → .txt file
# Needs the tree_root from compression
# ─────────────────────────────────────────
def decompress(file_path, tree_root):
    with open(file_path, "rb") as f:
        bit_string = ""
        byte = f.read(1)
        while byte:
            bit_string += bin(ord(byte))[2:].rjust(8, '0')
            byte = f.read(1)

    encoded_text = remove_padding(bit_string)
    decoded_text = decode(encoded_text, tree_root)

    out_path = file_path.replace(".bin", "_decompressed.txt")
    with open(out_path, "w", encoding='utf-8') as f:
        f.write(decoded_text)

    return out_path


def inspect_binary(file_path, max_bytes=64):
    """Print a human-readable hex + binary dump of a .bin file."""
    with open(file_path, "rb") as f:
        data = f.read(max_bytes)

    print(f"{'OFFSET':<8} {'HEX':<24} {'BINARY':<72} {'ASCII'}")
    print("─" * 115)
    for i in range(0, len(data), 8):
        chunk  = data[i:i+8]
        hex_   = ' '.join(f'{b:02X}' for b in chunk)
        binary = ' '.join(f'{b:08b}' for b in chunk)
        ascii_ = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"{i:<8} {hex_:<24} {binary:<72} {ascii_}")
