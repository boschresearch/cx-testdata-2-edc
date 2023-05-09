<template>
  <div>
    <v-data-table
        :headers="[{ text: 'VDA Key', value: 'vdaKey'}, { text: 'Human Readable Key', value: 'humanKey'}, { text: 'Value', value: 'value'}]"
        item-key="vdaKey"
        :items="item"
        disable-pagination
        disable-filtering
        disable-sort
        hide-default-footer
    />
  </div>
</template>

<script>
export default {
    props: {
        'item': []
    }

}
</script>

<style>

</style>