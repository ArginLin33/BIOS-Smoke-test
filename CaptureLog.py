import tkinter as tk
from tkinter import simpledialog, Label, messagebox
import subprocess
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
    # Prompt for BIOS version
def run_capture_log():
    version = simpledialog.askstring("Input", "Enter BIOS version (e.g., 100, 110):", parent=root)
    if not version:
        messagebox.showwarning("Input", "BIOS version is required!")
        return

    # Create a directory for the BIOS version if it doesn't exist
    version_dir = os.path.join(os.getcwd(), version)
    if not os.path.exists(version_dir):
        os.makedirs(version_dir)
        print(f"Created directory: {version_dir}")
    else:
        print(f"Directory already exists: {version_dir}")
    
    # Execute the batch file, passing the version as an argument
    print(f"Executing batch file for BIOS version: {version}")
    batch_file = resource_path('CaptureLog.bat')
    subprocess.run(['cmd', '/c', batch_file, version])
    # Echo completion message
    print("Capture log already done.")
    messagebox.showinfo("Result", "Capture log already done.")

def run_auto_smoke_test():
    """
    Function to handle the Auto Smoke Test button.
    It prompts the user to enter BIOS and compare version numbers, and then handles the process.
    """
    # Prompt for BIOS version
    version = simpledialog.askstring("Input", "Enter BIOS version (e.g., 100, 110):", parent=root)
    if not version:
        messagebox.showwarning("Input", "BIOS version is required!")
        return

    # Prompt for Previous BIOS version folder
    folder_a = simpledialog.askstring("Input", "Enter the path for Previous BIOS Version Folder:", parent=root)
    if not folder_a or not os.path.isdir(folder_a):
        messagebox.showwarning("Input", "A valid path for Previous BIOS Version Folder is required!")
        return

    # Create a directory for the BIOS version if it doesn't exist
    version_dir = os.path.join(os.getcwd(), version)
    if not os.path.exists(version_dir):
        os.makedirs(version_dir)
        print(f"Created directory: {version_dir}")
    else:
        print(f"Directory already exists: {version_dir}")
    
    # Execute the batch file, passing the version as an argument
    print(f"Executing batch file for BIOS version: {version}")
    batch_file = resource_path('CaptureLog.bat')
    subprocess.run(['cmd', '/c', batch_file, version])
    # Execute Compare_GPIO_Table.py's compare_all function
    print(f"Executing Compare_GPIO_Table.py's compare_all function for BIOS version: {version}")
    subprocess.run(['python', resource_path('Compare_GPIO_Table.py'), 'compare_all', folder_a, version_dir])
    # Execute MSS4WBCB_Error_Stop.bat
    print(f"Executing MSS4WBCB_Error_Stop.bat after compare_all")
    stop_batch_file = resource_path('MSS4WBCB_Error_Stop.bat')
    subprocess.run(['cmd', '/c', stop_batch_file])

def run_compare_log():
    """
    Function to handle the Compare Log button.
    This function executes Compare_GPIO_Table.py with different functions and changes the UI.
    """
    def compare_gpio():
        print("Executing Compare_GPIO_Table.py's compare_gpio function")
        subprocess.run(['python', resource_path('Compare_GPIO_Table.py'), 'compare_gpio'])

    def compare_brat():
        print("Executing Compare_GPIO_Table.py's compare_brat function")
        subprocess.run(['python', resource_path('Compare_GPIO_Table.py'), 'compare_brat'])

    def check_pcd():
        print("Executing Compare_GPIO_Table.py's check_pcd function")
        subprocess.run(['python', resource_path('Compare_GPIO_Table.py'), 'check_pcd'])

    def compare_smbios():
        print("Executing Compare_GPIO_Table.py's compare_smbios function")
        subprocess.run(['python', resource_path('Compare_GPIO_Table.py'), 'compare_smbios'])

    # Change UI to display new buttons
    for widget in root.winfo_children():
        widget.destroy()

    compare_gpio_button = tk.Button(root, text="Compare GPIO", command=compare_gpio)
    compare_gpio_button.pack(pady=5)

    compare_brat_button = tk.Button(root, text="Compare BRAT", command=compare_brat)
    compare_brat_button.pack(pady=5)

    check_pcd_button = tk.Button(root, text="PCD Check", command=check_pcd)
    check_pcd_button.pack(pady=5)

    compare_smbios_button = tk.Button(root, text="Compare SMBIOS", command=compare_smbios)
    compare_smbios_button.pack(pady=5)

def create_ui():
    """
    Function to create the initial UI with three buttons: Capture Log, Auto Smoke Test, and Compare Log.
    """
    global root
    root = tk.Tk()
    root.title("BIOS Smoke test")
    root.geometry("500x500")
    root.resizable(False, False)
    version_label = Label(root, text="ver0.0.1")
    version_label.pack(side='bottom', anchor='w')

    capture_log_button = tk.Button(root, text="Capture Log", command=run_capture_log)
    capture_log_button.pack(pady=20)

    auto_smoke_test_button = tk.Button(root, text="Auto Smoke Test", command=run_auto_smoke_test)
    auto_smoke_test_button.pack(pady=20)

    compare_log_button = tk.Button(root, text="Compare Log", command=run_compare_log)
    compare_log_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_ui()
