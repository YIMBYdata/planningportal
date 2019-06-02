.env:
	cp example.env .env

setup: .env
	pipenv install --dev

.PHONY: fetchdata
fetchdata:
	# From https://data.sfgov.org/Housing-and-Buildings/PPTS-Records/7yuw-98m5
	mkdir -p data
	curl -L -o data/$$(date "+%Y-%m-%d")-ppts.csv https://data.sfgov.org/api/views/kgai-svwy/rows.csv?accessType=DOWNLOAD 
