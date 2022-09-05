# Plattfomr i40 - Asset Administration Shell

Openapi specification can be found here:
https://app.swaggerhub.com/apis/Plattform_i40/Registry-and-Discovery/Final-Draft

Code can be generated with:
```
docker run --rm -v $PWD:/local openapitools/openapi-generator-cli generate -i /local/aas-registry-openapi.yaml -g python-fastapi -o /local/src/ --additional-properties=packageName=aas.registry
```

The relevant generated (and updated) code for this project can be found in /aas
