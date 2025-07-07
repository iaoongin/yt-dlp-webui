from yt_dlp import YoutubeDL

url = "https://www.bilibili.com/video/BV1MN41187U6?p=1"

with YoutubeDL({"format": "bestvideo+bestaudio"}) as ydl:
    info = ydl.extract_info(url, download=False)
    for f in info["formats"]:
        # if f["format_id"] in ["100113", "30280"]:
        # 100050+30280
        if f["format_id"] in ["100050", "30280"]:
            print(f"Format ID: {f['format_id']}")
            print(f"  Ext: {f['ext']}")
            print(f"  Video codec: {f.get('vcodec')}")
            print(f"  Audio codec: {f.get('acodec')}")
            print(f"  Container: {f.get('container')}")
