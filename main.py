"""PythonEggs - learn Python while hatching desktop applications."""
APP_VERSION = '0.3.4'  # The sole application version definition.

import builtins
import io
import keyword
import tokenize
import os
from pathlib import Path
import queue
import socket
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont
import traceback

from lessons import LESSONS
from examples import EXAMPLES

APP_NAME = 'PythonEggs'
PROJECT_DIR = Path(__file__).resolve().parent
SOCKET_PATH = Path(tempfile.gettempdir()) / f'pythoneggs-{os.getuid()}.sock'


def activate_existing():
    try:
        with socket.socket(socket.AF_UNIX) as client:
            client.settimeout(0.5)
            client.connect(str(SOCKET_PATH))
            client.sendall(b'SHOW')
        return True
    except (OSError, TimeoutError):
        return False


def claim_instance(messages):
    if activate_existing():
        return None
    try:
        SOCKET_PATH.unlink(missing_ok=True)  # A stale socket from a crash.
        server = socket.socket(socket.AF_UNIX)
        server.bind(str(SOCKET_PATH))
        server.listen(3)
        server.settimeout(0.5)
    except OSError:
        if activate_existing():
            return None
        raise

    def listen():
        while True:
            try:
                conn, _ = server.accept()
                with conn:
                    if conn.recv(64) == b'SHOW':
                        messages.put('SHOW')
            except socket.timeout:
                continue
            except OSError:
                return

    threading.Thread(target=listen, daemon=True).start()
    return server


