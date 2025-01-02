import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Set up the Google Sheets API authentication
def authenticate_google_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1jE3zJ-K0hLPA8SXahFz3hoA3doUakd7iX0pp2bH9HzE/edit#gid=0").sheet1
        return sheet
    except Exception as e:
        print(f"Failed to authenticate with Google Sheets: {e}")
        return None

# Function to get all inventory data
def get_inventory_data():
    try:
        sheet = authenticate_google_sheets()
        if sheet:
            records = sheet.get_all_records()
            return records
        else:
            return None
    except Exception as e:
        print(f"Failed to retrieve inventory data: {e}")
        return None

# Function to add a new device to the inventory
def add_device(item_id, item_name, brand, model_number, serial_number, purchase_date, warranty_expiry, status,
               condition, assigned_to, location, value, notes, disposition, hardware_type, tech_support, website,
               image_link):
    try:
        sheet = authenticate_google_sheets()
        if sheet:
            # Current date for 'Log Date'
            log_date = datetime.now().strftime('%Y-%m-%d')

            # Append the row (ensure order matches the headers in your sheet)
            sheet.append_row(
                [item_id, item_name, brand, model_number, serial_number, purchase_date, warranty_expiry, status, condition,
                 assigned_to, location, value, notes, disposition, log_date, hardware_type, tech_support, website, image_link])
        else:
            raise Exception("Failed to access the Google Sheet.")
    except Exception as e:
        print(f"Failed to add device: {e}")
        raise e  # Re-raise exception to handle it in the frontend if needed

# Function to edit an existing device in the inventory
def edit_device(row_number, updated_data):
    try:
        sheet = authenticate_google_sheets()
        if sheet:
            # Update the row based on the row number and updated data
            sheet.update(f"A{row_number}:T{row_number}", [updated_data])
        else:
            raise Exception("Failed to access the Google Sheet.")
    except Exception as e:
        print(f"Failed to edit device: {e}")
