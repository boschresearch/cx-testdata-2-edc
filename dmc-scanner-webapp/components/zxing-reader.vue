<template>
  <div>

    <v-tabs>
        <v-tab>
            <v-icon>mdi-camera-plus</v-icon>&nbsp;Camera
        </v-tab>
        <v-tab>
            <v-icon>mdi-panorama-variant</v-icon>&nbsp;Upload
        </v-tab>
        <v-tab>
            <v-icon>mdi-text-box-plus</v-icon>&nbsp;Manual Input
        </v-tab>

        <v-tab-item>
            <div>
                <v-btn @click="scanFromCamera"><v-icon>mdi-camera</v-icon>Scan from Camera</v-btn>
                <v-btn @click="stopCam"><v-icon>mdi-camera-off</v-icon></v-btn><br>
                <video :hidden="!videoScanningInProgress" autoplay id="vid" width="60%" style="border: 1px solid gray" muted="muted"></video>
                <v-select label="Choose Camera" v-model="selectedDeviceId" :items="videoinputDevices" item-text="label" item-value="deviceId" item-key="deviceId" />
            </div>
        </v-tab-item>
        <v-tab-item>
            <div>
                <v-file-input v-model="image" accept="image/*" label="Upload a label"></v-file-input>
                <img id="imgLabelDm"  :hidden="!imageUrl" :src="imageUrl" width="100%"><img>
                <v-btn @click="drawOnCanvas" v-if="error">Mark Code on Image</v-btn>
                <canvas id="mycanvas" @mousedown="canvasMousedown" @mouseup="canvasMouseup" width="300" />
                <canvas id="extractedImage" />
            </div>
        </v-tab-item>
        <v-tab-item>
            <div>
                <dmc-fields @fieldsChanged="manualInputFieldsChanged" />
                <v-btn @click="manualAdd"><v-icon>mdi-plus</v-icon>Scan / Add</v-btn>
                <br><br>
            </div>
        </v-tab-item>
    </v-tabs>
    <v-alert v-if="error" type="error">{{error}}</v-alert>
    <div v-if="showResult">
        <v-text-field v-model="codeScanValue" readonly />
    </div>
  </div>
</template>

<script>
import { BrowserDatamatrixCodeReader } from '@zxing/browser'
import { DecodeHintType } from '@zxing/library'
import dmcFields from './dmc-fields.vue'
import { SUPPORTED_GTL3_PREFIXES, DI_TO_HUMAN_READABLE, prepareDataStructure, prepareDataStructureFromArray } from '../plugins/vda'

