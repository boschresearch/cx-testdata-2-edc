<!--
 Copyright (c) 2022 - Robert Bosch GmbH
-->
<template>
  <div>
    <v-textarea outlined v-model="qrcodeContent" label="QR Code Content" />

    <v-btn @click="create" ><v-icon>mdi-qrcode</v-icon> Create</v-btn>
    <v-btn @click="shrinkJsonContent" ><v-icon>mdi-scissors-cutting</v-icon> Shrink JSON</v-btn>
    <v-btn @click="print" ><v-icon>mdi-printer</v-icon> Print</v-btn>
    <br>
    <canvas class="print" id="qrcanvas"></canvas>
  </div>
</template>

<script>
import QRCode from 'qrcode'

export default {
    data () {
        return {
            qrcodeContent: `
            [ {
                "value" : "BPNL00000003B5MJ",
                "key" : "ManufacturerId"
            }, {
                "value" : "66928C1-04",
                "key" : "ManufacturerPartId"
            }, {
                "value" : "NO-725118006090887311773452",
                "key" : "PartInstanceId"
            } ]
            `
        }
    },
    methods: {
        create() {
            console.log('create')
            var canvas = document.getElementById('qrcanvas')

            QRCode.toCanvas(canvas, this.qrcodeContent, function (error) {
                if (error) console.error(error)
                console.log('success!');
            })
        },
        shrinkJsonContent() {
            var content = this.qrcodeContent
            try {
                var j = JSON.parse(content)
                var trimmed = JSON.stringify(j)
                this.qrcodeContent = trimmed
            } catch {
                console.log('Could not trim spaces out of content. Not Json?')
            }
            this.create()
        },
        print() {
            window.print()
        },
    }
}
</script>

<style>

</style>