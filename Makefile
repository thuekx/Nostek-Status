.PHONY: ci hygiene test
ci: hygiene test
hygiene:
	python3 scripts/check_public.py .
test:
	python3 -m unittest discover -s tests -v
