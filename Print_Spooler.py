import wmi
import socket
import time
import logging

# Store logs in memory
logs = []


# Function to check the status of port 9100 (RAW printing)
def check_printer_port(ip, port=9100):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)  # Set a timeout for connection
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            logs.append(f"Printer {ip} Port {port} is open.")
            print(f"Printer {ip} Port {port} is open.")
        else:
            logs.append(f"Printer {ip} Port {port} is closed or inaccessible.")
            print(f"Printer {ip} Port {port} is closed or inaccessible.")
    except Exception as e:
        logs.append(f"Error checking port {port} on {ip}: {e}")
        print(f"Error checking port {port} on {ip}: {e}")


# Function to monitor the printer status and jobs
def monitor_printer_status():
    # Connect to WMI
    c = wmi.WMI()

    # Query the printers
    printers = c.Win32_Printer()

    # Loop through printers and check their status
    for printer in printers:
        try:
            printer_details = {
                "Name": printer.Name,
                "PortName": printer.PortName,
                "PrinterStatus": printer.PrinterStatus,
            }

            logs.append(f"Printer Details: {printer_details}")
            print(f"Printer Details: {printer_details}")

            # Check the RAW port if it's a network printer
            if printer.PortName.startswith("192.168."):
                check_printer_port(printer.PortName)

        except Exception as e:
            logs.append(f"Error accessing printer details: {e}")
            print(f"Error accessing printer details: {e}")


def main():
    print("Monitoring printer status and ports... Press 'Ctrl + C' to stop.")

    try:
        # Monitor printer status every 10 seconds
        while True:
            monitor_printer_status()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
        save_option = input("Do you want to save the logs to a file? (yes/no): ").strip().lower()
        if save_option == 'yes':
            filename = input("Enter the filename (default: print_job_log.txt): ").strip()
            if not filename:
                filename = "print_job_log.txt"
            with open(filename, 'w') as file:
                for log in logs:
                    file.write(f"{log}\n")
            print(f"Logs saved to {filename}.")
        else:
            print("Logs discarded.")


if __name__ == "__main__":
    main()
