import requests
from celery import shared_task
from .models import Bread

@shared_task
def update_breads_from_api():
    url = 'https://api.thecatapi.com/v1/breeds'
    response = requests.get(url)
    if response.status_code == 200:
        breeds = response.json()
        for breed in breeds:
            Bread.objects.update_or_create(
                external_id=breed['id'],
                defaults={'name': breed['name']}
            )
    else:
        pass

