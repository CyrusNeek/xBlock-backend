# @shared_task
# def crawl_toast_kitchen_timings(toast: ToastAuth):
#     filename = f'tmp-{toast.pk}.pem'
#     tmp_private_key = S3Client.s3_client.download_file(
#         settings.AWS_STORAGE_BUCKET_NAME,
#         toast.sshkey.private_key_location, 
#         filename
#     )

#     result = ToastCrawler(
#        host=toast.host,
#        username=toast.username,
#        location_id=toast.location_id,
#        private_key_path=filename,
#        date_time='20240512',
#        file_name='KitchenTimings.csv',
#     ).get_data()
#     os.remove(filename)

#     print(result)
