"""Install the PythonEggs desktop launcher to the current Ubuntu user's menu."""
from pathlib import Path
import shlex
import sys

folder = Path(__file__).resolve().parent
application_dir = Path.home() / '.local/share/applications'
application_dir.mkdir(parents=True, exist_ok=True)
launcher = application_dir / 'pythonEggs.desktop'
icon = folder / 'desktopIcon.png'
if not icon.exists():
    raise SystemExit(f'Missing icon: {icon}')

launcher.write_text(f'''[Desktop Entry]
Type=Application
Name=PythonEggs
Comment=Learn Python and build standalone desktop applications
Exec={shlex.quote(sys.executable)} {shlex.quote(str(folder / 'main.py'))}
Path={folder}
Icon={icon}
Terminal=false
StartupNotify=true
StartupWMClass=PythonEggs
Categories=Development;Education;
''', encoding='utf-8')
launcher.chmod(0o755)
print(f'Installed launcher: {launcher}')
print('Open PythonEggs in the applications menu and pin it to the dock.')
