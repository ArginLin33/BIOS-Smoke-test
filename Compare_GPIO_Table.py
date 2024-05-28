import os
import tkinter as tk
from tkinter import filedialog, messagebox

def find_different_index(lines_a, lines_b):
    for i, (line_a, line_b) in enumerate(zip(lines_a, lines_b)):
        if line_a.strip().startswith(('Pad Name', 'Net Name', 'GPIO Tx State', 'GPIO Rx State', 'GPIO Tx Disable', 'GPIO Rx Disable', 'Pad Mode')):
            if line_a.split(':')[-1].strip() != line_b.split(':')[-1].strip():
                return i
    return None

def compare_file_pairs(folder_a, folder_b, file_names, gpio=False, pcd=False):
    differences = {}
    for file_name in file_names:
        file_a = os.path.join(folder_a, file_name)
        file_b = os.path.join(folder_b, file_name)

        if os.path.isdir(file_a) or os.path.isdir(file_b):
            continue

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
    parsed_dict = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            parsed_dict[key.strip()] = value.strip()
    return parsed_dict

def find_differences_dict(dict_a, dict_b):
    differences = []
    all_keys = set(dict_a.keys()).union(set(dict_b.keys()))
    for key in all_keys:
        value_a = dict_a.get(key, None)
        value_b = dict_b.get(key, None)
        if value_a != value_b:
            differences.append((key, value_a, value_b))
    return differences

def save_differences(differences, output_file, gpio=False, pcd=False):
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
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

def compare_generic(folder_a, folder_b, file_pattern, output_log, gpio=False, pcd=False):
    if gpio:
        folder_a = os.path.join(folder_a, 'gpio')
        folder_b = os.path.join(folder_b, 'gpio')
    
    if not os.path.isdir(folder_a):
        messagebox.showerror("Error", f"The folder {folder_a} does not exist.")
        return
    if not os.path.isdir(folder_b):
        messagebox.showerror("Error", f"The folder {folder_b} does not exist.")
        return

    file_names = [f for f in os.listdir(folder_a) if file_pattern in f and os.path.isfile(os.path.join(folder_a, f))]
    file_names = [f for f in file_names if f in os.listdir(folder_b)]
    
    differences = compare_file_pairs(folder_a, folder_b, file_names, gpio=gpio, pcd=pcd)
    
    if not differences:
        messagebox.showinfo("Result", "PASS: No differences found.")
    else:
        save_differences(differences, output_log, gpio=gpio, pcd=pcd)
        messagebox.showinfo("Result", f"Files are different. Differences saved to {output_log}.")

def compare_gpio(folder_a, folder_b):
    compare_generic(folder_a, folder_b, '', 'gpio_differences.txt', gpio=True)

def compare_brat(folder_a, folder_b):
    compare_generic(folder_a, folder_b, 'BRAT.txt', 'BRAT_differences.txt')

def check_pcd(folder_a, folder_b):
    compare_generic(folder_a, folder_b, 'PCD.txt', 'PCD_differences.txt', pcd=True)

def compare_smbios(folder_a, folder_b):
    compare_generic(folder_a, folder_b, 'SMBIOS.txt', 'SMBIOS_differences.txt')

def compare_all(folder_a, folder_b):
    compare_gpio(folder_a, folder_b)
    compare_brat(folder_a, folder_b)
    check_pcd(folder_a, folder_b)
    compare_smbios(folder_a, folder_b)

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
    main()