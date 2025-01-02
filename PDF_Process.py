import pdfplumber
import pandas as pd
import os
import re
import shutil
from datetime import datetime

# Define the input and output paths
input_directory = r'C:\Users\it\OneDrive\Desktop\TESTFILE\Input'
processed_directory = r'C:\Users\it\OneDrive\Desktop\TESTFILE\Input\Processed'  # Define the processed directory
output_directory = r'C:\Users\it\OneDrive\Desktop\TESTFILE\Output'
template_path = r'C:\Users\it\OneDrive\Desktop\TESTFILE\Template\Template.xlsx'


def clean_text(text):
    """Remove unwanted commas and extra spaces from text."""
    return text.replace(',', '').strip()


def extract_data_from_pdf(pdf_path):
    all_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text is None:
                print(f"No text found on page {page_number} of {pdf_path}")
                continue

            # Extract order-level data
            order_data = {'Ship-to Name': "", 'Ship-to Addr 1': "", 'Ship-to City': "", 'Ship-to State': "US",
                          'Ship-to Zip': "US", 'Ship-to Country': "US", 'ORDER REF #': "", 'Shipment #': "", 'PO#': "",
                          'Order date': "", 'CLIENT CODE': "SAMSS", 'UOM': "EACH", 'Record Type': "BC",
                          'Warehouse': "JPFN"}

            # Extract 'Order Date' using regex based on surrounding text pattern
            order_date_pattern = r"Ship Cancel Ship Salesperson Cust# Warehouse\n(\d{2}/\d{2}/\d{2})"
            order_date_match = re.search(order_date_pattern, text)
            if order_date_match:
                order_data['Order date'] = order_date_match.group(1)

            # Extract 'Pick Ticket#' and 'Shipment #'
            ticket_pattern = r"PACKING SLIP\n(\d+)-"
            ticket_match = re.search(ticket_pattern, text)
            if ticket_match:
                order_data['ORDER REF #'] = ticket_match.group(1)
                order_data['Shipment #'] = ticket_match.group(1)

            # Regex to extract Purchase Order Number
            po_pattern = r"Purchase Order Number Dept Order Date Our Order Number\n(\d+)"
            po_match = re.search(po_pattern, text)
            if po_match:
                order_data['PO#'] = po_match.group(1)

            # Process 'Ship To' information
            ship_to_index = text.find('Ship To:')
            if ship_to_index != -1:
                ship_to_block = text[ship_to_index:].split('\n')[1:4]
                if len(ship_to_block) >= 3:
                    order_data['Ship-to Name'] = clean_text(ship_to_block[0])
                    order_data['Ship-to Addr 1'] = clean_text(ship_to_block[1])
                    city_zip_state = ship_to_block[2].split()
                    order_data['Ship-to City'] = clean_text(city_zip_state[0])
                    order_data['Ship-to State'] = clean_text(city_zip_state[1])
                    order_data['Ship-to Zip'] = clean_text(city_zip_state[2].split('-')[0])

            # Extract and process each item
            item_start = text.find("PO#")
            item_end = text.find("Total Qty")
            if item_start != -1 and item_end != -1:
                item_text = text[item_start:item_end]
                item_lines = item_text.split("\n")[1:]  # Skip the "PO#" line itself
                for item_line in item_lines:
                    item_details = re.match(r"(\d+,?\d*) EA (\d+\.\d+) (\S+) (.+)", item_line)
                    if item_details:
                        quantity, ctn_count, item_number, description = item_details.groups()
                        item_data = order_data.copy()  # Start with a copy of the order data
                        item_data.update({
                            'Qty Ordered': quantity.replace(',', ''),
                            'Item No.': item_number,
                            'Desc 1': description.split('SKU#')[0].strip()  # Assuming description adjustment here
                        })
                        all_data.append(item_data)

    return all_data


def fill_excel_template(all_data, template_path, output_path):
    df_template = pd.read_excel(template_path)
    output_df = pd.DataFrame(all_data, columns=df_template.columns)
    output_df.to_excel(output_path, index=False)


# Get the current date in MM-DD-YYYY format
current_date = datetime.now().strftime("%m-%d-%Y")

# Process each PDF file
for pdf_file in os.listdir(input_directory):
    if pdf_file.endswith('.pdf'):
        pdf_path = os.path.join(input_directory, pdf_file)
        all_data = extract_data_from_pdf(pdf_path)
        # Create a unique output file for each PDF based on the current date and the original PDF file name
        output_filename = f"{current_date} - PROCESSED - {os.path.splitext(pdf_file)[0]}.xlsx"
        output_file = os.path.join(output_directory, output_filename)
        fill_excel_template(all_data, template_path, output_file)
        print(f"Processed {pdf_file} and saved data to {output_file}.")

        # Move the processed PDF file to the 'Processed' directory
        shutil.move(pdf_path, os.path.join(processed_directory, pdf_file))
