import pandas as pd
import os

from report.selenium.utiles import send_error_report


class Excel:
    def load_any_file_in_dir(self, subfolder_name: str):
        folder_path = os.path.join(
            os.getcwd(), subfolder_name) if subfolder_name else os.getcwd()

        files = [f for f in os.listdir(folder_path) if os.path.isfile(
            os.path.join(folder_path, f))]
        if not files:
            raise FileNotFoundError("No files found in the directory.")

        files.sort(key=lambda f: os.path.getctime(
            os.path.join(folder_path, f)))

        most_recent_file = files[0]
        excel_file_path = os.path.join(folder_path, most_recent_file)
        print(f"Loading file: {excel_file_path}")
        # email the file use send_error_report
        try:
            cols = pd.read_csv(excel_file_path, nrows=1).columns
            data = pd.read_csv(excel_file_path, usecols=cols)
            return data
        except Exception as e:
            send_error_report(
                excel_file_path,
                f"Error loading file: {excel_file_path} and error{e}",
                'Error to read csv file - Tock',
                "csv"
            )
            return None

    def load_excel(self, subfolder_name: str, excel_file_name: str):
        excel_file_name = excel_file_name
        if not subfolder_name:
            excel_file_path = os.path.join(os.getcwd(), excel_file_name)
        else:
            excel_file_path = os.path.join(
                os.getcwd(), subfolder_name, excel_file_name)

        cols = pd.read_csv(excel_file_path, nrows=1).columns
        data = pd.read_csv(excel_file_path, usecols=cols)
        # os.remove(excel_file_path)
        return data
