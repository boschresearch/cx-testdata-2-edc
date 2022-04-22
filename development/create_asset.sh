#!/bin/sh

#curl -X POST http://provider-control-plane:9191/api/assets -H "X-Api-Key: 123456" -H "Content-Type: application/json" -d "@./asset1.json"
curl -X POST http://provider-control-plane:9191/api/assets -H "X-Api-Key: 123456" -H "Content-Type: application/json" -d "@./create_asset.json"
#curl -X POST http://provider-control-plane:9191/api/assets -H "Content-Type: application/json" -d "@./asset1.json"

#curl -X GET http://provider-control-plane:9191/api/assets/asset-3
#curl -X GET http://provider-control-plane:9191/api/assets -H "X-Api-Key: 123456" -H "Content-Type: application/json"