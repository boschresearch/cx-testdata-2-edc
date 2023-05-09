<template>
  <div>
    <v-text-field v-model="settings.endpoint" label="Destination Endpoint" />
    <v-text-field v-if="settings.method == 'POST'" v-model="settings.apiKeyName" label="Http Header Key" hint="Header name for the API key field, e.g. X-Api-Key" />
    <v-text-field v-if="settings.method == 'POST'" v-model="settings.apiKeyValue" label="Http Header Value" hint="Can be used for transferring a secret / API key" />
    <v-select
        v-model="settings.method" 
        label="Method"
        :items="[{'id': 'POST', name: 'POST to endpoint'}, {'id': 'FORWARD', name: 'FORWARD with query param (GET)'}]"
        item-text="name"
        item-value="id"
        item-key="id"
    />
    <v-btn @click="generate()"><v-icon>mdi-cog-sync</v-icon> Generate</v-btn>
    <br>
    Link:<br>
    <NuxtLink v-if="url.query.settings" :to="url">{{url.query.settings}}</NuxtLink>
    <v-alert type="info" v-if="url.query.settings">
        Distribute this link to everyone who is allowed to scan and send data to your backend.
        Keep in mind: the API key might not be human readable, but is machine readable.
        This means: don't distribute the Link to someone who should NOT be able to see the API key!
    </v-alert>
  </div>
</template>

<script>
import { encode } from 'base64url'

export default {
    data () {
        return {
            url: { name: 'scan', query: { settings: '' } },
            settings: {
                endpoint: 'http://localhost',
                apiKeyName: 'X-Api-Key',
                apiKeyValue: '',
                method: 'POST',
            }
        }
    },
    methods: {
        generate () {
            console.log('generate')
            const b64_settings = encode(JSON.stringify(this.settings))
            console.log(this.settings)
            console.log(b64_settings)
            this.url['query']['settings'] = b64_settings
        }
    }

}
</script>

<style>

</style>