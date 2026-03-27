from celery import Celery

BROOKER_URL = 'amqp://user:password@localhost:5672/'

app = Celery('tasks', broker=BROOKER_URL)

@app.task
def add(x, y):
    return x + y