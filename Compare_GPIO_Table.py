import os
import tkinter as tk
from tkinter import filedialog, messagebox

def find_different_index(lines_a, lines_b):
    """
    Find the index of the first line that differs between two lists of lines.
    
    Args:
    lines_a (list): List of lines from the first file.
    lines_b (list): List of lines from the second file.
    
    Returns:
    int or None: Index of the first differing line, or None if the files are identical.
    """
    for i, (line_a, line_b) in enumerate(zip(lines_a, lines_b)):
        if line_a.strip().startswith(('Pad Name', 'Net Name', 'GPIO Tx State', 'GPIO Rx State', 'GPIO Tx Disable', 'GPIO Rx Disable', 'Pad Mode')):
            if line_a.split(':')[-1].strip() != line_b.split(':')[-1].strip():
                return i
    return None

def compare_file_pairs(folder_a, folder_b, file_names, gpio=False, pcd=False):
    """
    Compare pairs of files from two folders and retrieve differences.
    
    Args:
    folder_a (str): Path to the first folder.
    folder_b (str): Path to the second folder.
    file_names (list): List of file names to compare.
    gpio (bool): Whether to use GPIO specific comparison logic.
    pcd (bool): Whether to use PCD specific comparison logic.
    
    Returns:
    dict: Dictionary containing file names as keys and difference information as values.
    """
    differences = {}
    for file_name in file_names:
        file_a = os.path.join(folder_a, file_name)
        file_b = os.path.join(folder_b, file_name)

        with open(file_a, 'r', encoding='utf-8') as f1, open(file_b, 'r', encoding='utf-8') as f2:
            lines_a = f1.readlines()
            lines_b = f2.readlines()

        if gpio:
            diff_index = find_different_index(lines_a, lines_b)
            if diff_index is not None:
                differences[file_name] = {'diff_index': diff_index, 'lines_a': lines_a, 'lines_b': lines_b}
        elif pcd:
            dict_a = parse_lines(lines_a)
            dict_b = parse_lines(lines_b)
            file_differences = find_differences_dict(dict_a, dict_b)
            if file_differences:
                differences[file_name] = file_differences
        else:
            if lines_a != lines_b:
                differences[file_name] = {'lines_a': lines_a, 'lines_b': lines_b}

    return differences

def parse_lines(lines):
    """
    Parse lines into a dictionary with the text before the colon as keys
    and text after the colon as values.
    
    Args:
    lines (list): List of lines to parse.
    
    Returns:
    dict: Dictionary with parsed lines.
    """
    parsed_dict = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            parsed_dict[key.strip()] = value.strip()
    return parsed_dict

def find_differences_dict(dict_a, dict_b):
    """
    Find differences between two dictionaries.
    
    Args:
    dict_a (dict): First dictionary to compare.
    dict_b (dict): Second dictionary to compare.
    
    Returns:
    list: List of tuples with differing key-value pairs.
    """
    differences = []
    all_keys = set(dict_a.keys()).union(set(dict_b.keys()))
    for key in all_keys:
        value_a = dict_a.get(key, None)
        value_b = dict_b.get(key, None)
        if value_a != value_b:
            differences.append((key, value_a, value_b))
    return differences

def save_differences(differences, output_file, gpio=False, pcd=False):
    """
    Save differences to a file.
    
    Args:
    differences (dict): Dictionary containing file names as keys and difference information as values.
    output_file (str): Path to the output file where differences will be saved.
    gpio (bool): Whether to use GPIO specific save logic.
    pcd (bool): Whether to use PCD specific save logic.
    """
    with open(output_file, 'w', encoding='utf-8') as diff_file:
        for file_name, diff_info in differences.items():
            diff_file.write(f"Differences in {file_name}:\n")
            if gpio:
                diff_index = diff_info['diff_index']
                lines_a = diff_info['lines_a']
                lines_b = diff_info['lines_b']
                
                for i in range(max(0, diff_index-4), diff_index):
                    line = lines_a[i].strip()
                    if line.split(':')[0].strip() in ('Pad Name', 'Net Name', 'GPIO Tx State', 'GPIO Rx State', 'GPIO Tx Disable', 'GPIO Rx Disable', 'Pad Mode'):
                        diff_file.write(line + '\n')
                
                for line in lines_a[diff_index:diff_index+7]:
                    if line.strip().startswith(('Pad Name', 'Net Name', 'GPIO Tx State', 'GPIO Rx State', 'GPIO Tx Disable', 'GPIO Rx Disable', 'Pad Mode')):
                        diff_file.write(line)
                
                for i in range(diff_index+7, min(diff_index+11, len(lines_a))):
                    line = lines_a[i].strip()
                    if line.split(':')[0].strip() in ('Pad Name', 'Net Name', 'GPIO Tx State', 'GPIO Rx State', 'GPIO Tx Disable', 'GPIO Rx Disable', 'Pad Mode'):
                        diff_file.write(line + '\n')
                
            elif pcd:
                for key, value_a, value_b in diff_info:
                    if value_a is not None:
                        diff_file.write(f"- {key}: {value_a}\n")
                    if value_b is not None:
                        diff_file.write(f"+ {key}: {value_b}\n")
            else:
                lines_a = diff_info['lines_a']
                lines_b = diff_info['lines_b']
                for line in lines_a:
                    if line not in lines_b:
                        diff_file.write(f"- {line}")
                for line in lines_b:
                    if line not in lines_a:
                        diff_file.write(f"+ {line}")
            diff_file.write('\n')
    print(f"Differences saved to {output_file}")

def compare_generic(file_pattern, output_log, gpio=False, pcd=False):
    folder_a = filedialog.askdirectory(title="Select the Previous BIOS Version Folder")
    folder_b = filedialog.askdirectory(title="Select the Formal BIOS Version Folder")
    
    if not os.path.isdir(folder_a):
        messagebox.showerror("Error", f"The folder {folder_a} does not exist.")
        return
    if not os.path.isdir(folder_b):
        messagebox.showerror("Error", f"The folder {folder_b} does not exist.")
        return

    file_names = [f for f in os.listdir(folder_a) if file_pattern in f]
    file_names = [f for f in file_names if f in os.listdir(folder_b)]
    
    differences = compare_file_pairs(folder_a, folder_b, file_names, gpio=gpio, pcd=pcd)
    
    if not differences:
        messagebox.showinfo("Result", "PASS: No differences found.")
    else:
        save_differences(differences, output_log, gpio=gpio, pcd=pcd)
        messagebox.showinfo("Result", f"Files are different. Differences saved to {output_log}.")

def compare_gpio():
    compare_generic('', 'differences.txt', gpio=True)

def compare_brat():
    compare_generic('BRAT.txt', 'BRAT_differences.txt')

def check_pcd():
    compare_generic('PCD.txt', 'PCD_differences.txt', pcd=True)

def compare_smbios():
    compare_generic('SMBIOS.txt', 'SMBIOS_differences.txt')

def main():
    root = tk.Tk()
    root.title("BIOS Tools")
    
    btn_compare_gpio = tk.Button(root, text="Compare GPIO", command=compare_gpio)
    btn_compare_brat = tk.Button(root, text="Compare BRAT", command=compare_brat)
    btn_check_pcd = tk.Button(root, text="PCD Check", command=check_pcd)
    btn_compare_smbios = tk.Button(root, text="Compare SMBIOS", command=compare_smbios)
    
    btn_compare_gpio.pack(pady=10)
    btn_compare_brat.pack(pady=10)
    btn_check_pcd.pack(pady=10)
    btn_compare_smbios.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()