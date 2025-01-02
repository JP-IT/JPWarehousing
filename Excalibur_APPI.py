import requests
import xml.etree.ElementTree as ET
import pandas as pd
import logging
from pathlib import Path

# Setup detailed logging
logging.basicConfig(filename="C:\\Users\\it\\OneDrive\\Desktop\\Excalibur API\\excalibur_api_log.txt",
                    level=logging.DEBUG,  # Set to DEBUG to capture detailed information
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Replace with your actual Excalibur API endpoint, username, and password
api_url = "https://jpwca.camelot3plcloud.com:7047/Excalibur140/WS/JP%20Warehousing/Codeunit/TPLWebServiceInt"
username = "WEBSERV"
password = "Itadmin1234!"

# Define the SOAP action header
headers = {
    'Content-Type': 'text/xml',
    'SOAPAction': 'urn:microsoft-dynamics-schemas/codeunit/TPLWebServiceInt:GetAvailableInventory'
}

# Define the SOAP request body to retrieve all inventory for the client "LALALA"
soap_body = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="urn:microsoft-dynamics-schemas/codeunit/TPLWebServiceInt">
   <soapenv:Header/>
   <soapenv:Body>
      <tem:GetAvailableInventory>
         <tem:pInterfaceProfile>TEST_API</tem:pInterfaceProfile>  <!-- Ensure this profile is correct -->
         <tem:pClient>LALALA</tem:pClient>  <!-- Ensure this client code is correct -->
         <tem:pTradingPartner></tem:pTradingPartner>
         <tem:pXMLDoc></tem:pXMLDoc>
         <tem:pClientFilter></tem:pClientFilter>
         <tem:pItem></tem:pItem>
      </tem:GetAvailableInventory>
   </soapenv:Body>
</soapenv:Envelope>
"""

try:
    # Make the SOAP request
    response = requests.post(api_url, data=soap_body, headers=headers, auth=(username, password))

    if response.status_code == 200:
        logging.info("Successfully connected to Excalibur API.")
        logging.debug(f"API Response: {response.content}")  # Log the raw API response content

        # Parse the XML response
        root = ET.fromstring(response.content)

        # Check if there's data to process
        items = root.findall('.//{urn:microsoft-dynamics-schemas/codeunit/TPLWebServiceInt}string')
        if items:
            # Convert XML data to a list of dictionaries
            data = []
            for item in items:
                data.append({"Inventory": item.text})

            # Convert to a DataFrame
            df = pd.DataFrame(data)

            # Define the output path
            output_dir = Path("C:\\Users\\it\\OneDrive\\Desktop\\Excalibur API")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "inventory_data_LALALA.xlsx"

            # Save DataFrame to Excel file
            df.to_excel(output_file, index=False)
            logging.info(f"Inventory data successfully extracted and saved to '{output_file}'.")
        else:
            logging.info("No inventory data found for the specified client.")
    else:
        logging.error(f"Failed to retrieve data. HTTP Status Code: {response.status_code}")
        logging.debug(f"Response content: {response.content}")

except requests.exceptions.RequestException as e:
    logging.error(f"API request failed: {e}")
