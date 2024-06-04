import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import subprocess
import os
import sys
import logging

# Set up logging to file and console
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("CaptureLog_debug.log"),
                              logging.StreamHandler()])

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def run_auto_smoke_test():
    """
    Function to handle the Auto Smoke Test button.
    It prompts the user to enter a BIOS version number, and then handles the process.
    """
    version = simpledialog.askstring("Input", "Enter new BIOS version (e.g., 100, 110):")
    preversion = simpledialog.askstring("Input", "Enter previous BIOS version (e.g., 110, 120):")
    if version and preversion:
        version_dir = os.path.join(os.getcwd(), version)
        preversion_dir = os.path.join(os.getcwd(), preversion)
        if not os.path.exists(version_dir):
            os.makedirs(version_dir)
            logging.debug(f"Created directory: {version_dir}")
        else:
            logging.debug(f"Directory already exists: {version_dir}")

        # Locate the batch file using resource_path
        batch_file = resource_path('CaptureLog.bat\CaptureLog.bat')
        resource_dir = resource_path('')
        logging.debug(f"Located batch file at: {batch_file}")
        logging.debug(f"Setting RESOURCEDIR to: {resource_dir}")

        # Execute the batch file, passing the version and BASEDIR as arguments
        logging.debug(f"Executing batch file for BIOS version: {version}")
        try:
            env = os.environ.copy()
            env['RESOURCEDIR'] = resource_dir
            env['BASEDIR'] = version_dir
            subprocess.run(['cmd.exe', '/c', batch_file, version], env=env, check=True)
        except Exception as e:
            logging.error(f"Unexpected error during capture log: {e}")

        # Execute the Compare_GPIO_Table.py script's compare_file_pairs function
        try:
            logging.debug("Executing comparison of GPIO tables")
            compare_all(preversion_dir, version_dir, show_message=False)
        except Exception as e:
            logging.error(f"Unexpected error during comparison: {e}")
			
        # Locate the batch file using resource_path
        batch_file = resource_path('MSS4WBCB_Error_Stop.bat\MSS4WBCB_Error_Stop.bat')


def run_compare_log():
    """
    Function to handle the Compare Log button.
    This function executes the Compare_GPIO_Table.py script.
    """
    folder_a = filedialog.askdirectory(title="Select the Previous BIOS Version Folder")
    folder_b = filedialog.askdirectory(title="Select the Formal BIOS Version Folder")
    if folder_a and folder_b:
        compare_all(folder_a, folder_b)

def capture_log():
    """
    Function to handle the Capture Log button.
    This function executes the CaptureLog.bat script.
    """
    version = simpledialog.askstring("Input", "Enter BIOS version (e.g., 100, 110):")
    if version:
        version_dir = os.path.join(os.getcwd(), version)
        if not os.path.exists(version_dir):
            os.makedirs(version_dir)
            logging.debug(f"Created directory: {version_dir}")
        else:
            logging.debug(f"Directory already exists: {version_dir}")

        # Locate the batch file using resource_path
        batch_file = resource_path('CaptureLog.bat\CaptureLog.bat')
        resource_dir = resource_path('')
        logging.debug(f"Located batch file at: {batch_file}")
        logging.debug(f"Setting RESOURCEDIR to: {resource_dir}")

        # Execute the batch file, passing the version and BASEDIR as arguments
        logging.debug(f"Executing batch file for BIOS version: {version}")
        try:
            env = os.environ.copy()
            env['RESOURCEDIR'] = resource_dir
            env['BASEDIR'] = version_dir
            subprocess.run(['cmd.exe', '/c', batch_file, version], env=env, check=True)
        except Exception as e:
            logging.error(f"Unexpected error during capture log: {e}")

def find_different_pairs(lines_a, lines_b):
    """
    Function to find the first index where lines differ between two files.
    
    Args:
    lines_a (list): List of lines from the first file.
    lines_b (list): List of lines from the second file.
    
    Returns:
    list: List of all different GPP pairs.
    """
    diff_GPP_list = []
    temp_a = []
    temp_b = []
    is_diff = False
    for (line_a, line_b) in zip(lines_a, lines_b):
        # Check if the current line starts with predefined keywords and if the content differs
        if line_a.strip().startswith(('Pad Name', 'Net Name', 'GPIO Tx State', 'GPIO Rx State', 'GPIO Tx Disable', 'GPIO Rx Disable', 'Pad Mode')):
            temp_a.append(line_a)
            temp_b.append(line_b)
            if line_a.split(':')[-1].strip() != line_b.split(':')[-1].strip():
                is_diff = True
            if line_a.strip().startswith(('Pad Mode')):
                # If two pairs different, add to diff_GPP_list
                if is_diff:
                    diff_GPP_list.append([list(temp_a), list(temp_b)])
                temp_a.clear()
                temp_b.clear()
                is_diff = False
    # Return None if the files are identical
    return diff_GPP_list

