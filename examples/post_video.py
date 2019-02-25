from inspie import InspieAPI

if __name__ == '__main__':
    i = InspieAPI("user", "pwd")
    photo_path = 'img_path'
    video_local_path = "video_path"
    caption = "#tag caption!"
    i.upload_Video(video_local_path, photo_path, caption=caption)
