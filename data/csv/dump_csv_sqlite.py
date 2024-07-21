import os
import csv
import sqlite3
import datetime
import logging

def sanitize_name(name):
    name = name.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
    return ''.join(['_' if not c.isalnum() else c for c in name])

def dump_csv_to_sqlite(dump_folder='dump', dumped_folder='dumped', db_name='coldhead.db', log_filename='dump_log_master.csv'):
    logging.info("Starting CSV dump.")
    db_conn = sqlite3.connect(db_name)
    cursor = db_conn.cursor()

    log_file_exists = os.path.isfile(log_filename)
    
    with open(log_filename, 'a', newline='') as log_file:
        log_writer = csv.writer(log_file)
        
        if not log_file_exists:
            log_writer.writerow(['Timestamp', 'Filename', 'Table Name', 'Status', 'Original File Size (bytes)', 'Copied File Size (bytes)', 'Number of Lines Copied'])

        for file_name in os.listdir(dump_folder):
            if file_name.endswith('.csv'):
                table_name = sanitize_name(f"t_{os.path.splitext(file_name)[0]}")
                file_path = os.path.join(dump_folder, file_name)
                original_file_size = os.path.getsize(file_path)
                number_of_lines_copied = 0

                try:
                    with open(file_path, 'r') as csv_file:
                        reader = csv.reader(csv_file)
                        headers = next(reader)
                        sanitized_headers = [sanitize_name(header) for header in headers]

                        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(sanitized_headers)})")
                        cursor.executemany(f"INSERT INTO {table_name} ({', '.join(sanitized_headers)}) VALUES ({', '.join(['?']*len(sanitized_headers))})", reader)
                        number_of_lines_copied = cursor.rowcount

                    db_conn.commit()
                    os.rename(file_path, os.path.join(dumped_folder, file_name))
                    status = 'Success'
                except Exception as e:
                    logging.error(f"Error processing {file_name}: {str(e)}")
                    status = f'Error: {str(e)}'

                copied_file_size = os.path.getsize(os.path.join(dumped_folder, file_name)) if status == 'Success' else 0
                log_writer.writerow([datetime.datetime.now(), file_name, table_name, status, original_file_size, copied_file_size, number_of_lines_copied])

    db_conn.close()
    logging.info(f"Completed CSV dump. Log file updated: {log_filename}")
    return log_filename

if __name__ == '__main__':
    logging.basicConfig(filename='csv_dump.log', level=logging.INFO, 
                        format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    try:
        log_file = dump_csv_to_sqlite()
        print(f"CSV dump completed successfully. Log file updated: {log_file}")
    except Exception as e:
        print(f"An error occurred during CSV dump: {str(e)}")
        logging.error(f"An error occurred during CSV dump: {str(e)}")
