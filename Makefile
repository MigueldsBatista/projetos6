worker:
	uv run celery -A pje_scraper.worker worker --loglevel=INFO