export default {
  components: { dmcFields },
    props: {
        showResult: Boolean,
    },
    emits: ['componentScanned'],
    data() {
        return {
            error: '',
            usePictureUpload: false,
            image: null,
            imageMaxSize: 500,
            imageRectStartX: 0,
            imageRectStartY: 0,
            imageRectEndX: 0,
            imageRectEndY: 0,
            videoinputDevices: [],
            videoScanningInProgress: false,
            selectedDeviceId: '',
            codeScanValue: '',
            noResult: '',
            stream: null,
            groups: [],
            manualInputFields: {},
        }
    },
    computed: {
        imageWidth() {
            try {
                const img = document.getElementById('imgLabelDm')
                const width = img.width
                return width
            } catch {
                return 0
            }
        },
        imageUrl() {
            if(this.image === null || this.image === undefined || this.iamge === '') return null
            const img = URL.createObjectURL(this.image)
            console.log(img)
            return img
        }
    },
    watch: {
        /**
         * select first element of the list of devices automatically
         */
        videoinputDevices(newVal, oldVal) {
            try {
                this.selectedDeviceId = newVal[0].deviceId
            } catch {}
        },
        /**
         * Most of this should go into a separate library
         * Parsing VDA 4994 into other data structure
         */
        codeScanValue(newVal) {
            if(newVal === '' || newVal === null || newVal === undefined) { return }
            console.log(newVal)
            const records = this.codeScanValue.split(String.fromCharCode(30)) // RS - Record Separator
            const groups = records[1].split(String.fromCharCode(29)) // GS - Group Separator
            this.groups = groups

            // prepare data structure
            let result = prepareDataStructure(groups)

            this.clenaupAfterGoodScan()
            this.$emit('componentScanned', result)
        },
        imageUrl(newVal) {
            if (newVal === null || newVal === undefined || newVal ==='') { return }
            this.scanFromPicture()
        }
    },
    async mounted() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({video: true, audio: false}) // get user consent first
            BrowserDatamatrixCodeReader.listVideoInputDevices()
                .then((devices) => {
                    this.videoinputDevices = devices
                })
                .catch((error) => {
                    console.log(error)
                })
                .finally(() => {
                    // in any case, let us relase the stream again (turn off camera (light) again )
                    this.stream.getTracks().forEach((track) => {
                        track.stop()
                    })
                })
        } catch (ex) {
            this.error = 'Could not fetch list of camera devices. Pherhaps no camera available or in use by other applications. You can still upload a picture of a code.'
        }
    },
    methods: {
        manualAdd() {
            // prepare data structure
            let result = prepareDataStructureFromArray(this.manualInputFields)
            this.$emit('componentScanned', result)
        },
        manualInputFieldsChanged(data) {
            console.log(data)
            this.manualInputFields = data
        },
        scanFromPicture() {
            this.error = ''
            const hints = new Map();
            hints.set(DecodeHintType.TRY_HARDER, true)
            const reader = new BrowserDatamatrixCodeReader(hints)
            //const imageEl = document.getElementById('imgLabelDm')
            
            reader.decodeFromImageElement('imgLabelDm')
                .then((result) => {
                    this.codeScanValue = result.text
                })
                .catch((error) => {
                    console.log(error)
                    this.error = 'Could not read code. Error: ' + error
                })
        },
        scanFromCanvas() {
            this.error = ''
            const hints = new Map()
            hints.set(DecodeHintType.TRY_HARDER, true)
            const reader = new BrowserDatamatrixCodeReader(hints)
            const canvas = document.getElementById('extractedImage')
            
            try {
                const result = reader.decodeFromCanvas(canvas)
                console.log(result)
                this.codeScanValue = result.text
            } catch (exception) {
                console.log(exception)
                this.error = 'Could not read code. Error: ' + exception
            }
        },
        async scanFromCamera() {
            this.error = ''
            this.videoScanningInProgress = true
            /**
            const enabledFormats = [
                BarcodeFormat.DATA_MATRIX,
            ];
             */
            const hints = new Map();
            //hints.set(DecodeHintType.POSSIBLE_FORMATS, enabledFormats);
            hints.set(DecodeHintType.TRY_HARDER, true)
            const reader = new BrowserDatamatrixCodeReader(hints)
            
            const vid = document.getElementById('vid')
            reader.decodeOnceFromVideoDevice(this.selectedDeviceId, vid)
                .then((result) => {
                    this.codeScanValue = result.text
                    this.stopCam()
                })
                .catch((error) => {
                    console.log(error)
                })
        },
        stopCam() {
            console.log('stop cam')
            // Developer documentation for how to close/stop a stream
            // https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack/stop
            try {
                const vid = document.getElementById('vid')
                const stream = vid.srcObject
                stream.getTracks().forEach((track) => {
                    track.stop()
                })
                vid.srcObject = null
            } catch(error) {
                console.log(error)
            } finally {
                this.videoScanningInProgress = false
            }
        },
        drawOnCanvas() {
            const img = document.getElementById('imgLabelDm')
            const canvas = document.getElementById('mycanvas')
            canvas.width = img.width
            canvas.height = img.height
            const ctx = canvas.getContext('2d')
            ctx.drawImage(img, 0, 0, img.width, img.height)
        },
        canvasMousedown(event) {
            console.log(event)
            this.imageRectStartX = event.x
            this.imageRectStartY = event.y
        },
        canvasMouseup(event) {
            console.log(event)
            this.imageRectEndX = event.x
            this.imageRectEndY = event.y
            this.drawCanvasRect()
        },
        drawCanvasRect() {
            const canvas = document.getElementById('mycanvas')
            const canvasBoundingRect = canvas.getBoundingClientRect()

            const ctx = canvas.getContext('2d')
            ctx.beginPath()
            const startX = this.imageRectStartX - canvasBoundingRect.left
            const startY = this.imageRectStartY - canvasBoundingRect.top
            const width = this.imageRectEndX - canvasBoundingRect.left - startX
            const height = this.imageRectEndY - canvasBoundingRect.top - startY
            ctx.rect(
                startX,
                startY,
                width,
                height)
            ctx.stroke()

            const extractedImageData = ctx.getImageData(startX, startY, width, height)
            console.log(extractedImageData)
            
            const extractedImageCanvas = document.getElementById('extractedImage')
            extractedImageCanvas.width = width
            extractedImageCanvas.height = height
            const hiddenCtx = extractedImageCanvas.getContext('2d')
            
            hiddenCtx.putImageData(extractedImageData, 0, 0)
            this.scanFromCanvas()
        },
        clenaupAfterGoodScan() {
            this.error = ''
            this.image = null
            this.codeScanValue = ''

            const canvas = document.getElementById('mycanvas')
            if (canvas !== null) {
                canvas.getContext('2d').clearRect(0,0, canvas.width, canvas.height)
            }
            const extractedImageCanvas = document.getElementById('extractedImage')
            if (extractedImageCanvas !== null) {
                extractedImageCanvas.getContext('2d').clearRect(0,0, canvas.width, canvas.height)
            }
        },
    }
}
</script>
