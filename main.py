import yt_dlp
import gradio as gr
import os
import time
import hashlib

# 定义下载目录
download_dir = 'downloads'

# 确保下载目录存在
os.makedirs(download_dir, exist_ok=True)

def md5_hash(text):
    """计算文本的MD5哈希值"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

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
    ydl_opts = {
        'skip_download': True  # 不下载视频
    }

    # 检查文件是否已存在,按文件名包含 url_hash 
    match_file = findFile(download_dir, url_hash)
    if match_file:
        elapsed_time = time.time() - start_time  # 计算执行时间
        return f"缓存命中: {match_file} (耗时: {elapsed_time:.2f}秒)", match_file

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_id = info_dict.get('id', None)
        video_title = info_dict.get('title', None)
    
    # 检查文件是否已存在,按文件名包含 url_hash 
    match_file = findFile(download_dir, video_id)
    if match_file:
        elapsed_time = time.time() - start_time  # 计算执行时间
        return f"缓存命中: {match_file} (耗时: {elapsed_time:.2f}秒)", match_file

    
    # 自定义文件名规则，使用URL的MD5哈希值
    video_filename = f"{url_hash}_{video_id}_{video_title}.mp4"
    video_filepath = os.path.join(download_dir, video_filename)

    # 如果视频不在缓存中，进行下载
    ydl_opts = {
        'format': 'best',
        'outtmpl': video_filepath  # 使用自定义文件名
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    elapsed_time = time.time() - start_time  # 计算执行时间
    return f"下载完成: {video_title} (耗时: {elapsed_time:.2f}秒)", video_filepath

# 创建 Gradio 接口
iface = gr.Interface(
    fn=download_video,
    inputs=gr.Textbox(lines=1, placeholder="输入视频URL..."),
    outputs=[
        gr.Textbox(),
        gr.Video(height=360)  # 设置视频预览的高度
    ],
    title="视频下载器",
    description="输入视频URL以下载视频",
    allow_flagging="never"  # 禁用 Flag 按钮 
)

if __name__ == "__main__":
    iface.launch(pwa=True)
