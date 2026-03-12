---
description: "Use when editing captcha_service OCR pipeline, captcha parsing, or related tests. Enforces charset constraints for TRT-6 captcha and uv-based environment workflow."
name: "Captcha OCR Constraints"
applyTo:
	- "captcha_service/main.py"
	- "captcha_service/test.py"
	- "captcha_service/pyproject.toml"
	- "captcha_service/pje_scraper/**/*.py"
---
# Captcha OCR Constraints

- Assume TRT-6 captcha contains only lowercase letters a-z and digits 0-9.
- Never treat uppercase letters as valid final output; normalize to lowercase before returning OCR text.
- Never keep symbols or foreign characters in final OCR output; filter to allowed charset.
- Handle frequent OCR confusions with explicit normalization mappings when validated by dataset examples.

## Environment and Commands

- Use uv as the package manager for Python tasks in this workspace.
- Prefer commands in this form: uv run python ...
- Do not suggest pip install flows when uv and the existing virtual environment are available.

## Testing Expectations

- Validate changes against captcha_service/data/images.json whenever OCR behavior changes.
- In diagnostics, report raw OCR output and normalized output separately.
- If a normalization rule is added, include a short test-visible trace that helps confirm the rule was applied.
