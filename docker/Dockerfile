# === 小分子量子化学計算用開発環境 ===
FROM mcr.microsoft.com/dotnet/sdk:8.0

ENV DEBIAN_FRONTEND=noninteractive \
    DOTNET_ROOT=/usr/share/dotnet \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PYTHON_VERSION=3.11

# システム依存関係のインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    python${PYTHON_VERSION} python${PYTHON_VERSION}-dev \
    build-essential git ca-certificates \
    libopenblas-dev liblapack-dev gfortran \
    wget curl \
 && rm -rf /var/lib/apt/lists/*

# MinicondaのインストールとToS承認
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -b -p /opt/conda \
    && rm /tmp/miniconda.sh \
    && /opt/conda/bin/conda init bash

# condaの利用規約を事前承認
RUN /opt/conda/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
    && /opt/conda/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# mambaのインストール（高速パッケージ管理）
RUN /opt/conda/bin/conda install mamba -n base -c conda-forge -y

# conda環境の設定
ENV PATH="/opt/conda/bin:${PATH}"
ENV CONDA_ENV_NAME=qchem-qsharp-ds

# 環境ファイルからconda環境を作成
COPY env/environment.yml /tmp/environment.yml
RUN mamba env create -f /tmp/environment.yml

# 開発環境を有効化
ENV PATH="/opt/conda/envs/${CONDA_ENV_NAME}/bin:${PATH}"

# 作業ディレクトリの設定
WORKDIR /workspace

# 開発用のエントリーポイント
CMD ["/bin/bash"]