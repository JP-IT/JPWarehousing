import os
import pandas as pd
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, font, Menu
import threading
import configparser
import appdirs
import ttkbootstrap as ttk

# Constants
CONFIG_DIR = appdirs.user_data_dir("DataProcessingApp", "YourName")
CONFIG_FILE = os.path.join(CONFIG_DIR, 'app_config.ini')
LOG_FILE = os.path.join(CONFIG_DIR, 'execution_log.txt')
os.makedirs(CONFIG_DIR, exist_ok=True)

config = configparser.ConfigParser()


def save_config(section, key, value):
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, key, value)
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)


def load_config(section, key, default):
    config.read(CONFIG_FILE)
    return config.get(section, key, fallback=default)


def log_message(message):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(message + '\n')


def clear_log():
    with open(LOG_FILE, 'w') as log_file:
        log_file.write('')


def on_close():
    save_config('PATHS', 'output_path', output_path.get())
    save_config('PATHS', 'processed_path', processed_path.get())
    root.destroy()


def get_client_name_from_filename(filename):
    base_name = os.path.basename(filename).upper()
    return 'VANDERBILT' if base_name.startswith('VAN') else 'SILVER POINT' if base_name.startswith('SPT') else 'UNKNOWN'


def get_store_name(item_number, filename):
    if 'VAN' in filename or 'SPT' in filename:
        return get_client_name_from_filename(filename)
    store_initials = item_number[:2]
    return {'LP': 'LIFEPRO', 'PC': 'PETCOVE', 'JB': 'JOYBERRI'}.get(store_initials, 'UNKNOWN')


def normalize_header(header):
    return header.upper()


def map_columns(df, filename):
    header_mappings = {
        'PO#': 'ORDER ID',
        'BATCH NUMBER': 'PICK LIST NUMBER',
        'SHIP_TO': 'STORE',
        'SKU': 'ITEM NUMBER',
        'EACH': 'EACH',
        'SHIP_DATE': 'DATE'
    }
    df.columns = [normalize_header(col) for col in df.columns]
    header_mappings = {normalize_header(k): normalize_header(v) for k, v in header_mappings.items()}
    df_renamed = df.rename(columns=header_mappings)
    store_name = get_client_name_from_filename(filename) if filename.upper().startswith(('VAN', 'SPT')) else \
    df_renamed['ITEM NUMBER'].apply(lambda x: get_store_name(x, filename)).iloc[0]
    df_renamed['B'] = df_renamed.get('B', store_name)
    return df_renamed, store_name


def process_file_to_csv(input_file_path, output_file_folder, processed_folder):
    log_message(f"Processing file: {input_file_path}")
    try:
        df = pd.read_excel(input_file_path) if input_file_path.endswith(('.xlsx', '.xls')) else pd.read_csv(
            input_file_path)
    except Exception as e:
        log_message(f"Error reading file {input_file_path}: {e}")
        return
    df_renamed, store_name = map_columns(df, os.path.basename(input_file_path))
    if 'DATE' in df_renamed.columns:
        df_renamed['DATE'] = pd.to_datetime(df_renamed['DATE'], errors='coerce').dt.strftime('%m/%d/%Y').fillna('')
    csv_df = pd.DataFrame({
        'A': ['BC'] * len(df_renamed),
        'B': df_renamed['B'],
        'C': df_renamed['ORDER ID'],
        'D': df_renamed['PICK LIST NUMBER'],
        'E': [''] * len(df_renamed),
        'F': df_renamed['DATE'],
        'G': [''] * len(df_renamed),
        'H': [''] * len(df_renamed),
        'I': df_renamed['STORE'],
        'J': [''] * len(df_renamed),
        'K': df_renamed.get('STREET_ADDRESS', [''] * len(df_renamed)),
        'L': [''] * len(df_renamed),
        'M': df_renamed.get('CITY', [''] * len(df_renamed)),
        'N': df_renamed.get('STATE', [''] * len(df_renamed)),
        'O': df_renamed.get('ZIP', [''] * len(df_renamed)),
        'P': [''] * len(df_renamed),
        'Q': [''] * len(df_renamed),
        'R': [''] * len(df_renamed),
        'S': [''] * len(df_renamed),
        'T': [''] * len(df_renamed),
        'U': ['D2C'] * len(df_renamed),
        'V': [''] * len(df_renamed),
        'W': [''] * len(df_renamed),
        'X': df_renamed['ITEM NUMBER'],
        'Y': df_renamed['QUANTITY'],
        'Z': [''] * len(df_renamed),
        'AA': ['EACH'] * len(df_renamed),
        'AB': [''] * len(df_renamed),
        'AC': [''] * len(df_renamed),
        'AD': [''] * len(df_renamed),
        'AE': [''] * len(df_renamed),
        'AF': [''] * len(df_renamed),
        'AG': [''] * len(df_renamed),
        'AH': [''] * len(df_renamed),
        'AI': [''] * len(df_renamed),
        'AJ': ['JPFN'] * len(df_renamed)
    })
    output_file_name = f"{df_renamed['PICK LIST NUMBER'].iloc[0]}_{store_name} - PROCESSED.csv"
    output_file_path = os.path.join(output_file_folder, output_file_name)
    try:
        csv_df.to_csv(output_file_path, index=False, header=False)
        shutil.move(input_file_path, os.path.join(processed_folder, os.path.basename(input_file_path)))
        log_message(f"Processed and moved file: {input_file_path}")
    except Exception as e:
        log_message(f"Error processing file {input_file_path}: {e}")


