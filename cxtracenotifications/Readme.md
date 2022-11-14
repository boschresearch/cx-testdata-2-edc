# Introduction
Implementation of:
https://confluence.catena-x.net/display/ARTV/%28TRS%29+Quality+Notification+Endpoints+and+EDC+Contract+Offerings

# Doc / Spec
http://localhost:8080/docs#/


# Dev
## codegen
```
datamodel-codegen --input quality-notification-cx-release-2-PI4-openapi.yaml --output notifications_model.py
```

## Swagger / Openapi Editor
```
docker run -d -p 5000:8080 swaggerapi/swagger-editor
```