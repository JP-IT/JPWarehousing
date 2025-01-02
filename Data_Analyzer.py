import tkinter as tk
from tkinter import filedialog, scrolledtext
import os
import fitz  # PyMuPDF
from openpyxl import Workbook
import logging

# Setup logging
logging.basicConfig(filename='process_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extract_data(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        data = []
        temp_labels = []
        for page in doc:
            text = page.get_text()
            if "LP-" in text:
                skus = [line.strip() for line in text.split('\n') if line.startswith("LP-")]
                for i in range(len(temp_labels)):
                    if i < len(skus):
                        data[temp_labels[i]] = skus[i]
                    else:
                        data[temp_labels[i]] = "SKU Missing"
                data.append("Packing List")
                temp_labels.clear()
            else:
                temp_labels.append(len(data))
                data.append("Tracking Label Placeholder")
        return data
    except Exception as e:
        logging.error(f"Failed to process PDF {pdf_path}: {str(e)}")
        raise


def create_spreadsheet(data, output_path):
    try:
        wb = Workbook()
        ws = wb.active
        for idx, entry in enumerate(data, start=1):
            ws[f'A{idx}'] = entry
        wb.save(output_path)
    except Exception as e:
        logging.error(f"Failed to create spreadsheet {output_path}: {str(e)}")
        raise


def process_pdfs(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    pdf_files = [f for f in os.listdir(input_directory) if f.lower().endswith('.pdf')]
    if not pdf_files:
        raise FileNotFoundError("No PDF files found in the selected directory.")

    for filename in pdf_files:
        pdf_path = os.path.join(input_directory, filename)
        output_filename = '{}_Processed.xlsx'.format(os.path.splitext(filename)[0])
        output_path = os.path.join(output_directory, output_filename)
        try:
            data = extract_data(pdf_path)
            create_spreadsheet(data, output_path)
            logging.info(f"Processed {filename} successfully.")
        except Exception as e:
            update_log(f"Error: {str(e)}")


# GUI Functions
def select_input_path():
    path = filedialog.askdirectory()
    input_path_var.set(path)


def select_output_path():
    path = filedialog.askdirectory()
    output_path_var.set(path)


def run_processing():
    input_path = input_path_var.get()
    output_path = output_path_var.get()
    try:
        process_pdfs(input_path, output_path)
        update_log("Processing Complete!")
    except FileNotFoundError as fe:
        update_log(str(fe))
    except Exception as e:
        update_log(f"Processing failed: {str(e)}")


def update_log(message):
    log_text.config(state='normal')
    log_text.insert(tk.END, message + '\n')
    log_text.see(tk.END)
    log_text.config(state='disabled')


# UI Setup
root = tk.Tk()
root.title("PDF Processing Tool")

input_path_var = tk.StringVar()
output_path_var = tk.StringVar()

tk.Label(root, text="Input Directory:").grid(row=0, column=0)
input_entry = tk.Entry(root, textvariable=input_path_var, width=50)
input_entry.grid(row=0, column=1)
input_button = tk.Button(root, text="Browse", command=select_input_path)
input_button.grid(row=0, column=2)

tk.Label(root, text="Output Directory:").grid(row=1, column=0)
output_entry = tk.Entry(root, textvariable=output_path_var, width=50)
output_entry.grid(row=1, column=1)
output_button = tk.Button(root, text="Browse", command=select_output_path)
output_button.grid(row=1, column=2)

process_button = tk.Button(root, text="Process PDFs", command=run_processing)
process_button.grid(row=2, column=1)

log_text = scrolledtext.ScrolledText(root, width=70, height=10, state='disabled')
log_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()
