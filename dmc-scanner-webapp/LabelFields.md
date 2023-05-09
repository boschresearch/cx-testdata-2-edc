

# VDA Global Transport Labels

```
DI: menas 'Datenidentifikator' (~ data identifier, ~  a key word to identify the data)

S: means Specificiation: 'VDA 4994 - Global Transport Label V1p3 2021-06.pdf'

R: means Recommendation for Autotmotive Industry: 'Empfohlene DI in der Automobilindustrie.pdf'

CX: Means how to map to the Catena-X world
```

## Lieferant
```
DI: V

S: Lieferantennummer des Verkäufers

R: Lieferant

CX: TODO: Mapping -> 'manufacturerId' or new field

```

## Warenempfänger
```
DI: 8V

S: Empfängerwerk

R: Warenempfänger

CX: TODO: Mapping -> 'customerId' or new field
```

## Artikelnummer
```
DI: P

S: Artikelnummer / Sachnummer des Kunden
engl: CUSTOMER PART NUMBER

R: Teilenummer des Kunden

CX: 'customerPartId'
```

## Sachnummer des Herstellers
```
DI: 1P

S: Sachnummer des Herstellers
engl: -

R: Teilenummer des Lieferanten

CX: 'manufacturerPartId'
```

## Charge
```
DI: 1T

S: Charge

R: Chargennummer (1)

CX: 'partInstanceId' (in local Identifiers / specificAssetIds)
```

## Seriennummer
```
DI: 1J (Single Label)

S: Eindeutige Packstück-ID der innersten Verpackungsebene (Single Label)
engl: PACKSTÜCK-ID -> PACKAGE ID

R: License Plate - eindeutige ID des Packstücks

CX: 'partInstanceId' TODO: The whole field or only the last 9 digits wich are the actual SN part
```
This needs to be clarified!
The field is a concatination of multiple other fields.

### Example: UN 987654321 123456789

UN: Dun & Bradstreet

987654321: DUNS-Number

123456789: SN des Packstücks
