# huffman-visualizer

A Python-based tool to explore and visualize Huffman Coding. Given a text input, this tool:

- Builds a frequency table
- Constructs the Huffman tree
- Encodes the input text using Huffman codes
- Visualizes the Huffman tree using `matplotlib` and `networkx`

---

## Demo

<div align="center">

![App Demo](https://github.com/NotYuSheng/huffman-visualizer/blob/main/sample-files/DEMO.gif) <br>

</div>

---

## Setup

To run this project locally, you can use a Python virtual environment.

### System Requirements (for Linux)

Install system-level dependency for Tkinter:

```bash
sudo apt update
sudo apt install python3-tk
```

### 1. Clone the repository

```bash
git clone https://github.com/your-username/huffman-visualizer.git
cd huffman-visualizer
```

### 2. Set up a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python huffman_visualizer.py
```

You’ll be prompted to enter a text string, and the script will display:

* The Huffman codes for each character
* The encoded bitstream
* A visualized Huffman tree
