FROM python:3.9
LABEL maintainer="v1st233@gmail.com"

WORKDIR /app

COPY requirements.txt ./
COPY sources.list /etc/apt/sources.list
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    libva-drm2 \
    libva2 \
    vainfo \
    i965-va-driver \
    && apt-get clean
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ["python3","app.py"]