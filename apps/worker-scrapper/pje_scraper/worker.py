import tempfile

from pje_scraper import PjePipeline
from shared.celery_client import app
from shared.s3_client import get_s3_client

client = get_s3_client()

@app.task
def run_pipeline(numero: str, grau: str = "1", headless: bool = True):
    pipeline = PjePipeline(headless=headless)
    session = pipeline.resolve(numero, grau=grau)
    response = pipeline.fetch_with_token(session)

    client.create_bucket("pje-documents")
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name
    client.upload_object("pje-documents", f"{session.numero_processo}.pdf", tmp_path)
