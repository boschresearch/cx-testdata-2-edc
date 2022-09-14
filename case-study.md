# Mapping VDA 4994 Global Transport Label

Reference:
https://www.vda.de/vda/de/aktuelles/publikationen/publication/vda-4994---global-transport-label---version-1.3-juni-2021

And more specifically the document in there called: 'Empfohlene DI in der Automobilindustrie'

## Direct Mapping
1P ('Teilenummer des Lieferanten') -> manufacturerPartId

P ( 'Teilenummer des Kunden') -> customerPartId

T1 ('Charge') -> partInstanceId (only for registry lookup with 'specificAssetIds')

## Mapping with Translation
V ('Lieferant') -> manufacturerId

8V ('Warenempfaenger') -> customerId

It should be considered to add those VDA Label numbers to the registry's 'specificAssetIds' list to avoid 'hard coded' mappings


# Potential CX-Id Transfer
Potentially, the following customer specific fields coudl be used to transfer e.g. the CX-Id:

11Z

12Z

...

20Z
