import re, requests, functools, urllib.parse

@service
def video_doorbell():
    entity = camera.loock_v06_d9c1_video_doorbell  #替换为你自己的实体
    stream_address = urllib.parse.quote(getattr(entity, 'stream_address'))
    motion_video_time = re.sub(r'[^0-9]', '', getattr(entity, 'motion_video_time'))
    save_video(stream_address, motion_video_time)


async def save_video(stream_address, motion_video_time):
    nas_addr = "http://192.168.0.250:5005" #替换为你自己的nas地址，端口为app.py中定义的端口，或者docker开放的端口
    post_request = functools.partial(requests.post, f'{nas_addr}/save_video', data={"stream_address": stream_address, "motion_video_time": motion_video_time})
    response = await hass.async_add_executor_job(post_request)
    return response
