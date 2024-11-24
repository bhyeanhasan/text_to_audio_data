file_path = 'processed_output.txt'
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            print(f"Line {line_number}: {line.strip()}")
except FileNotFoundError:
    print(f"The file '{file_path}' does not exist.")
except UnicodeDecodeError as e:
    print(f"An encoding error occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
