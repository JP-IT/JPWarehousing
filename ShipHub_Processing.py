import os
import pandas as pd
from datetime import datetime
from shutil import move
from tkinter import filedialog, Tk, Label, Button, Entry, StringVar
import json

# Configuration file path
config_file_path = "path_config.json"


def process_excel_files(input_dir, processed_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    all_headers = [
        "Batch Order", "Order ID", "Package Reference", "From Company", "From Name",
        "From Address 1", "From Address 2", "From City", "From State", "From Postal",
        "From Country", "From Phone", "From Email", "From Notify On Shipment",
        "From Notify On Exception", "From Notify On Delivery", "To Company", "To Name",
        "To Address 1", "To Address 2", "To Address 3", "To City", "To State", "To Postal",
        "To Country", "To Phone", "To Email", "To Notify On Shipment", "To Notify On Exception",
        "To Notify On Delivery", "Signature", "Saturday Delivery", "Reference 1", "Reference 2",
        "Provider", "Package Type", "Service", "Bill To", "3rd Party ACC Num",
        "3rd Party Postal Code", "3rd Party Country Code", "Package Weight LB",
        "Package Length", "Package Width", "Package Height", "Package Insured Value", "Can be merged"
    ]

    for file_name in os.listdir(input_dir):
        if file_name.endswith('.xlsx'):
            input_file_path = os.path.join(input_dir, file_name)
            processed_file_path = os.path.join(processed_dir, file_name)
            df = pd.read_excel(input_file_path)

            output_df = pd.DataFrame(columns=all_headers)
            column_mapping = {
                'Cust Po': ['Reference 2', 'Order ID'],
                'Cust Name': 'To Name',
                'Cust Address1': 'To Address 1',
                'Cust Address2': 'To Address 2',
                'Cust City': 'To City',
                'Cust State': 'To State',
                'Cust Zip Code': 'To Postal',
                'Cust Country': 'To Country',
                'Our Style': 'Reference 1'
            }

            for input_col, output_cols in column_mapping.items():
                if isinstance(output_cols, list):
                    for output_col in output_cols:
                        output_df[output_col] = df[input_col] if input_col in df else None
                else:
                    output_df[output_cols] = df[input_col] if input_col in df else None

            constant_data = {
                'From Company': 'JP Warehousing',
                'From Name': 'Jennifer Rhodes',
                'From Address 1': '13310 Valley blvd',
                'From City': 'Fontana',
                'From State': 'CA',
                'From Postal': '92335',
                'From Country': 'US',
                'From Phone': '9094195595',
                'From Email': 'Jennifer@jpwarehousing.com',
                'To Company': 'B2C',
                'To Phone': '877-370-4580',
                'To Email': 'support@ihomeclean.com',
                'Provider': 'Fedex',
                'Package Type': 'YOUR_PACKAGING',
                'Service': 'GROUND_HOME_DELIVERY',
                'Bill To': 'Sender',
                'Package Weight LB': '1'
            }

            for col, value in constant_data.items():
                output_df[col] = value

            output_df = output_df.reindex(columns=all_headers).fillna('')

            # Mark 'Reference 1' as 'Multiple' where 'Reference 2' has duplicates
            duplicate_mask = output_df['Reference 2'].duplicated(keep=False)
            output_df.loc[duplicate_mask, 'Reference 1'] = 'Multiple'
            output_df = output_df.drop_duplicates(subset=['Reference 2'], keep='first')

            name = df['Name'].iloc[0] if 'Name' in df else 'Unknown'
            current_date = datetime.now().strftime('%Y-%m-%d')
            output_file_name = f'Bulk Upload - {current_date} - {name}.csv'
            output_file_path = os.path.join(output_dir, output_file_name)

            output_df.to_csv(output_file_path, index=False)
            move(input_file_path, processed_file_path)


# Configuration management
def save_config(config, file_path):
    with open(file_path, 'w') as f:
        json.dump(config, f)


def load_config(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        return {}


def update_gui_paths(config):
    if 'input_dir' in config:
        input_dir.set(config['input_dir'])
    if 'processed_dir' in config:
        processed_dir.set(config['processed_dir'])
    if 'output_dir' in config:
        output_dir.set(config['output_dir'])


def browse_path(path_var):
    directory = filedialog.askdirectory()
    if directory:
        path_var.set(directory)
        config = {
            'input_dir': input_dir.get(),
            'processed_dir': processed_dir.get(),
            'output_dir': output_dir.get()
        }
        save_config(config, config_file_path)


def execute_script():
    process_excel_files(input_dir.get(), processed_dir.get(), output_dir.get())


def on_close():
    config = {
        'input_dir': input_dir.get(),
        'processed_dir': processed_dir.get(),
        'output_dir': output_dir.get()
    }
    save_config(config, config_file_path)
    root.destroy()


root = Tk()
root.title("Excel File Processor")

input_dir = StringVar()
processed_dir = StringVar()
output_dir = StringVar()

Label(root, text="Input Directory:").grid(row=0, column=0)
Entry(root, textvariable=input_dir).grid(row=0, column=1)
Button(root, text="Browse", command=lambda: browse_path(input_dir)).grid(row=0, column=2)

Label(root, text="Processed Directory:").grid(row=1, column=0)
Entry(root, textvariable=processed_dir).grid(row=1, column=1)
Button(root, text="Browse", command=lambda: browse_path(processed_dir)).grid(row=1, column=2)

Label(root, text="Output Directory:").grid(row=2, column=0)
Entry(root, textvariable=output_dir).grid(row=2, column=1)
Button(root, text="Browse", command=lambda: browse_path(output_dir)).grid(row=2, column=2)

Button(root, text="Process Files", command=execute_script).grid(row=3, columnspan=3)

# Load existing configuration at startup
config = load_config(config_file_path)
update_gui_paths(config)

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
