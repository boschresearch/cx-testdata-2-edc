<!--
 Copyright (c) 2022 - Robert Bosch GmbH
 All rights reserved
-->
<template>
  <div>
    <zxing-reader @componentScanned="addComponent"></zxing-reader>
    <br>

    <div v-if="settings.endpoint">
        <v-btn @click="send()"><v-icon>mdi-send</v-icon> Send *</v-btn>
        <br>
        <p style="font-size:8px;">*) Sending data to: {{settings.endpoint}}</p>
        <br>
        <v-alert :type="messageType" v-if="message">{{message}}</v-alert>
        <br>
        <v-alert v-if="settings.apiKey" type="warning">
            <small>
            Beware, that transfering secrets in the settings via the b64 encoded URL param is NOT secure!
            Data is NOT encrypted and even though, it is not human readable, it is easily possible to re-construct it
            from the URL above! Meaning: Don't screenshot / record video / share to others who should not see it!
            </small>
        </v-alert>
    </div>
    <div v-else>
        <v-alert type="info">
            <small>A 'settings' query param must be provided to send data
                to a backend system.
                Please consult the application admin.</small>
        </v-alert>
    </div>

    <h2 v-if="components.sub">Sub Components: {{components.sub.length}}</h2>
    <h2 v-if="components.main">Main Component:</h2>
    <v-btn @click="deleteMain"><v-icon>mdi-trash-can-outline</v-icon></v-btn>
    <component-table :item="components.main" />
    <h2 v-if="components.sub">Sub Components ({{components.sub.length}})</h2>
    <v-btn @click="deleteSub"><v-icon>mdi-trash-can-outline</v-icon></v-btn>
    <div v-for="(item, idx) in components.sub" :key="idx">
        <h3>Component {{idx+1}}:</h3>
        <component-table :key="idx" :item="item" />
    </div>

  </div>
</template>

<script>
import { encode, decode } from 'base64url'
import zxingReader from '~/components/zxing-reader.vue';
import ComponentTable from '~/components/component-table.vue';

export default {
  components: { zxingReader, ComponentTable },
    data () {
        return {
            message: '',
            messageType: '',
            components: {
                main: [],
                sub: [],
            }
        }
    },
    computed: {
        settings() {
            try {
                const settings_b64 = this.$route.query['settings']
                //console.log(settings_b64)
                const settings_str = decode(settings_b64)
                //console.log(settings_str)
                const settings = JSON.parse(settings_str)
                //console.log(settings)
                return settings
            } catch {
                return { endpoint: '' }
            }
        },
    },
    methods: {
        addComponent(component) {
            console.log(component)
            this.clearMessage()
            if (Object.keys(this.components.main).length === 0) {
                // if main not set, the scan goes into main component
                this.components.main = component
            } else {
                // all consequent scans go into sub components
                console.log(component)
                this.components.sub.push(component)
            }
        },
        send() {
            console.log('send')
            if(this.settings.method == 'POST') {
                this.doPost()
            } else if(this.settings.method == 'FORWARD') {
                this.doForward()
            } else {
                this.message = "Unkonown settings.method: " + this.settings.method
                this.messageType = "error"
            }
        },
        async doPost() {
            let headers = {}
            if (this.settings.apiKeyName && this.settings.apiKeyValue) {
                headers[this.settings.apiKeyName] = this.settings.apiKeyValue
            }
            this.$axios.post(this.settings.endpoint, this.components, { 'headers': headers})
            .then((result) => {
                console.log(result)
                this.messageType = 'success'
                this.message = 'Data sent to the backend.'
                try {
                    this.message = this.message + ' aas_id: ' + result?.data?.aas_id + ' asset_id: ' + result?.data?.asset_id
                } catch {}
            })
            .catch((error) => {
                console.log(error)
                this.messageType = 'error'
                this.message = error + " " + error?.response?.data?.detail
            })
        },
        doForward() {
            const components_b64 = encode(JSON.stringify(this.components))
            const url = this.settings.endpoint + '?components=' + components_b64
            window.location.href = url
        },
        clearMessage() {
            this.message = ''
            this.messageType = 'info'
        },
        deleteMain() {
            this.components.main = []
        },
        deleteSub() {
            this.components.sub = []
        },
    },
};
</script>
