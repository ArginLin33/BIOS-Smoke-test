import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def find_different_pairs(lines_a, lines_b):
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
        with open(file_a, 'r', encoding='utf-8') as f1, open(file_b, 'r', encoding='utf-8') as f2:
            lines_a = f1.readlines()
            lines_b = f2.readlines()

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

def save_differences(differences, output_file):
    """
    Save differences to a file.
    
    Args:
    differences (list): List of differences.
    output_file (str): Path to the output file.
    """
    with open(output_file, 'w', encoding='utf-8') as diff_file:
        for i in range(len(differences)):
            if len(differences[i]) != 0:
                # Write the file name and fixed content to the output file
                diff_file.write(f"Differences in {file_names[i]}:\n")
                for j in differences[i]:
                    diff_file.write(f"Previous BIOS Version folder   : {folder_a}\n")
                    for k in range(len(j[0])):
                        diff_file.write(f"{j[0][k]}")
                    diff_file.write(f"Formal BIOS Version folder     : {folder_b}\n")
                    for k in range(len(j[1])):
                        diff_file.write(f"{j[1][k]}")
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
            messagebox.showerror("Error", f"The folder {folder_a} does not exist.")
        return
    if not os.path.isdir(folder_b):
        if show_message:
            messagebox.showerror("Error", f"The folder {folder_b} does not exist.")
        return

    file_names = [f for f in os.listdir(folder_a) if file_pattern in f and os.path.isfile(os.path.join(folder_a, f))]
    file_names = [f for f in file_names if f in os.listdir(folder_b)]

    differences = compare_file_pairs(folder_a, folder_b, file_names)

    if not differences:
        if show_message:
            messagebox.showinfo("Result", "PASS: No differences found.")
    else:
        save_differences(differences, output_log)
        if show_message:
            messagebox.showinfo("Result", f"Files are different. Differences saved to {output_log}.")

def compare_gpio
(folder_a, folder_b, show_message=True):
    compare_generic(folder_a, folder_b, '', 'gpio_differences.txt', gpio=True, show_message=show_message)

def compare_brat(folder_a, folder_b, show_message=True):
    compare_generic(folder_a, folder_b, 'BRAT.txt', 'BRAT_differences.txt', show_message=show_message)

def check_pcd(folder_a, folder_b, show_message=True):
    compare_generic(folder_a, folder_b, 'PCD.txt', 'PCD_differences.txt', pcd=True, show_message=show_message)

def compare_smbios(folder_a, folder_b, show_message=True):
    compare_generic(folder_a, folder_b, 'SMBIOS.txt', 'SMBIOS_differences.txt', show_message=show_message)

def compare_all(folder_a, folder_b, show_message=True):
    compare_gpio(folder_a, folder_b, show_message=show_message)
    compare_brat(folder_a, folder_b, show_message=show_message)
    check_pcd(folder_a, folder_b, show_message=show_message)
    compare_smbios(folder_a, folder_b, show_message=show_message)

def main():
    root = tk.Tk()
    root.title("BIOS Tools")

    def select_folders_and_compare_all():
        folder_a = filedialog.askdirectory(title="Select the Previous BIOS Version Folder")
        folder_b = filedialog.askdirectory(title="Select the Formal BIOS Version Folder")
        if folder_a and folder_b:
            compare_all(folder_a, folder_b)

    def select_folders_and_compare_gpio():
        folder_a = filedialog.askdirectory(title="Select the Previous BIOS Version Folder")
        folder_b = filedialog.askdirectory(title="Select the Formal BIOS Version Folder")
        if folder_a and folder_b:
            compare_gpio(folder_a, folder_b)

    def select_folders_and_compare_brat():
        folder_a = filedialog.askdirectory(title="Select the Previous BIOS Version Folder")
        folder_b = filedialog.askdirectory(title="Select the Formal BIOS Version Folder")
        if folder_a and folder_b:
            compare_brat(folder_a, folder_b)

    def select_folders_and_check_pcd():
        folder_a = filedialog.askdirectory(title="Select the Previous BIOS Version Folder")
        folder_b = filedialog.askdirectory(title="Select the Formal BIOS Version Folder")
        if folder_a and folder_b:
            check_pcd(folder_a, folder_b)

    def select_folders_and_compare_smbios():
        folder_a = filedialog.askdirectory(title="Select the Previous BIOS Version Folder")
        folder_b = filedialog.askdirectory(title="Select the Formal BIOS Version Folder")
        if folder_a and folder_b:
            compare_smbios(folder_a, folder_b)

    btn_compare_all = tk.Button(root, text="Compare All", command=select_folders_and_compare_all)
    btn_compare_gpio = tk.Button(root, text="Compare GPIO", command=select_folders_and_compare_gpio)
    btn_compare_brat = tk.Button(root, text="Compare BRAT", command=select_folders_and_compare_brat)
    btn_check_pcd = tk.Button(root, text="PCD Check", command=select_folders_and_check_pcd)
    btn_compare_smbios = tk.Button(root, text="Compare SMBIOS", command=select_folders_and_compare_smbios)
    btn_exit = tk.Button(root, text="Exit", command=root.quit)
    
    btn_compare_all.pack(pady=10)
    btn_compare_gpio.pack(pady=10)
    btn_compare_brat.pack(pady=10)
    btn_check_pcd.pack(pady=10)
    btn_compare_smbios.pack(pady=10)
    btn_exit.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "compare_all":
        if len(sys.argv) != 4:
            print("Usage: Compare_GPIO_Table.py compare_all <folder_a> <folder_b>")
            sys.exit(1)
        folder_a, folder_b = sys.argv[2], sys.argv[3]
        compare_all(folder_a, folder_b, show_message=False)
    else:
        main()
