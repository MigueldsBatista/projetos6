worker:
	# Limita a concorrência ao número de CPUs disponíveis (ou ajuste para metade, se preferir)
	uv run celery -A pje_scraper.worker worker --loglevel=INFO --concurrency=$$(nproc)
