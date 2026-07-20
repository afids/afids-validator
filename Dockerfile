FROM debian:bookworm as packaging
ENV PATH=/root/.local/bin:$PATH
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
    python3 \
    python3-pip \
    pipx \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && pipx ensurepath \
    && pipx install poetry
WORKDIR /apps/afidsvalidator
COPY . .
RUN poetry build

FROM debian:bookworm as deploy
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
    build-essential \
    gcc \
    python3 \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
WORKDIR /apps/afidsvalidator
COPY --from=packaging /apps/afidsvalidator/dist/afidsvalidator-*-py3-none-any.whl /apps/wheels/
RUN pip install --no-cache-dir --break-system-packages `ls /apps/wheels/*.whl`[deploy]
ENTRYPOINT ["uwsgi", "-w", "afidsvalidator.wsgi:app"]
