<template>
    <RouterView />
    <div id="overlay-block"></div>
    <CookieBanner />
</template>

<script setup>
import { RouterView } from 'vue-router';
import CookieBanner from './components/CookieBanner.vue';
</script>
