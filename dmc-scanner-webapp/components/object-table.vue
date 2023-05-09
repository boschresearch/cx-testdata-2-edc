<template>
  <div>
    <v-data-table
        :headers="[{text: 'Field', value: 'key'}, { text: 'Value', value: 'value'}]"
        :items="Object.entries(item).map( (entry) => { return { 'key': entry[0], 'value' : entry[1]} } )"
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
        'item': {}
    }

}
</script>

<style>

</style>