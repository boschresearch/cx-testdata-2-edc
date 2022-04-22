#!/bin/sh

#curl -X GET http://provider-control-plane:9191/api/assets/urn:uuid:754095ca-33d5-4da9-bb55-c8a22286f53durn:uuid:4f83f36e-8b62-4339-9a91-e4281d7127a9 -H "X-Api-Key: 123456" -H "Content-Type: application/json" | jq
curl -X DELETE http://provider-control-plane:9191/api/assets/yyyyy -H "X-Api-Key: 123456" -H "Content-Type: application/json" | jq