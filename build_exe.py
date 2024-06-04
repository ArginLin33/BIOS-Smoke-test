import subprocess
import sys
import os
import shutil
import stat

def install_pyinstaller():
    """Install PyInstaller if it's not already installed."""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def gather_all_files(directory):
    """Gather all files in the directory recursively."""
    all_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, directory)
            all_files.append((full_path, relative_path))
    return all_files

def create_spec_file(entry_script, all_files, output_spec, include_debug):
    """Create a PyInstaller spec file for the project."""
    with open(output_spec, 'w', encoding='utf-8') as f:
        f.write(f"# -*- mode: python ; coding: utf-8 -*-\n")
        f.write(f"block_cipher = None\n\n")
        f.write(f"a = Analysis([r'{entry_script}'],\n")
        f.write(f"             pathex=['.'],\n")
        f.write(f"             binaries=[],\n")
        f.write(f"             datas=[\n")
        for full_path, relative_path in all_files:
            f.write(f"                 (r'{full_path}', r'{relative_path}'),\n")
        f.write(f"             ],\n")
        f.write(f"             hiddenimports=[],\n")
        f.write(f"             hookspath=[],\n")
        f.write(f"             runtime_hooks=[],\n")
        f.write(f"             excludes=[],\n")
        f.write(f"             win_no_prefer_redirects=False,\n")
        f.write(f"             win_private_assemblies=False,\n")
        f.write(f"             cipher=block_cipher,\n")
        f.write(f"             noarchive=False)\n")
        f.write(f"pyz = PYZ(a.pure, a.zipped_data,\n")
        f.write(f"             cipher=block_cipher)\n")
        f.write(f"exe = EXE(pyz,\n")
        f.write(f"          a.scripts,\n")
        f.write(f"          a.binaries,\n")
        f.write(f"          a.zipfiles,\n")
        f.write(f"          a.datas,\n")
        f.write(f"          [],\n")
        f.write(f"          name='{os.path.splitext(os.path.basename(entry_script))[0]}',\n")
        f.write(f"          debug={'True' if include_debug else 'False'},\n")
        f.write(f"          bootloader_ignore_signals=False,\n")
        f.write(f"          strip=False,\n")
        f.write(f"          upx=True,\n")
        f.write(f"          upx_exclude=[],\n")
        f.write(f"          runtime_tmpdir=None,\n")
        f.write(f"          console={'True' if include_debug else 'False'})\n")

def handle_remove_readonly(func, path, exc):
    """Clear the readonly bit and reattempt the removal."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clean_build_directories():
    """Clean the build and dist directories."""
    for directory in ['build', 'dist']:
        if os.path.exists(directory):
            shutil.rmtree(directory, onerror=handle_remove_readonly)
            print(f"Removed directory: {directory}")

def build_exe(clean=False, rel=False):
    """Build the executable using PyInstaller."""
    project_folder = os.path.dirname(os.path.abspath(__file__))
    entry_script = os.path.join(project_folder, 'CaptureLog.py')
    spec_file = os.path.join(project_folder, 'build_exe.spec')

    if clean:
        clean_build_directories()
        print("Build directories cleaned.")
        return

    all_files = gather_all_files(project_folder)
    
    if not rel:
        print("Files to be included in the package:")
        for full_path, relative_path in all_files:
            print(f"Full path: {full_path}, Relative path: {relative_path}")

    create_spec_file(entry_script, all_files, spec_file, include_debug=not rel)

    pyinstaller_command = [
        'pyinstaller',
        '--clean',  # Clean PyInstaller cache and remove temporary files before building
        '--log-level=WARN',  # Ignore warnings
        spec_file
    ]

    print("Running PyInstaller...")
    result = subprocess.run(pyinstaller_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)

    if result.returncode != 0:
        print("PyInstaller encountered an error:")
        print(result.stderr)
    else:
        print("PyInstaller completed successfully.")
        if not rel:
            debug_exe_path = os.path.join(project_folder, 'dist', os.path.splitext(os.path.basename(entry_script))[0] + '.exe')
            print("Running the debug executable with PowerShell...")
            subprocess.run(['powershell', '-Command', debug_exe_path])

if __name__ == "__main__":
    install_pyinstaller()
    clean = '--cleanall' in sys.argv
    rel = '--rel' in sys.argv
    build_exe(clean, rel)