def start_processing():
    clear_log()
    threading.Thread(target=process_files, daemon=True).start()


def process_files():
    output_folder = output_path.get()
    processed_folder = processed_path.get()
    os.makedirs(processed_folder, exist_ok=True)
    file_paths = filedialog.askopenfilenames(filetypes=[("Excel and CSV files", "*.xlsx;*.xls;*.csv")])
    if not file_paths:
        status_label.config(text="No files selected.")
        return
    progress_step = 100 / len(file_paths)
    progress_bar['value'] = 0
    for file_path in file_paths:
        process_file_to_csv(file_path, output_folder, processed_folder)
        progress_bar['value'] += progress_step
        root.update_idletasks()
    progress_bar['value'] = 100
    status_label.config(text="Processing complete.")


def show_help():
    help_text = """
    How to Use the App:
    -------------------
    1. Set the Output Folder: Choose where you want the processed files to be saved.
    2. Set the Processed Folder: Choose where to move the original files after processing.
    3. Click 'Process Files' to select and process files.
       - You can select multiple Excel or CSV files.
    4. The progress bar shows the processing progress.
    5. 'Processing complete' will be displayed once all files are processed.
    """
    messagebox.showinfo("Help - How to Use", help_text)


def show_logs():
    with open(LOG_FILE, 'r') as log_file:
        logs = log_file.read()
    log_window = tk.Toplevel(root)
    log_window.title("Execution Logs")
    log_text = tk.Text(log_window, wrap='word', width=100, height=30)
    log_text.insert(tk.END, logs)
    log_text.config(state=tk.DISABLED)
    log_text.pack(expand=True, fill=tk.BOTH)


def browse_folder(entry_field):
    directory = filedialog.askdirectory()
    if directory:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, directory)
        save_config('PATHS', entry_field.winfo_name(), directory)


def parse_color_profile(profile_str):
    return dict(item.split(':') for item in profile_str.split(';'))


def load_color_profiles():
    return {key: parse_color_profile(config.get('COLOR_PROFILES', key)) for key in config.options('COLOR_PROFILES')}


def save_color_profile(profile_name):
    save_config('SETTINGS', 'color_profile', profile_name)


def load_saved_color_profile():
    return load_config('SETTINGS', 'color_profile', 'Default')


