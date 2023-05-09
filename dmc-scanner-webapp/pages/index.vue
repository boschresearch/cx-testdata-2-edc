<!--
 Copyright (c) 2022 - Robert Bosch GmbH
 All rights reserved
-->
<template>
  <div>
    Create and scan Data Matrix Codes (DMC) in the form of
    <br>
    <a target="_blank" href="https://www.vda.de/vda/de/aktuelles/publikationen/publication/vda-4994---global-transport-label---version-1.3-juni-2021">VDA 4994 - Global Transport Label - Version 1.3 Juni 2021</a>
    <br>
    and later also
    <br>
    <a target="_blank" href="https://www.vda.de/vda/de/aktuelles/publikationen/publication/vda-4992---mat-label-und-emat-datenaustausch">VDA 4992 - MAT Label und eMAT Datenaustausch</a>
    <br>
    <br>
    <b>Get started here:</b>
    <br>
    <nuxt-link :to="{ name: 'scan' }">Read DMC</nuxt-link> (needs permissions to use the Camera to read the code)
    <br>
    <nuxt-link :to="{ name: 'create' }">Create DMC</nuxt-link>
  </div>
</template>

<script>
</script>
