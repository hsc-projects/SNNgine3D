# https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker/54763270#54763270

FROM python:3.10


# --------------------------------------
# ------------- Set labels -------------

# See https://github.com/opencontainers/image-spec/blob/master/annotations.md
LABEL name="snn_engine3d"
LABEL version="0.0.0"
LABEL vendor="hsc-projects"
LABEL org.opencontainers.image.title="snn_engine3d"
LABEL org.opencontainers.image.version="0.0.0"
LABEL org.opencontainers.image.url="https://github.com/hsc-projects/snn_engine3d"
LABEL org.opencontainers.image.documentation="https://github.com/hsc-projects/snn_engine3d"


# --------------------------------------
# ---------- Copy and install ----------

# Configure env variables for build/install
# ENV no longer adds a layer in new Docker versions,
# so we don't need to chain these in a single line
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=120
ENV POETRY_VERSION=1.3.2

# Install system deps
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Install with poetry
# pip install would probably work, too, but we'd have to make sure it's a recent enough pip
# Don't bother creating a virtual env -- significant performance increase
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy everything (code) to our workdir
# Our .dockerignore file should be good enough that we don't have extra stuff
COPY . /code


# --------------------------------------
# --------------- Run! -----------------

# Now do something!
#CMD snn_engine3d --help

# Perhaps run a command:
# CMD snn_engine3d --my --options --etc
# or expose a port:
# EXPOSE 443/tcp
