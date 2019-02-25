from inspie import InspieAPI
from config import huey


@huey.task()
def count_beans(num):
    print('-- counted %s beans --' % num)


@huey.task(retries=3, retry_delay=5)
def ins_upload(user, pwd, photo_path, caption):
    i = InspieAPI(user, pwd)
    status = i.upload_photo(photo_path, caption=caption)
    return status
