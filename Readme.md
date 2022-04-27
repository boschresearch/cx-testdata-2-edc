# Intro
This is a simple `importer.py` script to import from provided test data set.

The `main.py` server provides the data via standardized aspect / submodel endpoints.

This project is a simple test tool in the context of:

https://github.com/catenax-ng/product-data-integrity-demonstrator

# Settings
`.env-example` shows possible settings for `.env` / environment variables.

It contains default configuration for getting started with the getting-started-guide:

https://catenax-ng.github.io/docs/catenax-at-home-getting-started-guide

## Getting-Started-Guide
For providing data, it is enough to start the guide with the following command:

Checkout the project from:
https://github.com/catenax-ng/catenax-at-home/tree/main/getting-started-guide

```
docker-compose up registry-service provider-control-plane provider-data-plane
```
If the Catena-X INT registry is configured (you need client_id and client_secret) you only need:
```
docker-compose up provider-control-plane provider-data-plane
```

# Run
```
docker-compose --project-name getting-started-guide up --build testdata2edc
```
This command starts the container and attaches it to the same network that has been started with the `getting-started-guide` docker environment by using the `--project-name` flag.

Leave out `--build` to reuse the existing container/image.

You can then import or delete data with (change your Testdata BPN...)
```
docker exec -ti testdata2edc python importer.py --import-for BPNLTIERBZZ ./testdata_file.json
# delete items
docker exec -ti testdata2edc python importer.py --import-for BPNLTIERBZZ --delete ./testdata_file.json
```
The testdata file can be changed with `TESTDATA_FILE` in your customized `.env` file. Default is `OEMA_HYBRID_VEHICLES_10_fix8.json` in the root directory.

Download Testdata files from the internal source at: https://confluence.catena-x.net/pages/viewpage.action?pageId=25225943

Open http://localhost:8080/docs#/
to see the endpoints and use one of the `cx_id` printed from the import script or afterwards from the sarted docker print out (if you start without `--build` option to reuse the existing container...)

# Development
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

## Run the endpoints
After the data has been imported, it can be served via the endpoints. Start the server with:
```
python main.py
```


# Todo / Notes
- Instead of importer script, think about upload interface
- The submodules catena-x-edc and tractusx are not used by default. Nothing to worry about and no need to checkout those submodules

