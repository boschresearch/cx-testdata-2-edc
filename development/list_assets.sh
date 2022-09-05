#!/bin/sh

curl -X GET http://provider-control-plane:9191/api/assets -H "X-Api-Key: 123456" -H "Content-Type: application/json" | jq