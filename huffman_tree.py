import heapq
from collections import Counter


# ─────────────────────────────────────────
# Node class
# ─────────────────────────────────────────
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


# ─────────────────────────────────────────
# Build Huffman Tree
# ─────────────────────────────────────────
def build_tree(text):
    freq_map = Counter(text)
    heap = []
    for char, freq in freq_map.items():
        heapq.heappush(heap, Node(char, freq))

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0]


# ─────────────────────────────────────────
# Generate Codes from Tree
# ─────────────────────────────────────────
def generate_codes(root, current_code="", codes=None):
    if codes is None:
        codes = {}
    if root is None:
        return codes

    if root.char is not None:
        codes[root.char] = current_code if current_code else "0"
        return codes

    generate_codes(root.left,  current_code + "0", codes)
    generate_codes(root.right, current_code + "1", codes)
    return codes


# ─────────────────────────────────────────
# Convert tree to dict (for visualizer)
# ─────────────────────────────────────────
def tree_to_dict(node, code=""):
    if node is None:
        return None

    result = {
        "freq": node.freq,
        "code": code,
        "children": []
    }

    if node.char is not None:
        display = repr(node.char).strip("'")
        result["name"]   = f"{display} ({node.freq})"
        result["isLeaf"] = True
        result["char"]   = display
    else:
        result["name"]   = str(node.freq)
        result["isLeaf"] = False
        if node.left:
            result["children"].append(tree_to_dict(node.left,  code + "0"))
        if node.right:
            result["children"].append(tree_to_dict(node.right, code + "1"))

    return result
