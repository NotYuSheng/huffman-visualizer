import tkinter as tk
from tkinter import ttk
import heapq
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading

# === Huffman Tree Node ===
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    def __lt__(self, other):
        """Enable priority queue behavior for the nodes."""
        return self.freq < other.freq

# === Huffman Logic ===
def build_huffman_tree(freq_map):
    heap = [Node(ch, freq) for ch, freq in freq_map.items()]
    heapq.heapify(heap)
    steps = []

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = Node(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        heapq.heappush(heap, parent)
        steps.append((left, right, parent.freq))

    return heap[0] if heap else None, steps

def assign_codes(node, prefix="", code_map=None):
    if code_map is None:
        code_map = {}
    if node:
        if node.char is not None:
            code_map[node.char] = prefix
        assign_codes(node.left, prefix + "0", code_map)
        assign_codes(node.right, prefix + "1", code_map)
    return code_map

def draw_tree_matplotlib(root):
    G = nx.DiGraph()
    labels = {}
    pos = {}

    def add_edges(node, x=0.0, y=0.0, dx=1.0):
        if node:
            node_id = id(node)
            label = f"{node.char}:{node.freq}" if node.char else f"{node.freq}"
            labels[node_id] = label
            pos[node_id] = (x, -y)
            if node.left:
                G.add_edge(node_id, id(node.left))
                add_edges(node.left, x - dx, y + 1, dx / 1.5)
            if node.right:
                G.add_edge(node_id, id(node.right))
                add_edges(node.right, x + dx, y + 1, dx / 1.5)

    add_edges(root)
    fig, ax = plt.subplots(figsize=(7, 6))
    nx.draw(G, pos, labels=labels, with_labels=True, arrows=False, ax=ax)
    ax.set_title("Huffman Tree")
    plt.tight_layout()
    return fig

# === Heatmap Color Helper ===
def get_heat_color(freq, max_freq=10):
    freq = min(freq, max_freq)
    intensity = int(255 - (freq / max_freq) * 180)
    return f"#ff{intensity:02x}{intensity:02x}"

# === GUI Application ===
class HuffmanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Huffman Coding Visualizer")
        self.root.geometry("980x720")

        self.input_text = tk.StringVar()

        # Main container for columns
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # Left column: fixed 980px
        self.left_frame = tk.Frame(self.main_frame, width=980)
        self.left_frame.pack(side="left", fill="y")
        self.left_frame.pack_propagate(False)

        tk.Label(self.left_frame, text="Enter Text:", font=("Arial", 12)).pack(pady=(10, 0))
        tk.Entry(self.left_frame, textvariable=self.input_text, width=60, font=("Arial", 12)).pack(pady=(0, 10))
        ttk.Button(self.left_frame, text="Run", command=self.run_animation_threaded).pack()

        self.freq_canvas = tk.Canvas(self.left_frame, height=250, bg="white")
        self.freq_canvas.pack(fill="both", expand=True, padx=10, pady=10)

        self.log = tk.Text(self.left_frame, height=12, font=("Courier", 10))
        self.log.pack(fill="x", padx=10, pady=10)

        # Right column, initially not packed
        self.right_frame = tk.Frame(self.main_frame, width=600)
        self.right_frame.grid_propagate(False)  # Prevent children from changing size
        self.right_frame.config(bg="lightgray")  # Optional: visual aid to see the frame

        # Canvas frame inside the right column
        self.canvas_frame = tk.Frame(self.right_frame, width=600)
        self.canvas_frame.pack(fill="both", expand=False)

    def log_step(self, text):
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.root.update()

    def run_animation_threaded(self):
        threading.Thread(target=self.run_animation).start()

    def run_animation(self):
        self.log.delete("1.0", tk.END)
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        text = self.input_text.get().strip()
        if not text:
            self.log_step("Please enter some text.")
            return

        self.animate_frequency_count(text, lambda freq: self.run_huffman_steps(freq, text))

    def init_freq_blocks(self):
        self.freq_blocks = {}
        self.freq_values = {chr(i): 0 for i in range(ord('a'), ord('z')+1)}
        self.freq_canvas.delete("all")
        self.freq_canvas.update_idletasks()

        canvas_width = self.freq_canvas.winfo_width()
        num_blocks = 26
        padding = 40
        available_width = canvas_width - padding
        spacing = available_width // num_blocks
        offset_x = (canvas_width - (spacing * num_blocks)) // 2

        for i, letter in enumerate(self.freq_values):
            x = offset_x + i * spacing
            rect = self.freq_canvas.create_rectangle(x, 20, x + spacing - 5, 50, fill="lightgray")
            label = self.freq_canvas.create_text(x + (spacing // 2), 35, text=letter, font=("Arial", 10))
            count = self.freq_canvas.create_text(x + (spacing // 2), 65, text="0", font=("Arial", 10))
            self.freq_blocks[letter] = {"rect": rect, "count": count}

    def draw_input_text(self, text, current_index):
        self.freq_canvas.delete("input_text")
        canvas_width = self.freq_canvas.winfo_width()
        char_width = 8
        chars_per_row = max(1, (canvas_width - 40) // char_width)

        for i, ch in enumerate(text):
            row = i // chars_per_row
            col = i % chars_per_row
            x = 20 + col * char_width
            y = 100 + row * 20
            color = "gray" if i < current_index else "orange" if i == current_index else "black"
            self.freq_canvas.create_text(x, y, text=ch, font=("Arial", 10), fill=color, tags="input_text")

    def animate_frequency_count(self, text, callback):
        self.init_freq_blocks()
        self.freq_data = {chr(i): 0 for i in range(ord('a'), ord('z')+1)}
        self.text_to_process = text.lower()
        self.char_index = 0

        def step():
            if self.char_index >= len(self.text_to_process):
                callback(self.freq_data)
                return
            ch = self.text_to_process[self.char_index]
            if ch in self.freq_data:
                self.freq_data[ch] += 1
                block = self.freq_blocks[ch]
                self.freq_canvas.itemconfig(block["count"], text=str(self.freq_data[ch]))
                heat_color = get_heat_color(self.freq_data[ch])
                self.freq_canvas.itemconfig(block["rect"], fill=heat_color)
            self.draw_input_text(self.text_to_process, self.char_index)
            self.char_index += 1
            self.root.after(10, step)

        step()

    def run_huffman_steps(self, final_freq, text):
        self.log_step("\nBuilding Huffman Tree (merging nodes):")
        root, merge_steps = build_huffman_tree(final_freq)

        for i, (left, right, merged_freq) in enumerate(merge_steps):
            left_label = f"{left.char}:{left.freq}" if left.char else f"Node:{left.freq}"
            right_label = f"{right.char}:{right.freq}" if right.char else f"Node:{right.freq}"
            self.log_step(f"Step {i+1}: Merge {left_label} + {right_label} → {merged_freq}")
            time.sleep(0.2)
            self.root.update()

        codes = assign_codes(root)
        self.log_step("\nAssigning Huffman Codes:")
        for ch in sorted(codes):
            self.log_step(f"'{ch}': {codes[ch]}")
        encoded = ''.join(codes[ch] for ch in text.lower() if ch in codes)
        original_bits = len(text) * 8  # 8 bits per ASCII character
        compressed_bits = len(encoded)

        compression_ratio = ((original_bits - compressed_bits) / original_bits) * 100 if original_bits > 0 else 0

        self.log_step(f"\nEncoded: {encoded}")
        self.log_step(f"\nOriginal size: {original_bits} bits")
        self.log_step(f"Compressed size: {compressed_bits} bits")
        self.log_step(f"Compression Ratio: {compression_ratio:.2f}%")

        # Expand window and show tree
        self.root.geometry("1470x720")
        self.right_frame.pack(side="right", fill="both", expand=False)

        fig = draw_tree_matplotlib(root)
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

# === Run App ===
if __name__ == "__main__":
    root = tk.Tk()
    app = HuffmanApp(root)
    root.mainloop()
