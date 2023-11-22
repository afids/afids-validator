FROM debian:bullseye as packaging
ENV PATH=/root/.local/bin:$PATH
RUN echo "deb http://deb.debian.org/debian bullseye-backports main" > /etc/apt/sources.list.d/backports.list \
    && apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
    python3=3.9.2-3 \
    python3-pip=20.3.4-4+deb11u1 \
    && apt-get install -y -q --no-install-recommends -t bullseye-backports pipx=1.0.0-1~bpo11+1 \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && pipx ensurepath \
    && pipx install poetry
WORKDIR /apps/afidsvalidator
COPY . .
RUN poetry build

FROM debian:bullseye as deploy
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
    build-essential=12.9 \
    gcc=4:10.2.1-1 \
    python3=3.9.2-3 \
    python3-dev=3.9.2-3 \
    python3-pip=20.3.4-4+deb11u1 \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
WORKDIR /apps/afidsvalidator
COPY --from=packaging /apps/afidsvalidator/dist/afidsvalidator-*-py3-none-any.whl /apps/wheels/
RUN pip install --no-cache-dir `ls /apps/wheels/*.whl`[deploy]
ENTRYPOINT ["uwsgi", "-w", "afidsvalidator.wsgi:app"]
