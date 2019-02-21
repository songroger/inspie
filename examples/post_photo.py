from inspie import InspieAPI

if __name__ == '__main__':
    i = InspieAPI("user", "pwd")
    photo_path = 'img_path'
    caption = "#tag caption!"
    i.upload_photo(photo_path, caption=caption)
