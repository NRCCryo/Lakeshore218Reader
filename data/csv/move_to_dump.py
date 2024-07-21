# move_to_dump.py
import os
import shutil

def move_csv_to_dump():
    source_folder = '.'
    dump_folder = './dump'

    if not os.path.exists(dump_folder):
        os.makedirs(dump_folder)

    for file in os.listdir(source_folder):
        if file.endswith('.csv'):
            shutil.move(os.path.join(source_folder, file), dump_folder)
            print(f"Moved: {file}")

if __name__ == "__main__":
    move_csv_to_dump()
