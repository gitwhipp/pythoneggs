"""PythonEggs practical interactive programs; real editable Python snippets."""

EXAMPLES = [
    ('SDR signal statistics', 'This example combines a list of numeric readings with sum(), len(), min(), and max(). The / operator produces a floating-point mean, while f-strings format numbers for the preview. Modify readings to observe the statistics.', '''from tkinter import ttk

readings = [-67, -63, -72, -58, -61, -64]
mean = sum(readings) / len(readings)
for title, value in [("Minimum", min(readings)), ("Maximum", max(readings)), ("Average", round(mean, 2))]:
    ttk.Label(preview, text=f"{title}: {value} dBm").pack(anchor="w", padx=20, pady=6)
print("Above -65 dBm:", [x for x in readings if x > -65])'''),
    ('Signal pattern recognition', 'This loop examines readings one at a time. The comparison reading > threshold yields True or False; a conditional expression increments or resets run, and max() keeps the longest run. Change threshold to adjust the detected pattern.', '''from tkinter import ttk

readings = [-72, -64, -59, -55, -70, -61, -57]
threshold = -65
run = best = 0
for reading in readings:
    run = run + 1 if reading > threshold else 0
    best = max(best, run)
ttk.Label(preview, text=f"Longest run: {best}", font=("Sans", 20)).pack(pady=25)'''),
    ('Interactive calculator', 'ttk.Entry creates editable fields. StringVar.get() reads their contents as strings, float() converts them into numbers, and command=calculate attaches a callback without calling it immediately. try/except reports invalid numeric input. Modify the arithmetic operator to experiment.', '''import tkinter as tk
from tkinter import ttk

a = tk.StringVar(value="12")
b = tk.StringVar(value="8")
ttk.Entry(preview, textvariable=a).pack(pady=5)
ttk.Entry(preview, textvariable=b).pack(pady=5)
result = ttk.Label(preview, text="Result: ?")
result.pack(pady=8)
def calculate():
    try:
        result.config(text=f"Result: {float(a.get()) + float(b.get())}")
    except ValueError:
        result.config(text="Enter valid numbers")
ttk.Button(preview, text="Calculate", command=calculate).pack()'''),
    ('Counter application', 'The list count contains a mutable counter. The nested increment() function changes count[0] using +=, then label.config() updates the visible text. Click repeatedly, and compare this approach with an instance attribute in a class.', '''from tkinter import ttk

count = [0]
label = ttk.Label(preview, text="0", font=("Sans", 26))
label.pack(pady=10)
def increment():
    count[0] += 1
    label.config(text=str(count[0]))
ttk.Button(preview, text="Add one", command=increment).pack()'''),
    ('Data filters', 'A list comprehension builds a new list: [expression for item in collection if condition]. The expression number * 10 transforms values; number % 2 == 0 filters even numbers. Edit either portion to change the result.', '''from tkinter import ttk

values = [1, 2, 3, 4, 5, 6]
selected = [number * 10 for number in values if number % 2 == 0]
ttk.Label(preview, text=str(selected), font=("Sans", 17)).pack(pady=24)
print("Filtered:", selected)'''),
    ('Dropdown selection', 'ttk.Combobox creates a dropdown; values= supplies its choices. bind("<<ComboboxSelected>>", callback) registers an event handler. The callback receives an event argument and calls choice.get() to retrieve the selected text.', '''from tkinter import ttk

choice = ttk.Combobox(preview, values=["Python", "Tkinter", "PySide6"], state="readonly")
choice.current(0)
choice.pack(pady=12)
label = ttk.Label(preview, text="Choose a topic")
label.pack()
choice.bind("<<ComboboxSelected>>", lambda event: label.config(text=f"Selected: {choice.get()}"))'''),
]
