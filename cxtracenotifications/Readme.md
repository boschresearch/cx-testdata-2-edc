# Introduction
Implementation of:
https://confluence.catena-x.net/display/ARTV/%28TRS%29+Quality+Notification+Endpoints+and+EDC+Contract+Offerings

and Unqiuqe ID Push
https://confluence.catena-x.net/display/BDPQ/%28TRS%29+Unique+ID+Push+Notifications

https://confluence.catena-x.net/download/attachments/81691003/traceability-unique-id-push-cx-release-openapi-v1.0.0.yaml?version=1&modificationDate=1678353599139&api=v2

# Doc / Spec
http://localhost:8080/docs#/


# Dev
## codegen
```
pip install datamodel-code-generator
```
```
datamodel-codegen --input traceability-unique-id-push-cx-release-openapi-v1.0.0.yaml --output models_unique_push.py --base-class models.MyBaseModel

datamodel-codegen --input quality-notification-cx-release-2-PI4-openapi.yaml --output notifications_model.py --base-class models.MyBaseModel
```

## Swagger / Openapi Editor
```
docker run -d -p 5000:8080 swaggerapi/swagger-editor
```