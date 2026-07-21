# Dockerfile for JCIIOT FactorySorting 100/100 Reproduction
# 基于 NVIDIA CUDA 镜像，包含 MuJoCo + EGL 渲染环境
#
# 构建命令：
#   docker build -t jciiot:latest .
#
# 运行命令（需要 NVIDIA Container Toolkit）：
#   docker run --gpus all -it --rm \
#     -v $(pwd):/workspace \
#     -e MUJOCO_GL=egl \
#     -e PYOPENGL_PLATFORM=egl \
#     jciiot:latest bash

FROM nvidia/cuda:13.3.0-runtime-ubuntu22.04

LABEL maintainer="Yigen Feng <fengyigen@qq.com>"
LABEL description="JCIIOT FactorySorting 100/100 reproduction environment"
LABEL version="1.0.0"

# 避免交互式安装
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 设置工作目录
WORKDIR /workspace

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3-pip \
    python3.12-dev \
    python3.12-venv \
    wget \
    curl \
    git \
    vim \
    less \
    libegl1 \
    libgles2 \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libegl-mesa0 \
    libosmesa6 \
    libosmesa6-dev \
    libglfw3 \
    libglfw3-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置 Python 3.12 为默认
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# 升级 pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 设置环境变量（MuJoCo EGL 渲染）
ENV MUJOCO_GL=egl
ENV PYOPENGL_PLATFORM=egl
ENV PYTHONPATH=/workspace/JCIIOT:/workspace/JCIIOT/robosuite/robosuite:/workspace/JCIIOT/robomimic:/workspace/JCIIOT/src

# 复制 requirements.txt 并安装 Python 依赖
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 创建数据目录
RUN mkdir -p /workspace/JCIIOT/robosuite/robosuite \
             /workspace/JCIIOT/demos_l1_50 \
             /workspace/JCIIOT/demos_l3_50

# 默认命令
CMD ["/bin/bash"]
