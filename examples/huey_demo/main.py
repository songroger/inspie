# main.py
import time
import argparse
from config import huey
from tasks import count_beans, ins_upload


if __name__ == '__main__':
    # count_beans(int(100))
    # res = count_beans.schedule(args=(10), delay=10)

    parser = argparse.ArgumentParser()
    parser.add_argument('--user', required=True, help='user name')
    parser.add_argument('--pwd', required=True, help='password')
    parser.add_argument('--photo', required=True, help='photo')
    parser.add_argument('--caption', help='caption')
    parser.add_argument('--delay', type=int, default=0, help='delay time')
    args = parser.parse_args()

    photo_path = args.photo
    caption = args.caption
    delay = args.delay
    res = ins_upload.schedule(args=(args.user, args.pwd, photo_path, caption), delay=delay)

    print(res.get(False))
    time.sleep(delay + 10)
    print(res.get())
