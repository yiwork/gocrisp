FROM python:3.9

WORKDIR /app

RUN useradd -U -r gocrisp

# Install pip libraries
COPY --chown=gocrisp:gocrisp Pipfile* /app/
RUN chown -R gocrisp:gocrisp /app && \
    pip install pipenv && \
    pipenv install --system --deploy

# Copies code into image  
COPY --chown=gocrisp:gocrisp . /app/

USER gocrisp
EXPOSE 5000/tcp

CMD ["/usr/local/bin/gunicorn", "-c", "/app/gunicorn.conf.py", "wordcount:app"]

