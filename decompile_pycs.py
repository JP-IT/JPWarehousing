import os
import subprocess

# Set the directory where your .pyc files are located
pyc_files_dir = 'C:\\Users\\it\\PycharmProjects\\pythonProject3\\Data_Processing.exe_extracted'

# Loop through all files in the directory
for root, dirs, files in os.walk(pyc_files_dir):
    for file in files:
        if file.endswith('.pyc'):
            full_path = os.path.join(root, file)
            # Construct the output path for the .py file
            output_path = full_path.rsplit('.', 1)[0] + '.py'
            # Use uncompyle6 to decompile the .pyc file to .py
            try:
                subprocess.run(['uncompyle6', '-o', output_path, full_path], check=True)
                print(f'Successfully decompiled: {file}')
            except subprocess.CalledProcessError as e:
                print(f'Failed to decompile: {file}')

# Replace 'path_to_extracted_files_directory' with the actual path to your extracted .pyc files
