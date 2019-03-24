.env:
	cp example.env .env

setup: .env
	pipenv install --dev
