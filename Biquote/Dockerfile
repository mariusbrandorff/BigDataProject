FROM python:3.14.10-slim-trixie
WORKDIR /app

COPY ./requirements.txt ./

# Caches pip dependencies, so that upon change of 1 dependency all pip dependencies don't have to be re-downloaded
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip pip install -r requirements.txt

# Copy src after requirements, as src can change without requirements. (Lets docker cache properly)
COPY ./src ./

RUN python -m compileall -q .

COPY ./schema.avsc ./

# ENV BOOTSTRAP_SERVER # needs to be defined when running, can't have a default that's expected to work
ENV IN_TOPIC="biquote_in"
ENV OUT_TOPIC="biquote_out"

ENTRYPOINT [ "python", "main.py" ]