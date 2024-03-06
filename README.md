# save_doorbell_video

> 用于保存米家门铃视频的Python脚本

### 准备
#### HomeAssistant
- 接入米家xiaomi_miot_auto
- HACS安装pyscript
#### Nas
- Docker运行环境

>非必须为Nas，HAOS、OpenWrt等支持Docker的设备也可以；  
甚至可以不使用Docker配置好ffmpeg和驱动的Linux环境也可以。  
**需要自行解决挂载等问题**



### 使用
- Nas配置  
把nas目录复制到Nas中，cd到nas目录下    
    - Docker环境  
    执行命令`docker build -t save2mp4 .`创建镜像，执行完成后运行`docker run -it -p 5005:5005 -v $(pwd):/app -v /{替换为你的视频保存地址}:/nas --device=/dev/dri:/dev/dri save2mp4`
    - Linux环境(不使用Docker)  
        - 安装ffmpeg和驱动
        - 修改app.py中19行save_path为你自己的保存地址
        - 按照以下顺序执行
    ```
    pip3 install -r requirements.txt
    nohup python3 app.py > save2mp4.log 2>&1 &  
    ```


- 米家配置  
把猫眼改为实时查看模式，不然HA中会显示猫眼离线，获取不到视频
- HA配置  
    - 把pyscript目录中脚本放入到HA的配置对应目录
    - 修改video_doorbell.py脚本5行中entity为你的猫眼实体id
    - 修改video_doorbell.py脚本12行中nas_addr为你的nas地址
    - YAML配置重载->**重载Pyscript Python scripting**  
    - 配置自动化
    ```
    alias: 猫眼视频保存
    description: ""
    trigger:
    - platform: state
        entity_id:
        - camera.loock_v06_d9c1_video_doorbell # 替换为你的猫眼实体ID
        attribute: motion_video_time
    condition: []
    action:
    - service: pyscript.video_doorbell
        data: {}
    mode: single
    ```

