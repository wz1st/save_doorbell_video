#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import Flask, request
import urllib.parse, os, requests, m3u8
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


app = Flask(__name__)

@app.route('/save_video', methods=['POST'])
def save_video():
    current_date = datetime.now().strftime("%Y%m%d")
    
    data = request.form
    stream_address = urllib.parse.unquote(data.get('stream_address'))
    motion_video_time = data.get('motion_video_time')
    save_path = '/nas'  #视频保存位置
    video_limit = '30'  #保存天数上限

    m3u8_file = f'{save_path}/tmp/{motion_video_time}.m3u8'
    ts_tmp_dir = f'{save_path}/tmp/{motion_video_time}/'

    try:
        os.makedirs(f"{save_path}/{current_date}")
    except:
        pass
    try:
        os.makedirs(f"{save_path}/tmp")
    except:
        pass
    try:
        os.makedirs(ts_tmp_dir)
    except:
        pass
    download_m3u8(stream_address, m3u8_file)
    with open(m3u8_file, 'r') as f:
        m3u8_data = f.read()
        m3u8_decode(m3u8_data, ts_tmp_dir)
        try:
            os.system(f"rm -rf {save_path}/{current_date}/{motion_video_time}.mp4")
            # 猫眼的视频是HEVC编码格式，有点占用较少，缺点不同的设备不一定能播放出画面
            # os.system(f"ffmpeg -f concat -safe 0 -i {ts_tmp_dir}ts.list -c copy {save_path}/{current_date}/{motion_video_time}.mp4")


            # 软解把HEVC转成H.264，占用较大，软解硬解都能放
            os.system(f"ffmpeg -f concat -safe 0 -i {ts_tmp_dir}ts.list -c:v libx264 -preset slow -crf 22 -c:a copy -b:a 128k {save_path}/{current_date}/{motion_video_time}.mp4")

            # 启用VAAPI硬编码
            # os.system(f"ffmpeg -f concat -safe 0 -i {ts_tmp_dir}ts.list -vaapi_device /dev/dri/renderD128 -c:v h264_vaapi -global_quality 25 -vf 'format=nv12|vaapi,hwupload' -c:a copy {save_path}/{current_date}/{motion_video_time}.mp4")
            os.system(f"rm -rf {save_path}/tmp/{motion_video_time}*")
            os.system(f"find {save_path} -type f -mtime +{video_limit} -delete")
            os.system(f"find {save_path} -depth -type d -empty -delete")
        except:
            pass
    return "ok"

def download_m3u8(url, output_file):
    for i in range(5):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                break
        except:
            pass

def m3u8_decode(m3u8_data, ts_tmp_dir):
    m3u8_obj = m3u8.loads(m3u8_data)
    key = download_key(m3u8_obj.keys[0].uri)
    iv = bytes.fromhex(m3u8_obj.keys[0].iv.split('0x')[1])
    os.system(f"rm -rf {ts_tmp_dir}ts.list")
    with open(f"{ts_tmp_dir}ts.list", "a") as f:
        for i in range(len(m3u8_obj.segments)):
            for j in range(5):
                try:
                    ts_data = requests.get(m3u8_obj.segments[i].uri).content
                    break
                except:
                    pass
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_data = unpad(cipher.decrypt(ts_data), AES.block_size)
            with open(f"{ts_tmp_dir}{i}.ts", "wb") as f1:
                f1.write(decrypted_data)
            f.write(f"file '{ts_tmp_dir}{i}.ts'\n")
    return True

def download_key(key_url):
    for i in range(5):
        try:
            response = requests.get(key_url)
            return response.content
        except:
            pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)