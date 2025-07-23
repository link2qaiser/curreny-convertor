# Export only production dependencies
requirements:
	poetry export -f requirements.txt --without-hashes -o requirements.txt

# Export all dependencies including dev
requirements-dev:
	poetry export -f requirements.txt --with dev --without-hashes -o requirements-dev.txt

# Run tests
tests:
	pytest

