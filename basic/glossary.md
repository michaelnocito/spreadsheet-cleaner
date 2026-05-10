# Python & Coding Glossary
### Spreadsheet Cleaner — Plain-English Reference

New to a word? Look it up here and jump back to the guide.
These aren't textbook definitions — they're the answers to
"wait, what does that mean?" written the way a trainer would explain it.

> **This glossary is for the Basic layer.**
> It covers every term used in [`spreadsheet_cleaner.py`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/spreadsheet_cleaner.py)
> and [`guide_basic.md`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/guide_basic.md).

---

## Python Terms

### `import`
Borrows a toolbox someone else built so you can use it in your code.
When you see `import pandas`, you're saying: *"go get the pandas library
 and make it available in this file."*
Without it, Python only knows its built-in basics.

---

### `def` — Define a Function
A function is a named set of instructions you write once and can run
as many times as you need. `def` is how you create one.

```python
def greet():
    print("Hello!")
```

After writing that, you can call `greet()` anywhere in the file
and it runs those instructions. In this project, `load_file()` and
`report()` are both functions.

→ See how they're used in [`guide_basic.md — What the App Does`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/guide_basic.md#what-the-app-does)

---

### `return`
Sends a result back to whoever called the function.
Think of a function like a vending machine: you put something in,
it processes it, and `return` is the part where it gives you back the result.

In this project, `load_file()` returns a DataFrame (your spreadsheet)
so that `report()` can use it.

---

### `if` / `elif` / `else`
Makes a decision. Python checks a condition — if it's true, it does
one thing. If not, it moves to the next option.

```python
if file.endswith(".csv"):
    # load as CSV
elif file.endswith(".xlsx"):
    # load as Excel
else:
    # tell the user it's not a supported type
```

In plain English: *"If this, do that. Otherwise if this other thing,
do that instead. If nothing matched, do this."*

---

### `for` Loop
Does something once for every item in a list.

```python
for column in df.columns:
    print(column)
```

In plain English: *"For each column in the spreadsheet, print its name."*
This is how the app lists every column and checks each one for missing values.

---

### f-string
A string (text) with a variable baked right into it. The `f` at the
start tells Python to look for `{}` and fill them in with real values.

```python
name = "Sarah"
print(f"Hello, {name}!")
# prints: Hello, Sarah!
```

Without f-strings you'd have to piece strings together manually.
With them, you just write the sentence and drop variables in where you need them.

---

### `None`
Python's way of saying *"nothing here."* It's not zero, it's not
an empty string — it's the complete absence of a value.

In a spreadsheet, an empty cell becomes `None` (or `NaN`) when
loaded into Python. That's what the missing value check looks for.

---

### `if __name__ == "__main__"`
This tells Python: *"only run this block if someone launched this
file directly — not if another file imported it."*

It's the entry point — the ignition switch. When you type
`python spreadsheet_cleaner.py` in the terminal, Python sees this
block and knows that's where to start.

It's one of the most common lines in Python programs and one of the
most confusing to beginners. Just know: it means *"start here."*

→ See it in context in [`guide_basic.md — What the App Does`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/guide_basic.md#what-the-app-does)

---

### `input()`
Pauses the program and asks the user to type something.
Whatever they type gets stored as a string (text) that the
program can then use.

```python
file_path = input("Enter the file path: ")
```

That's how the app knows which spreadsheet to open —
it waits for you to tell it.

---

### DataFrame
Pandas' word for a spreadsheet loaded into Python.
Rows, columns, cell values — all the structure you're used to
seeing in Excel, but now it's in code and you can do things to it
that Excel would take forever to do manually.

When `load_file()` opens your `.xlsx` or `.csv`, it comes back as a DataFrame.
Everything `report()` does — counting rows, listing columns,
checking for missing values — is done on that DataFrame.

---

### `isnull()` / `sum()`
`isnull()` checks every cell and returns `True` if it's empty, `False` if it has a value.
`sum()` then counts how many `True`s there are — because in Python, `True` counts as 1.

Together, `df.isnull().sum()` gives you a count of missing values per column.
That's the engine behind the ⚠️ warnings in the report.

---

## General Coding Terms

### Terminal / Shell
The text window where you type commands to run your code.
No clicking, no menus — just you typing instructions directly
and the computer responding.

In this project, the terminal is where you run `python spreadsheet_cleaner.py`
and where the report prints out.

→ See how to open yours in [`guide_basic.md — How to Run the App`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/guide_basic.md#how-to-run-the-app)

---

### Script
A file of code that runs from top to bottom when you execute it.
`spreadsheet_cleaner.py` is a script. When you run it, Python
starts at line 1 and works its way down.

---

### Library / Package
Pre-built code someone else wrote that you can borrow.
Instead of writing your own spreadsheet loader from scratch,
you import `pandas` — a library that already does it perfectly.

In this project: `pandas` handles the spreadsheet, `os` handles file paths.

---

### Virtual Environment
An isolated workspace just for one project's libraries.
When you install `pandas` inside a virtual environment, it only
exists there — it doesn't affect anything else on your computer.

That's why you activate `.venv` before running the project.
If you forget, the libraries won't be found.

→ Setup instructions in [`README.md — How to Get Started`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/README.md#how-to-get-started)

---

### Error / Exception
Python stopping to tell you something went wrong.
Errors aren't failures — they're Python being specific about what it needs.
The last line of an error message is almost always the most useful part.

Common ones you might see in this project:
- `FileNotFoundError` — the path you typed doesn't point to a real file
- `ModuleNotFoundError` — a library isn't installed (run `pip install` again)
- `ValueError` — something was the wrong type or format

---

### Syntax
The grammar rules of a programming language.
Just like a sentence needs punctuation in the right places,
Python code needs colons, indentation, and parentheses exactly where they belong.
A `SyntaxError` means Python couldn't understand what you wrote.

---

### String
Any text in quotes. `"hello"`, `"example_messy_dates.xlsx"`, `"2021-03-15"`
are all strings. Python treats them as text, not numbers or code.

---

### Integer / Float
Two types of numbers:
- **Integer** — a whole number with no decimal: `10`, `42`, `1001`
- **Float** — a number with a decimal point: `3.14`, `10.0`

In this project, row and column counts are integers.

---

### Boolean
`True` or `False` — nothing else. Every `if` statement in Python
ultimately comes down to a boolean. Either the condition is true and
the block runs, or it's false and Python skips it.

---

### Path
The address of a file on your computer.
On Windows it looks like: `C:\Users\YourName\spreadsheet-cleaner\sample_data\example_messy_dates.xlsx`
On Mac/Linux: `/Users/YourName/spreadsheet-cleaner/sample_data/example_messy_dates.xlsx`

A **relative path** is a shortcut that starts from where you already are:
`..\sample_data\example_messy_dates.xlsx` means *"go up one folder, then into sample_data."*

→ See path examples in [`guide_basic.md — How to Run the App`](https://github.com/michaelnocito/spreadsheet-cleaner/blob/main/basic/guide_basic.md#how-to-run-the-app)

---

### Comment
A line in code that starts with `#`. Python ignores it completely when running.
Comments exist for the human reading the code — explaining what a line does,
why a decision was made, or what to watch out for.

In this project, comments are part of the curriculum.
Read them.

---

*Glossary maintained as part of the [Spreadsheet Cleaner](https://github.com/michaelnocito/spreadsheet-cleaner) Python learning project by [Michael Nocito](https://github.com/michaelnocito).*