class PythonEggs(tk.Tk):
    def __init__(self, messages):
        super().__init__(className='PythonEggs')
        self.title(f'{APP_NAME}  •  v{APP_VERSION}')
        self.geometry('1250x780')
        self.minsize(900, 570)
        self.messages = messages
        self.selected_snippet = None
        self.editor_changed = False
        icon = PROJECT_DIR / 'desktopIcon.png'
        if icon.is_file():
            try:
                self.iconphoto(True, tk.PhotoImage(file=str(icon)))
            except tk.TclError:
                pass

        self.palette = {
            'bg': '#141d29', 'panel': '#202e40', 'raised': '#2b3b50',
            'editor': '#121a25', 'paper': '#fff4dc', 'ink': '#e9edf5',
            'muted': '#b4c4d3', 'red': '#e65054', 'gold': '#f0c379',
            'border': '#4b6077', 'selection': '#ac3948',
        }
        self.configure(background=self.palette['bg'])
        self.setup_theme()
        container = ttk.Frame(self, padding=12)
        container.pack(fill='both', expand=True)
        header = ttk.Frame(container, style='Header.TFrame', padding=(12, 8))
        header.pack(fill='x', pady=(0, 10))
        if icon.is_file():
            try:
                logo_image = tk.PhotoImage(file=str(icon))
                max_side = max(logo_image.width(), logo_image.height())
                shrink = max(1, (max_side + 67) // 68)
                self.header_logo = logo_image.subsample(shrink, shrink)
                ttk.Label(header, image=self.header_logo, style='Header.TLabel').pack(side='left', padx=(0, 12))
            except tk.TclError:
                pass
        header_text = ttk.Frame(header, style='Header.TFrame')
        self.header_text = header_text
        header_text.pack(side='left', fill='x', expand=True)
        self.selectable_text(header_text, f'PythonEggs  |  v{APP_VERSION}', bold=True, size=18)
        self.selectable_text(header_text, 'Learn real Python syntax, edit the source, and run it in the interactive preview.')
        self.tabs = ttk.Notebook(container)
        self.tabs.pack(fill='both', expand=True)
        self.learning_tab('Lessons', LESSONS)
        self.learning_tab('Examples', EXAMPLES)
        self.build_tab()
        self.guide_tab()
        self.after(150, self.check_messages)

    def setup_theme(self):
        """Retro IDE colors with legible modern type."""
        c = self.palette
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('.', background=c['bg'], foreground=c['ink'], font=('DejaVu Sans', 10))
        style.configure('TFrame', background=c['panel'])
        style.configure('Header.TFrame', background=c['bg'])
        style.configure('Header.TLabel', background=c['bg'], foreground=c['ink'])
        style.configure('TNotebook', background=c['bg'], borderwidth=0, tabmargins=(3, 3, 3, 0))
        style.configure('TNotebook.Tab', background=c['raised'], foreground=c['ink'],
                        padding=(16, 8), borderwidth=1, bordercolor=c['border'])
        style.map('TNotebook.Tab', background=[('selected', c['red']), ('active', c['border'])],
                  foreground=[('selected', '#ffffff')])
        style.configure('TButton', background=c['raised'], foreground=c['ink'],
                        padding=(12, 7), borderwidth=1, bordercolor=c['border'])
        style.map('TButton', background=[('active', c['red']), ('pressed', c['selection'])],
                  foreground=[('active', '#ffffff')])
        style.configure('TEntry', fieldbackground=c['paper'], foreground='#1c2430', padding=5)
        style.configure('TScrollbar', background=c['raised'], troughcolor=c['bg'],
                        arrowcolor=c['gold'], bordercolor=c['border'])
        style.configure('TPanedwindow', background=c['border'])
        style.configure('TSizegrip', background=c['panel'])

    def selectable_text(self, parent, text=None, *, textvariable=None, bold=False, size=10, pady=0):
        """Display copyable, drag-selectable text instead of a Tkinter Label."""
        widget = tk.Text(parent, height=1, wrap='word', borderwidth=0,
                         highlightthickness=0, relief='flat', padx=0, pady=0,
                         font=('DejaVu Sans', size, 'bold' if bold else 'normal'),
                         background=self.palette['bg'] if parent.winfo_toplevel() == self and parent is getattr(self, 'header_text', None) else self.palette['panel'],
                         foreground=self.palette['gold'] if bold else self.palette['ink'],
                         selectbackground=self.palette['selection'], selectforeground='#ffffff',
                         insertbackground=self.palette['ink'], cursor='xterm', takefocus=True)
        widget.pack(anchor='w', fill='x', pady=pady)

        def update(*_):
            value = textvariable.get() if textvariable is not None else str(text or '')
            widget.configure(state='normal')
            widget.delete('1.0', 'end')
            widget.insert('1.0', value)
            widget.configure(state='disabled')

        update()
        if textvariable is not None:
            textvariable.trace_add('write', update)
        return widget

    def check_messages(self):
        try:
            while self.messages.get_nowait() == 'SHOW':
                self.deiconify()
                self.lift()
                self.focus_force()
        except queue.Empty:
            pass
        self.after(150, self.check_messages)

    def learning_tab(self, title, items):
        page = ttk.Frame(self.tabs, padding=7)
        self.tabs.add(page, text=title)
        # Give the lesson list an actual pixel width, not a weight-based share.
        # Tk's PanedWindow respects an initial pane width and still lets users
        # drag the divider. Keep the sidebar from stretching with the window.
        pane = tk.PanedWindow(page, orient='horizontal', sashwidth=7,
                              sashrelief='raised', borderwidth=0, background=self.palette['border'])
        pane.pack(fill='both', expand=True)
        sidebar = ttk.Frame(pane, width=225)
        work = ttk.Frame(pane)
        pane.add(sidebar, width=225, minsize=170, stretch='never')
        pane.add(work, minsize=400, stretch='always')

        self.selectable_text(sidebar, title, bold=True, size=12, pady=(2, 6))
        picker = tk.Listbox(sidebar, exportselection=False, width=12, font=('DejaVu Sans', 10),
                            background=self.palette['panel'], foreground=self.palette['ink'],
                            selectbackground=self.palette['selection'], selectforeground='#ffffff',
                            highlightthickness=0, borderwidth=0, activestyle='none')
        picker.pack(fill='both', expand=True)
        picker.bind('<Control-c>', lambda _event: (self.clipboard_clear(), self.clipboard_append('\n'.join(picker.get(i) for i in picker.curselection())), 'break')[-1])
        for name, _, _ in items:
            picker.insert('end', name)

        self.selectable_text(work, 'SYNTAX EXPLANATION — SELECT AND COPY TEXT', bold=True, pady=(0, 3))
        # Keep long explanations selectable, with a scrollbar. Leave the
        # 225-pixel sidebar and draggable pane proportions unchanged.
        explanation_frame = ttk.Frame(work)
        explanation_frame.pack(fill='x', pady=(0, 8))
        explanation = tk.Text(explanation_frame, height=15, wrap='word', font=('DejaVu Sans', 11), background=self.palette['paper'], foreground='#222a39',
                              selectbackground=self.palette['selection'], selectforeground='#ffffff',
                              borderwidth=1, relief='solid', padx=12, pady=10,
                              takefocus=True)
        explanation_scroll = ttk.Scrollbar(explanation_frame, orient='vertical',
                                           command=explanation.yview)
        explanation.configure(yscrollcommand=explanation_scroll.set)
        explanation.pack(side='left', fill='both', expand=True)
        explanation_scroll.pack(side='right', fill='y')
        explanation.configure(state='disabled')
        toolbar = ttk.Frame(work)
        toolbar.pack(fill='x', pady=(0, 6))
        status = tk.StringVar(value='Ready')

        columns = ttk.PanedWindow(work, orient='horizontal')
        columns.pack(fill='both', expand=True)
        code_column = ttk.Frame(columns)
        result_column = ttk.Frame(columns)
        columns.add(code_column, weight=3)
        columns.add(result_column, weight=2)
        self.selectable_text(code_column, 'REAL PYTHON CODE — EDIT HERE', bold=True, pady=(0, 5))
        editor_frame = ttk.Frame(code_column)
        editor_frame.pack(fill='both', expand=True)
        editor = tk.Text(editor_frame, font=('DejaVu Sans Mono', 11), undo=True, wrap='none', tabs=('28p',),
                         background=self.palette['editor'], foreground=self.palette['ink'],
                         insertbackground=self.palette['gold'], selectbackground=self.palette['selection'],
                         selectforeground='#ffffff', padx=10, pady=10, relief='flat')
        ybar = ttk.Scrollbar(editor_frame, orient='vertical', command=editor.yview)
        xbar = ttk.Scrollbar(editor_frame, orient='horizontal', command=editor.xview)
        editor.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        editor.grid(row=0, column=0, sticky='nsew')
        ybar.grid(row=0, column=1, sticky='ns')
        xbar.grid(row=1, column=0, sticky='ew')
        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)
        editor.tag_configure('kw', foreground='#e6a1fc')
        editor.tag_configure('string', foreground='#a9eaa1')
        editor.tag_configure('comment', foreground='#8799ad')
        editor.tag_configure('number', foreground='#f0c379')

        self.selectable_text(result_column, 'LIVE WINDOW PREVIEW', bold=True, pady=(0, 5))
        preview_outer = ttk.Frame(result_column, padding=8, relief='groove', borderwidth=1)
        preview_outer.pack(fill='both', expand=True)
        self.selectable_text(result_column, 'CONSOLE / ERRORS', bold=True, pady=(9, 4))
        console = tk.Text(result_column, height=9, font=('DejaVu Sans Mono', 10), wrap='word',
                          background=self.palette['editor'], foreground=self.palette['ink'],
                          selectbackground=self.palette['selection'], selectforeground='#ffffff',
                          insertbackground=self.palette['gold'], padx=8, pady=7, state='disabled')
        console.pack(fill='x')
        self.selectable_text(work, textvariable=status, pady=(6, 0))

        job = [None]
        busy = [False]
        def write_console(message):
            console.configure(state='normal')
            console.insert('end', message)
            console.see('end')
            console.configure(state='disabled')

        def highlight():
            for name in ('kw', 'string', 'comment', 'number'):
                editor.tag_remove(name, '1.0', 'end')
            source = editor.get('1.0', 'end-1c')
            try:
                offsets = [0]
                for line in source.splitlines(keepends=True):
                    offsets.append(offsets[-1] + len(line))
                for tok in tokenize.generate_tokens(io.StringIO(source).readline):
                    token_type, token_text, pos, endpos, _ = tok
                    tag = ('kw' if token_type == tokenize.NAME and keyword.iskeyword(token_text)
                           else 'string' if token_type == tokenize.STRING
                           else 'comment' if token_type == tokenize.COMMENT
                           else 'number' if token_type == tokenize.NUMBER else None)
                    if tag:
                        editor.tag_add(tag, f'{pos[0]}.{pos[1]}', f'{endpos[0]}.{endpos[1]}')
            except (tokenize.TokenError, IndentationError):
                pass

        def run():
            if busy[0]:
                return
            busy[0] = True
            try:
                if job[0] is not None:
                    self.after_cancel(job[0])
                    job[0] = None
                for child in preview_outer.winfo_children():
                    child.destroy()
                console.configure(state='normal')
                console.delete('1.0', 'end')
                console.configure(state='disabled')
                source = editor.get('1.0', 'end-1c')
                # A new frame each run makes widgets, layout managers and variables independent.
                preview = ttk.Frame(preview_outer)
                preview.pack(fill='both', expand=True)
                def lesson_print(*args, sep=' ', end='\n', file=None, flush=False):
                    write_console(sep.join(str(arg) for arg in args) + end)
                namespace = {'__name__': '__main__', 'preview': preview, 'print': lesson_print}
                try:
                    exec(compile(source, '<PythonEggs lesson>', 'exec'), namespace)
                    # Ordinary Tkinter labels are not selectable; Ctrl+C copies a focused preview label.
                    for child in preview.winfo_children():
                        if isinstance(child, (ttk.Label, tk.Label)):
                            child.bind('<Control-c>', lambda _e, w=child: (self.clipboard_clear(), self.clipboard_append(w.cget('text')), 'break')[-1])
                    status.set('Preview updated — edit code to update again.')
                except Exception:
                    write_console(traceback.format_exc())
                    status.set('Python error — details in Console / Errors.')
            finally:
                busy[0] = False

        def changed(_=None):
            if busy[0]:
                return
            highlight()
            if job[0] is not None:
                self.after_cancel(job[0])
            job[0] = self.after(700, run)
            status.set('Updating preview after typing…')

        def select(_=None):
            if not picker.curselection():
                return
            _, description, source = items[picker.curselection()[0]]
            explanation.configure(state='normal')
            explanation.delete('1.0', 'end')
            explanation.insert('1.0', description)
            explanation.yview_moveto(0)
            explanation.configure(state='disabled')
            editor.delete('1.0', 'end')
            editor.insert('1.0', source)
            changed()

        def save_code():
            filename = filedialog.asksaveasfilename(defaultextension='.py', filetypes=[('Python file', '*.py')])
            if filename:
                source = editor.get('1.0', 'end-1c')
                Path(filename).write_text(source + '\n', encoding='utf-8')

        ttk.Button(toolbar, text='Run / Refresh', command=run).pack(side='left')
        ttk.Button(toolbar, text='Save Python Code', command=save_code).pack(side='left', padx=7)
        refresh_info = self.selectable_text(toolbar, 'Auto-refresh: 0.7 seconds after editing')
        refresh_info.pack_forget()
        refresh_info.pack(side='left', padx=10)
        editor.bind('<<Modified>>', lambda event: (editor.edit_modified(False), changed()) if editor.edit_modified() else None)
        picker.bind('<<ListboxSelect>>', select)
        picker.selection_set(0)
        select()

    def build_tab(self):
        frame = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(frame, text='App Builder')
        self.selectable_text(frame, 'Create a simple, independent Tkinter desktop application.', bold=True, size=12)
        self.selectable_text(frame, 'Project name (letters, numbers, spaces, hyphens):', pady=(12, 3))
        self.project_name = ttk.Entry(frame)
        self.project_name.insert(0, 'My First Egg')
        self.project_name.pack(fill='x')
        self.selectable_text(frame, 'Window heading:', pady=(12, 3))
        self.window_heading = ttk.Entry(frame)
        self.window_heading.insert(0, 'My First Python App')
        self.window_heading.pack(fill='x')
        self.selectable_text(frame, 'Custom Python logic (called when you press Run Action):', pady=(12, 3))
        self.custom_logic = tk.Text(frame, height=12, font=('DejaVu Sans Mono', 11), undo=True,
                                    background=self.palette['editor'], foreground=self.palette['ink'],
                                    insertbackground=self.palette['gold'], selectbackground=self.palette['selection'],
                                    selectforeground='#ffffff', padx=10, pady=10)
        self.custom_logic.insert('1.0', 'print("Hello from my new application!")')
        self.custom_logic.pack(fill='both', expand=True)
        ttk.Button(frame, text='Hatch Application (Export Folder)', command=self.hatch).pack(anchor='w', pady=12)
        self.selectable_text(frame, 'The exported project contains editable main.py, a README, and a desktop launcher installer.')

    def hatch(self):
        import re
        raw_name = self.project_name.get().strip()
        safe_name = re.sub(r'[^A-Za-z0-9_-]+', '_', raw_name).strip('_')
        if not safe_name:
            messagebox.showerror('Missing name', 'Enter a project name.')
            return
        parent = filedialog.askdirectory(title='Choose where to hatch the application')
        if not parent:
            return
        target = Path(parent) / safe_name
        if target.exists():
            messagebox.showerror('Folder exists', f'This project already exists:\n{target}')
            return
        target.mkdir(parents=True)
        heading = self.window_heading.get().strip() or raw_name
        code = self.custom_logic.get('1.0', 'end-1c')
        # Add user code as a function body without generating invalid indentation.
        indented_code = '\n'.join('    ' + line if line.strip() else '' for line in code.splitlines()) or '    pass'
        source = (f'APP_VERSION = "0.1.0"\n'
                  f'import tkinter as tk\nfrom tkinter import ttk\n\n'
                  f'def custom_action():\n{indented_code}\n\n'
                  f'root = tk.Tk(className={safe_name!r})\n'
                  f'root.title({heading!r} + "  •  v" + APP_VERSION)\n'
                  f'root.geometry("650x420")\n'
                  f'ttk.Label(root, text={heading!r}, font=("Sans", 16, "bold")).pack(padx=24, pady=24)\n'
                  f'ttk.Button(root, text="Run Action", command=custom_action).pack(pady=12)\n'
                  f'root.mainloop()\n')
        (target / 'main.py').write_text(source, encoding='utf-8')
        (target / 'README.txt').write_text(f'{heading}\nRun: python3 main.py\nEdit custom_action() in main.py to add features.\n', encoding='utf-8')
        messagebox.showinfo('Egg hatched', f'New editable project created:\n{target}\n\nRun: python3 main.py')

    def guide_tab(self):
        frame = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(frame, text='How It Was Made')
        guide = tk.Text(frame, wrap='word', font=('DejaVu Sans', 11),
                        background=self.palette['paper'], foreground='#222a39',
                        selectbackground=self.palette['selection'], selectforeground='#ffffff',
                        padx=16, pady=16)
        guide.pack(fill='both', expand=True)
        guide.insert('1.0', '''PYTHONEGGS: HOW THIS UBUNTU DESKTOP APP WORKS\n\n'
'1. main.py starts Tkinter and builds a window with tabs.\n'
'2. lessons.py stores interactive teaching samples.\n'
'3. examples.py stores practical programs (including SDR readings).\n'
'4. desktopIcon.png is loaded with Tkinter iconphoto().\n'
'5. setup_launcher.py creates the Ubuntu .desktop launcher with absolute paths.\n'
'6. StartupWMClass=PythonEggs matches Tk(className="PythonEggs"), so the dock identifies one application.\n'
'7. A local Unix socket lets a second launch tell the first window to raise/focus. This prevents duplicate PythonEggs windows.\n'
'8. Ubuntu uses the installed .desktop shortcut to show the icon and active indicator (dock behavior can differ by desktop).\n\n'
'INSTALL\n'
'Place all PythonEggs files in your project folder beside desktopIcon.png.\n'
'Run: python3 setup_launcher.py\n'
'Launch PythonEggs from the Ubuntu applications menu; pin the launcher to the dock if desired.\n'
'Close any older PythonEggs process before testing a new version.\n\n'
'TO LEARN\n'
'Choose a lesson, edit real Python, and watch the inline Tkinter preview change.\n'
'TO BUILD\n'
'Use App Builder to export a new independent Python application into a folder.\n'
'You can then open that exported main.py and extend it in PyCharm or another editor.\n\n'
'NOTE\n'
'Only run code you trust: the editor executes real Python in this application. A blocking loop can freeze the window; restart if needed.\n''')
        guide.config(state='disabled')


def main():
    messages = queue.Queue()
    server = claim_instance(messages)
    if server is None:
        return
    try:
        app = PythonEggs(messages)
        app.mainloop()
    finally:
        server.close()
        SOCKET_PATH.unlink(missing_ok=True)


if __name__ == '__main__':
    main()