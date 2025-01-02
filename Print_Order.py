import requests
import base64

# Replace this with your actual PrintNode API key
API_KEY = 'HOBebRar_TAWX_1SQYNQXN7RO1sQt-1Psgl3sHpAdpY'

# Printer ID from PrintNode
PRINTER_ID = 73652056


# Headers for authentication
def get_headers():
    auth = base64.b64encode(f'{API_KEY}:'.encode('utf-8')).decode('utf-8')
    return {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json'
    }


# Function to reorder the print job content
def reorder_print_content(content):
    # For simplicity, assuming the content is a simple list of "pages" (you can adjust this)
    pages = content.split("\n")
    reordered_content = ""

    # Duplicate each page (Page 1, Page 1, Page 2, Page 2, etc.)
    for page in pages:
        if page.strip():  # Ignore empty lines
            reordered_content += f"{page}\n{page}\n"

    return reordered_content


# Function to submit the modified job to PrintNode
def submit_print_job(printer_id, title, content):
    url = 'https://api.printnode.com/v4/printjobs'
    headers = get_headers()

    # Prepare the payload for the print job submission
    payload = {
        'printerId': printer_id,
        'title': title,
        'content': {
            'type': 'raw_base64',
            'data': base64.b64encode(content.encode()).decode('utf-8')
        },
        'source': 'python_script'
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print(f"Print job '{title}' successfully submitted to printer.")
    else:
        print(f"Failed to submit print job: {response.status_code} - {response.text}")


# Example content for the print job (replace this with actual content from your system)
original_content = """
Page 1 content
Page 2 content
Page 3 content
"""

# Main logic to reorder and resubmit the print job
if __name__ == "__main__":
    # Reorder the print content (Page 1, Page 1, Page 2, Page 2, etc.)
    reordered_content = reorder_print_content(original_content)

    # Submit the reordered job to the printer via PrintNode
    submit_print_job(PRINTER_ID, "Reordered Print Job", reordered_content)
