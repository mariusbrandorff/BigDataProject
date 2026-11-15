FROM python:3.14.10-slim-trixie AS builder

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

# Copy src after requirements, as src cna change without requirements. (Lets docker cache properly)
COPY ./src ./

RUN python -m py_compile main.py

FROM python:3.14.10-slim-trixie AS runner
COPY --from=builder /__pycache__/main.cpython-314.pyc ./main.pyc

COPY ./requirements.txt ./
RUN pip install -r requirements.txt


ENV SCHEDULE="* * * * *"
ENV TOPIC_LISTEN="new_card"
ENV TOPIC_SHOUT="tcg"



ENTRYPOINT [ "python", "main.pyc" ]