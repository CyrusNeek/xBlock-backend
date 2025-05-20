from datetime import datetime

from django.conf import settings
from django.utils import timezone

from report.selenium.services.excel import Excel

import math
import os
import paramiko
import pandas as pd


input_format = "%m/%d/%y %I:%M %p"


def parse_date(date_str, format="%m/%d/%y %I:%M %p"):

    formats = ["%m/%d/%Y %I:%M %p", "%m/%d/%y %I:%M %p"]

    if format:
        formats.insert(0, format)

    for format in formats:
        try:
            return timezone.datetime.strptime(date_str, format)
        except Exception:
            pass

    raise ValueError(f"Invalid date format: {date_str}")


def safe_float(value):
    try:
        return float(value) if pd.notnull(value) or not math.isnan(value) else None
    except ValueError:
        return None


def get_current_time_format():
    current_datetime = datetime.now() - timezone.timedelta(days=1)
    return current_datetime.strftime("%Y%m%d")


class ToastCrawler(Excel):
    def __init__(
        self,
        host: str,
        username: str,
        location_id: str,
        private_key_path: str,
        date_time: str = None,
        file_name: str = None,
        download_path: str = settings.BASE_DIR / "downloads/",
    ):
        self.host = host
        self.username = username
        self.location_id = location_id
        self.date_time = date_time
        self.file_name = file_name
        self.private_key_path = private_key_path
        self.download_path = f"{download_path}/{location_id}"
        self.port = 22

    def get_history(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            self.host,
            port=self.port,
            username=self.username,
            key_filename=self.private_key_path,
        )
        sftp = self.client.open_sftp()
        result = self.get_datetime_list(sftp, f"/{self.location_id}")
        sftp.close()
        return result

    def get_data(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            self.host,
            port=self.port,
            username=self.username,
            key_filename=self.private_key_path,
        )
        return self.download_file()

    def get_datetime_list(self, sftp, remote_url: str):
        data = dict()
        data["status"] = True

        try:
            data["list"] = sftp.listdir(remote_url)
        except Exception as e:
            print(e)
            data["status"] = False
            data["list"] = []
            data["error"] = e

        return data

    def download_file(self):
        if os.path.exists(
            self.download_path + "/" + self.file_name + str(self.date_time or "")
        ):
            os.remove(
                self.download_path + "/" + self.file_name + str(self.date_time or "")
            )

        sftp = self.client.open_sftp()
        data_list = self.get_datetime_list(sftp, f"/{self.location_id}")
        data = {"status": False, "result": []}
        dates = sorted(data_list["list"], reverse=True)
        if data_list["status"]:
            for item in dates:
                if item == self.date_time:
                    remote_file_path = f"/{self.location_id}/{self.date_time}"
                    if "." not in self.date_time:
                        remote_file_path += f"/{self.file_name}"
                    else:
                        remote_file_path = f"/{self.location_id}/{self.file_name}"
                    os.makedirs(self.download_path, exist_ok=True)
                    try:
                        sftp.get(
                            remote_file_path,
                            self.download_path
                            + "/"
                            + self.file_name
                            + str(self.date_time or ""),
                        )
                    except Exception:
                        cols = pd.read_csv(
                            sftp.open(remote_file_path, "r"), nrows=1
                        ).columns
                        df = pd.read_csv(sftp.open(remote_file_path, "r"), usecols=cols)

                        df.to_csv(
                            self.download_path
                            + "/"
                            + self.file_name
                            + str(self.date_time or ""),
                            index=False,
                            mode="w",
                            header=True,
                        )
                    sftp.close()
                    data["status"] = True
                    data["result"] = self.load_excel(
                        self.download_path, self.file_name + str(self.date_time or "")
                    )
                    break

        return data