def compare_file_pairs(folder_a, folder_b, file_names):
    """
    Compare pairs of files from two folders and retrieve differences.
    
    Args:
    folder_a (str): Path to the first folder.
    folder_b (str): Path to the second folder.
    file_names (list): List of file names to compare.
    
    Returns:
    list: list containing all different GPP pairs.
    """
    differences = []
    is_diff = False
    for i in range(len(file_names)):
        file_a = os.path.join(folder_a, file_names[i])
        file_b = os.path.join(folder_b, file_names[i])
        differences.append([])

        # Read the contents of the two files
        try:
            with open(file_a, 'r', encoding='utf-8', errors='ignore') as f1, open(file_b, 'r', encoding='utf-8', errors='ignore') as f2:
                lines_a = f1.readlines()
                lines_b = f2.readlines()
        except Exception as e:
            logging.error(f"Error reading files: {file_a} or {file_b}. Error: {e}")
            continue

        # Find different GPP pairs
        diff_pairs = find_different_pairs(lines_a, lines_b)
        # Store the difference information if differences exist
        if len(diff_pairs) != 0:
            is_diff = True
            for j in diff_pairs:
                differences[i].append(j)
    if is_diff:
        return differences
    else:
        return None


def save_differences(differences, output_file, file_names, folder_a, folder_b):
    """
    Save differences to a file.
    
    Args:
    differences (list): List of differences.
    output_file (str): Path to the output file.
    """
    with open(output_file, 'w', encoding='utf-8') as diff_file:
        for file_index in range(len(differences)):
            if len(differences[file_index]) != 0:
                # Write the file name and fixed content to the output file
                diff_file.write(f"Differences in {file_names[file_index]}:\n")
                for diff_pairs in differences[file_index]:
                    diff_file.write(f"Previous BIOS Version folder   : {folder_a}\n")
                    for diff_pairs_file_a in diff_pairs[0]:
                        diff_file.write(f"{diff_pairs_file_a}")
                    diff_file.write(f"Formal BIOS Version folder     : {folder_b}\n")
                    for diff_pairs_file_b in diff_pairs[1]:
                        diff_file.write(f"{diff_pairs_file_b}")
                    diff_file.write(f"\n")

def compare_generic(folder_a, folder_b, file_pattern, output_log, gpio=False, pcd=False, show_message=True):
    """
    Generic function to compare files based on a pattern and save results.
    """
    if gpio:
        folder_a = os.path.join(folder_a, 'gpio')
        folder_b = os.path.join(folder_b, 'gpio')

    if not os.path.isdir(folder_a):
        if show_message:
            logging.error(f"The folder {folder_a} does not exist.")
        return
    if not os.path.isdir(folder_b):
        if show_message:
            logging.error(f"The folder {folder_b} does not exist.")
        return

    file_names = [f for f in os.listdir(folder_a) if file_pattern in f and os.path.isfile(os.path.join(folder_a, f))]
    file_names = [f for f in file_names if f in os.listdir(folder_b)]

    differences = compare_file_pairs(folder_a, folder_b, file_names)

    if not differences:
        if show_message:
            logging.debug("Result: PASS: No differences found.")
    else:
        save_differences(differences, output_log, file_names, folder_a, folder_b)
        if show_message:
            logging.debug(f"Result: Files are different. Differences saved to {output_log}.")

def compare_gpio(folder_a, folder_b, show_message=True):
    """
    Function to compare GPIO files.
    """
    compare_generic(folder_a, folder_b, '', 'gpio_differences.txt', gpio=True, show_message=show_message)

def compare_brat(folder_a, folder_b, show_message=True):
    """
    Function to compare BRAT files.
    """
    compare_generic(folder_a, folder_b, 'BRAT.txt', 'BRAT_differences.txt', show_message=show_message)

def check_pcd(folder_a, folder_b, show_message=True):
    """
    Function to compare PCD files.
    """
    compare_generic(folder_a, folder_b, 'Setup.txt', 'PCD_differences.txt', pcd=True, show_message=show_message)

def compare_smbios(folder_a, folder_b, show_message=True):
    """
    Function to compare SMBIOS files.
    """
    compare_generic(folder_a, folder_b, 'SMBIOS.txt', 'SMBIOS_differences.txt', show_message=show_message)

def compare_all(folder_a, folder_b, show_message=True):
    """
    Function to compare all types of files.
    """
    compare_gpio(folder_a, folder_b, show_message=show_message)
    compare_brat(folder_a, folder_b, show_message=show_message)
    check_pcd(folder_a, folder_b, show_message=show_message)
    compare_smbios(folder_a, folder_b, show_message=show_message)

# GUI setup for the initial root window
root = tk.Tk()
root.title("BIOS Smoke Test")
root.geometry("500x500")
root.resizable(False, False)

# Add version label
version_label = tk.Label(root, text="ver0.0.1")
version_label.pack(side="bottom", pady=5)

# Buttons for initiating tests
capture_log_button = tk.Button(root, text="Capture Log", command=capture_log)
capture_log_button.pack(pady=5)

auto_smoke_test_button = tk.Button(root, text="Auto Smoke Test", command=run_auto_smoke_test)
auto_smoke_test_button.pack(pady=5)

compare_log_button = tk.Button(root, text="Compare Log", command=run_compare_log)
compare_log_button.pack(pady=5)

btn_compare_all = tk.Button(root, text="Compare All", command=run_compare_log)
btn_compare_all.pack(pady=10)

root.mainloop()
