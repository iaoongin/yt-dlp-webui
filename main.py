import re
import yt_dlp
import gradio as gr
import os
import time
import hashlib

# 定义下载目录
download_dir = "downloads"
download_tmp_dir = "downloads/tmp"

# 确保下载目录存在
os.makedirs(download_dir, exist_ok=True)
os.makedirs(download_tmp_dir, exist_ok=True)


def md5_hash(text):
    """计算文本的MD5哈希值"""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def sanitize_filename(filename):
    # 替换 Windows 不允许的字符为下划线
    return re.sub(r'[<>:"/\\|?*]', "_", filename)


def findFile(directory, target_string):
    """
    判断指定目录下的文件名是否包含某个字符串
    :param directory: 要检查的目录路径
    :param target_string: 要查找的目标字符串
    :return: 如果找到包含目标字符串的文件名返回 True，否则返回 False
    """
    # 遍历指定目录下的所有文件和文件夹
    for entry in os.scandir(directory):
        if entry.is_file() and target_string in entry.name:
            return os.path.join(download_dir, entry.name)


def download_video(url):
    start_time = time.time()  # 记录开始时间

    # 计算URL的MD5哈希值作为文件名的一部分
    url_hash = md5_hash(url)

    # 使用yt-dlp提取视频信息而不下载
    ydl_opts = {"skip_download": True}  # 不下载视频

    # 检查文件是否已存在,按文件名包含 url_hash
    match_file = findFile(download_dir, url_hash)
    if match_file:
        elapsed_time = time.time() - start_time  # 计算执行时间
        return f"缓存命中: {match_file} (耗时: {elapsed_time:.2f}秒)", match_file

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_id = info_dict.get("id", None)
        video_title = info_dict.get("title", None)

    # 检查文件是否已存在,按文件名包含 url_hash
    match_file = findFile(download_dir, video_id)
    if match_file:
        elapsed_time = time.time() - start_time  # 计算执行时间
        return f"缓存命中: {match_file} (耗时: {elapsed_time:.2f}秒)", match_file

    # 自定义文件名规则，使用URL的MD5哈希值
    safe_title = sanitize_filename(video_title) if video_title else "video"
    video_filename = f"{url_hash}_{video_id}_{safe_title}.mp4"
    tmp_video_filepath = os.path.join(download_tmp_dir, video_filename)

    # 如果视频不在缓存中，进行下载
    # ydl_opts = {"format": "best", "outtmpl": video_filepath}  # 使用自定义文件名
    ydl_opts = {
        "format": "bv[ext=mp4][vcodec^=avc1]+ba[acodec^=mp4a]/best",
        "merge_output_format": "mp4",
        "postprocessor_args": ["-c", "copy"],
        "outtmpl": tmp_video_filepath,
    }  # 使用自定义文件名
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # 下载完成后，将视频文件移动到下载目录
    video_filepath = os.path.join(download_dir, video_filename)
    os.rename(tmp_video_filepath, video_filepath)

    elapsed_time = time.time() - start_time  # 计算执行时间
    # 分别对应不同的输出参数
    return f"下载完成: {video_title} (耗时: {elapsed_time:.2f}秒)", video_filepath


# 创建 Gradio 接口
iface = gr.Interface(
    fn=download_video,
    inputs=gr.Textbox(
        lines=1,
        placeholder="输入视频URL...",
        label="视频URL",
        value="https://www.bilibili.com/video/BV1MN41187U6?p=1",
    ),
    outputs=[
        gr.Textbox(label="下载状态"),  # 显示下载状态
        # 显示下载的视频文件路径
        gr.Video(
            label="下载的视频",
            height=360,
        ),
    ],  # 设置视频预览的高度
    title="视频下载器",
    description="输入视频URL以下载视频",
    flagging_mode="never",  # 禁用 Flag 按钮
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0")
