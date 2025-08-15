# === Stable base: .NET SDK 8 (Debian, multi-arch) ===
FROM mcr.microsoft.com/dotnet/sdk:8.0

ENV DEBIAN_FRONTEND=noninteractive \
    DOTNET_ROOT=/usr/share/dotnet \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    VENV_PATH=/opt/venv

# System deps (Python + venv + build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv python3-pip \
    build-essential git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Create and use a dedicated virtualenv for Python packages
RUN python3 -m venv ${VENV_PATH} \
 && ${VENV_PATH}/bin/pip install --upgrade pip setuptools wheel

# Make the virtualenv the default Python
ENV PATH="${VENV_PATH}/bin:${PATH}"

WORKDIR /workspace

# Install Python deps using your requirements.txt into the venv
COPY env/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# (Optional) COPY . /workspace

CMD ["/bin/bash"]