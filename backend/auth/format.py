import subprocess
import os

# Path to the src directory within the backend folder
src_path = "./"  # Adjust this path if necessary


# Function to check formatting using Black
def check_format():
    if not os.path.exists(src_path):
        print(f"Path '{src_path}' does not exist.")
        return

    try:
        result = subprocess.run(
            ["black", "--check", src_path], check=True, capture_output=True, text=True
        )
        print("Format check passed!\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Format issues found:\n", e.stderr)


# Function to fix formatting using Black
def fix_format():
    if not os.path.exists(src_path):
        print(f"Path '{src_path}' does not exist.")
        return

    try:
        result = subprocess.run(
            ["black", src_path], check=True, capture_output=True, text=True
        )
        print("Format fixed!\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error while fixing format:\n", e.stderr)


# Call the check function
check_format()
# Uncomment the following line to fix the format
fix_format()
