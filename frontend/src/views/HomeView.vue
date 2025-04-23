<script setup>
    import Sidebar from '../components/Sidebar.vue';
    import { useStore } from 'vuex';

    const store = useStore();
    store.commit('loadProjects');
</script>

<template>
    <Sidebar />
    <RouterView />
</template>



