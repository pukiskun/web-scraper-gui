import csv

def export_to_csv(data, file_path):
    if not data:
        raise ValueError("No data to export")

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write header
        writer.writerow(data.keys())
        
        # Write data rows
        num_rows = len(next(iter(data.values())))
        for i in range(num_rows):
            row = [data[col][i] for col in data]
            writer.writerow(row)
