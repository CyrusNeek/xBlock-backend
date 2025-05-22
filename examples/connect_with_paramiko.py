from report.models import *

import paramiko


def main():
    toast = ToastAuth.objects.first()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        toast.host,
        port=22,
        username=toast.username,
        key_filename="tmp-" + str(toast.pk) + ".pem",
    )
    sftp = client.open_sftp()
    remote_url = f"/{toast.location_id}"
    print(sftp.listdir(remote_url))
    with sftp.open(remote_url + f"/20231021/ItemSelectionDetails.csv") as file:
        data = file.read()
        print(data)


if __name__ == "django.core.management.commands.shell":
    main()
