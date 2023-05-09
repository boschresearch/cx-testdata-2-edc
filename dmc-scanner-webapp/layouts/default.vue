<!--
 Copyright (c) 2022 - Robert Bosch GmbH
 All rights reserved
-->
<template>
  <v-app>

    <v-app-bar
      app
      color="primary"
      dark
    >
      <v-btn :to="{ name: 'index' }" text>Traceability-CS</v-btn>
      <v-spacer></v-spacer>

      <v-toolbar-items>
      </v-toolbar-items>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
    </v-app-bar>

      <v-navigation-drawer v-model="drawer" app>
          <v-list>
                <v-list-item link :to="{name: 'scan' }">
                    <v-icon>mdi-camera</v-icon><p>&nbsp;</p>
                    <v-list-item-title>Scan</v-list-item-title>
                </v-list-item>
                <v-list-item link :to="{ name: 'create' }">
                    <v-icon>mdi-qrcode</v-icon><p>&nbsp;</p>
                    <v-list-item-title>Create</v-list-item-title>
                </v-list-item>
                <v-list-item link :to="{ name: 'license' }">
                    <v-icon small>mdi-copyright</v-icon><p>&nbsp;</p>
                    <v-list-item-title><small>License</small></v-list-item-title>
                </v-list-item>

            </v-list>
      </v-navigation-drawer>

    <v-main class="ma-5">
      <nuxt />
    </v-main>
  </v-app>
</template>

<script>

export default {
  name: 'App',

  components: {
  },

  data: () => ({
    drawer: null
  })

}
</script>
