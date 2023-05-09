<!--
 Copyright (c) 2022 - Robert Bosch GmbH
 All rights reserved
-->
<template>
  <div>
    <v-btn :disabled="scanningOngoing" @click="scan"><v-icon>mdi-camera</v-icon>Scan</v-btn>
    <v-btn @click="stopScanning"><v-icon>mdi-cancel</v-icon>Stop scanning</v-btn>
    <v-btn :disabled="scanningOngoing" @click="listCameras"><v-icon>mdi-reload</v-icon>List available cameras</v-btn>
    <v-select v-if="cameras.length > 0" label="Choose Camera" v-model="selectedCamera" :items="cameras" item-text="label" item-value="id" item-key="id" />
    <br><br>
    <v-textarea outlined v-model="qrcode.data" label="QR Code Content" />
    <video style='border: 1px solid black;' id="cam" width="50%"></video>
    <!-- or upload a file -->
    <v-file-input v-model="image" accept="image/*" label="Upload a label"></v-file-input>
    <v-img id="imgLabel" :src="imageUrl" ></v-img>
    <v-btn :disabled="!imageUrl" @click="scanFromPicture"><v-icon>mdi-qrcode</v-icon>Scan from picture</v-btn>
    <br>
    <v-btn @click="makeMainComponent"><v-icon>mdi-equal</v-icon>Make Main Component</v-btn>
    <v-btn @click="addChildComponent"><v-icon>mdi-plus</v-icon>Add Child Component</v-btn>
  </div>
</template>

<script>
import QrScanner from 'qr-scanner'

export default {
    data () {
        return {
            image: null,
            qrcode: {data: ''},
            qrScanner: null,
            cameras: [],
            selectedCamera: '',
            scanningOngoing: false,
            mainComponent: {},
            childComponents: [],
        }

    },
    computed: {
        imageUrl() {
            if(!this.image) return null
            const img = URL.createObjectURL(this.image)
            console.log(img)
            return img
        }
    },
    methods: {
        scan() {
            this.scanningOngoing = true
            var cam = document.getElementById('cam')
            var camId = this.selectedCamera || ''
            this.qrScanner = new QrScanner(
                cam,
                result => {
                     console.log('decoded qr code:', result)
                     this.qrcode = result
                     this.qrScanner.stop()
                     this.scanningOngoing = false
                },
                {'highlightScanRegion': true, 'preferredCamera': camId }
            );
            this.qrScanner.start()
        },
        stopScanning() {
            this.qrScanner.stop()
            this.scanningOngoing = false
        },
        async listCameras() {
            this.cameras = await QrScanner.listCameras(true);
        },
        scanFromPicture() {
            const image = document.getElementById('imgLabel')
            QrScanner.scanImage(this.imageUrl, {'returnDetailedScanResult': true})
                .then(result => console.log(result))
                .catch(error => console.log(error || 'No QR code found.'));
        },
        makeMainComponent() {
            var j = JSON.parse(this.qrcode.data)
            this.mainComponent = j
        },
        addChildComponent() {
            var j = JSON.parse(this.qrcode.data)
            this.childComponents.push(j)
        },
    }
    
}
</script>

<style>

</style>