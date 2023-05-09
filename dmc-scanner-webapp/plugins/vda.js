
export const SUPPORTED_GTL3_PREFIXES = ['3L', 'V', '2S', 'P', '1T', '1P', 'J', '1J', '3J', '4J', '5J',
            '6J', '4L', '8V', '2L', '20L', 'Q', '3Q', '2Q', 'B', '14D']

export const DI_TO_HUMAN_READABLE = {
    '3L': 'LieferantenNummerWarenversender',
    'V': 'LieferantenNummerVerkaeufer',
    '2S': 'Lieferscheinnummer',
    'P': 'ArtikelNummer',
    '1T': 'Charge',
    '1P': 'SachnummerHersteller',
    'J': 'PacksteuckID',
    '1J': 'PacksteuckID',
    '3J': 'PacksteuckID',
    '4J': 'PacksteuckID',
    '5J': 'PacksteuckID',
    '6J': 'PacksteuckID',
    '4L': 'Ursprungsland',
    '8V': 'Warenempfaenger',
    '2L': 'Abladestelle',
    '20L': 'Lagerort',
    'Q': 'MengeAnzahlLadeeinheiten',
    '3Q': 'Masseinheit',
    '2Q': 'Bruttogewicht',
    'B': 'Packmutteltyp',
    '14D': 'Verfalldatum',
}

/**
 * Prepare from the group sepearator separated array. Which menas, the strings still contain the DI strings
 * @param {*} groups 
 * @returns 
 */
export function prepareDataStructure(groups) {
    let result = []
    console.log(groups)
    groups.forEach((group) => {
        SUPPORTED_GTL3_PREFIXES.forEach((prefix) => {
            if (!group.startsWith(prefix)) { return }
            const value = group.replace(prefix, '')
            const data = {}
            data['humanKey'] = DI_TO_HUMAN_READABLE[prefix]
            data['vdaKey'] = prefix
            data['value'] = value
            result.push(data)
        })
    })
    return result
}

/**
 * Prepare from already given key value list
 * @param {*} keyValueList 
 * @returns 
 */
export function prepareDataStructureFromArray(keyValueList) {
    let result = []
    // TODO: fix / improve this!
    Object.entries(keyValueList).forEach((kv) => {
        const data = {}
        data['humanKey'] = DI_TO_HUMAN_READABLE[kv[0]]
        data['vdaKey'] = kv[0]
        data['value'] = kv[1]
        result.push(data)
    })
    return result
}
