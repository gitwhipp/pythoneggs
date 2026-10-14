PythonEggs v0.1.0 — Ubuntu Python App Studio

FILES
main.py — Main desktop application, single-instance activation, app exporter
lessons.py — Python teaching modules
examples.py — Practical sample programs
setup_launcher.py — Creates the launcher at ~/.local/share/applications/pythonEggs.desktop
desktopIcon.png — Your icon; place it beside main.py (not included in ZIP)

INSTALL
1. Copy these files into your existing /webStuff/pythonEggs folder.
2. Keep your desktopIcon.png in the same folder.
3. In a terminal inside that folder run:
   python3 setup_launcher.py
4. Launch PythonEggs from Ubuntu's applications menu and pin it to the dock.
5. To run without the launcher: python3 main.py

Notes:
- Requires Python 3 and Tkinter (on Ubuntu: python3-tk).
- Single-instance app communicates over a local Unix socket and raises existing window.
- Tk(className="PythonEggs") matches StartupWMClass=PythonEggs for dock grouping.
- Runs example code locally with current user permissions; only execute code you trust.
- App Builder exports editable application source folders. It does not bundle an executable binary yet.
