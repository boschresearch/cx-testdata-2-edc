<template>
  <div>
    <v-text-field v-model="fields['V']" label="Lieferantennummer des Verkäufers" hint="DI: V (potential CX Mapping - *with translation*: manufacturerId)"></v-text-field>
    <v-text-field v-model="fields['8V']" label="Empfängerwerk / Warenempfänger" hint="DI: 8V (potential CX Mapping - *with translation*: customerId)"></v-text-field>
    <v-text-field v-model="fields['P']" label="Artikelnummer / Sachnummer des Kunden / Teilenummer des Kunden" hint="DI: P (potential CX Mapping: customerPartId)"></v-text-field>
    <v-text-field v-model="fields['1P']" label="Sachnummer des Herstellers / Teilenummer des Lieferanten" hint="DI: 1P (potential CX Mapping: manufacturerPartId)"></v-text-field>
    <v-text-field v-model="fields['1T']" label="Charge / Chargennummer (1)" hint="DI: 1T (potential CX Mapping: partInstanceId)"></v-text-field>
    <v-text-field v-model="fields['1J']" label="Eindeutige Packstück-ID der innersten Verpackungsebene (Single Label)" hint="DI: 1J (potential CX Mapping: partInstanceId)"></v-text-field>

    <!--
    <v-text-field v-model="fields['3L']" label="Lieferantennummer des Warenversenders" hint="DI: 3L"></v-text-field>
    <v-text-field v-model="fields['2S']" label="Lieferscheinnummer" hint="DI: 2S"></v-text-field>
    -->

    <small>Not all possible fields available right now. This is a pre-selection.</small>

  </div>
</template>

<script>
export default {
    data() {
        return {
            fields: {},
        }
    },
    emits: ['fieldsChanged'],
    watch: {
        fields: {
            handler(newVal) {
                this.$emit('fieldsChanged', newVal)
            },
            deep: true
        }
    },

}
</script>

<style>

</style>