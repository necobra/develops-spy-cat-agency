FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN python manage.py migrate && \
    python manage.py shell -c "from spycats.tasks import update_breads_from_api; update_breads_from_api()"

CMD ["python", "manage.py", "runserver"]
