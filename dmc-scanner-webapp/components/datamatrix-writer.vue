<template>
  <div>
    <v-btn @click="createCode()">Create</v-btn>
    <v-text-field v-model="inputData" label="Raw Input Data" :readonly="showFields" hint="e.g. [)>063L1234V56" />
    <v-checkbox v-model="showFields" label="Show individual Fields" />
    <div v-if="showFields">
        <dmc-fields @fieldsChanged="fieldsChanged"  />
        <br><br>
    </div>
    <div id="svgcontent" hidden></div>
    <h2>Data Matrix Code</h2>
    <div class="print_top_right_corner">
        <img class="print" id="myimg" width="256" height="256" />
        <object-table class="print" style="visibility: hidden;" :item="fields" />
    </div>
  </div>
</template>

<script>
import dmcFields from './dmc-fields.vue'

export default {
  components: { dmcFields },
    head() {
        return {
            script: [
                {
                    src: '../datamatrix.js'
                }
            ]
        }
    },
    data() {
        return {
            inputData: '',
            fields: {},
            showFields: false,
        }
    },
    methods: {
        fieldsChanged(newVal) {
            console.log(newVal)
            this.fields = newVal;
            const EOT = 4
            const GS = 29
            const RS = 30
            const prefix = "[)>" + String.fromCharCode(RS) + "06"
            const suffix = String.fromCharCode(RS) + String.fromCharCode(EOT)

            let main = ''
            Object.entries(newVal).forEach((item) => {
                main = main + String.fromCharCode(GS) + item.join('')
            })
            this.inputData = prefix + main + suffix
        },
        createCode() {
            var svgNode = DATAMatrix({
                msg :  this.inputData,
                dim :   256,
                rct :   0,
                pad :   2,
                pal : ["#000000", "#f2f4f8"],
                vrb :   0,

            })
            svgNode.setAttribute('id', 'svgdata')
            console.log(svgNode)
            const el = document.getElementById('svgcontent')
            el.childNodes.forEach((child) => {
                el.removeChild(child)
            })
            el.appendChild(svgNode)
            this.createPng(svgNode)
        },
        createPng(svg) {
            const data = (new XMLSerializer()).serializeToString(svg)
            const url = 'data:image/svg+xml,' + encodeURIComponent( data );

            const width = 256
            const height = 256
            const dummyCanvas = document.createElement('canvas')
            dummyCanvas.width = width
            dummyCanvas.height = height
            var dummyImg = new Image(width, height);

            dummyImg.onload = function () {
                let ctx = dummyCanvas.getContext('2d')
                ctx.drawImage(dummyImg, 0, 0, width, height);

                myimg.src = dummyCanvas.toDataURL("image/png");
            }
            dummyImg.src = url
        },
    }
}
</script>
