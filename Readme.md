# Intro
This is a simple `importer.py` script to import from provided test data set.

The `main.py` server provides the data via standardized aspect / submodel endpoints.

This project is a simple test tool in the context of:

https://github.com/catenax-ng/product-data-integrity-demonstrator

# Instructions
## Setup
You may use a virtual python env
```
python3 -m venv venv
source ./venv/bin/activate
```
Install the dependencies
```
pip install -r requirements.txt
```

# Import from data file
```
# get a list of available ManufacturerID s from the data set
python importer.py --list-manufacturers ./OEMA_HYBRID_VEHICLES_10_fix2.json

# select one to import
python importer.py --import-for BPNLTIERBZZ

# delete, also from EDC and Registry
python importer.py --import-for BPNLTIERBZZ --delete

```
# Run the endpoints
```
python main.py
```
Open http://localhost:8080/docs#/
