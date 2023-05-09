# traceability-case-study

## Build (Docker)
```
ADMIN_PASSWORD=admin docker-compose build --no-cache
```

Beware, that everyone with access to the built image can see the password!
Password changes are done via build-time and can NOT be changed at runtime right now.

## Run (Docker)
```
docker-compose up --force-recreate
```

## UI
The camera that is usef for QrCode scanning is typically only allowed on `localhost` and `https` connections!

## Licenses
This project includes and heavily uses the work from:
https://github.com/datalog/datamatrix-svg

```
    https://github.com/datalog/datamatrix-svg
	under MIT license
	# datamatrix.js has no dependencies
	Copyright (c) 2020 Constantine

```
Thank you for this library!

## Build Setup for Development

```bash
# install dependencies
$ npm install

# serve with hot reload at localhost:3000
$ npm run dev

# build for production and launch server
$ npm run build
$ npm run start

# generate static project
$ npm run generate
```

# VDA Labels
Find details here: [LabelFields.md](./LabelFields.md)