def apply_color_profile(profile):
    style = ttk.Style()
    style.configure('TButton', background=profile['button_bg_color'], foreground=profile['button_fg_color'])
    style.configure('TLabel', background=profile['label_bg_color'], foreground=profile['label_fg_color'])
    style.configure('TEntry', fieldbackground=profile['entry_bg_color'], foreground=profile['entry_fg_color'])
    style.configure('TProgressbar', background=profile['label_bg_color'], foreground=profile['label_fg_color'])
    style.configure('TFrame', background=profile['bg_color'])

    root.configure(bg=profile['bg_color'])  # Apply background color to the main window

    for widget in root.winfo_children():
        widget_class = widget.winfo_class()
        if widget_class in ['TButton', 'TLabel', 'TEntry', 'TProgressbar', 'TFrame']:
            widget.config(style=widget_class)
        elif widget_class == 'Frame':  # For non-ttk Frame widgets
            widget.config(bg=profile['bg_color'])


def set_color_profile(profile_name):
    profiles = load_color_profiles()
    if profile_name in profiles:
        apply_color_profile(profiles[profile_name])
        save_color_profile(profile_name)


def create_ui():
    global root, output_path, processed_path, progress_bar, status_label

    root = ttk.Window(themename="litera")
    root.title("File Processor")

    style = ttk.Style()
    theme = 'litera'
    if theme not in style.theme_names():
        theme = 'flatly'
    style.theme_use(theme)

    custom_font = font.nametofont("TkDefaultFont")
    custom_font.configure(size=10)
    root.option_add("*Font", custom_font)

    menu_bar = Menu(root)
    root.config(menu=menu_bar)

    file_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Execution Logs", command=show_logs)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)

    color_menu = Menu(file_menu, tearoff=0)
    for profile_name in load_color_profiles().keys():
        color_menu.add_command(label=profile_name, command=lambda name=profile_name: set_color_profile(name))
    file_menu.add_cascade(label="Color Profile", menu=color_menu)

    ttk.Button(root, text='Process Files', command=start_processing, bootstyle="secondary-outline").grid(row=0,
                                                                                                         column=0,
                                                                                                         padx=10,
                                                                                                         pady=10)

    ttk.Label(root, text="Output Folder", bootstyle="secondary").grid(row=1, column=0, padx=10, pady=10)
    output_path = ttk.Entry(root, width=50, name='output_path')
    output_path.grid(row=1, column=1, padx=10, pady=10)
    output_path.insert(0, load_config('PATHS', 'output_path', "Default/Output/Folder/Path"))
    ttk.Button(root, text="Browse", command=lambda: browse_folder(output_path), bootstyle="secondary-outline").grid(
        row=1, column=2, padx=10, pady=10)

    ttk.Label(root, text="Processed Folder", bootstyle="secondary").grid(row=2, column=0, padx=10, pady=10)
    processed_path = ttk.Entry(root, width=50, name='processed_path')
    processed_path.grid(row=2, column=1, padx=10, pady=10)
    processed_path.insert(0, load_config('PATHS', 'processed_path', "Default/Processed/Folder/Path"))
    ttk.Button(root, text="Browse", command=lambda: browse_folder(processed_path), bootstyle="secondary-outline").grid(
        row=2, column=2, padx=10, pady=10)

    progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
    progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky=(tk.W + tk.E))

    status_label = ttk.Label(root, text="Select files and start processing", bootstyle="secondary")
    status_label.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky=(tk.W + tk.E))


def main():
    config.read(CONFIG_FILE)
    if not config.has_section('COLOR_PROFILES'):
        config['COLOR_PROFILES'] = {
            'Default': 'bg_color:#F0F0F0;button_bg_color:#D1D1D1;button_fg_color:black;label_bg_color:#F0F0F0;label_fg_color:black;entry_bg_color:white;entry_fg_color:black',
            'Red/Grey': 'bg_color:#767676;button_bg_color:#d0d0d0;button_fg_color:#d30000;label_bg_color:#b6b6b6;label_fg_color:black;entry_bg_color:#dcdcdc;entry_fg_color:#ff0000'
        }
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)

    create_ui()
    root.protocol("WM_DELETE_WINDOW", on_close)

    # Apply the saved color profile after creating the UI
    saved_profile_name = load_saved_color_profile()
    set_color_profile(saved_profile_name)

    root.mainloop()


if __name__ == "__main__":
    main()
