<template>
  <div :id="project.id"  class="project_container" v-for="project in store.state.projects" :key="project.id">
      <Project v-if="project.id == route.params.id"/>
  </div>
  <div class="small-screen-placeholder">
      Your current screen-size is not supported. Please switch to a bigger device or screen.
  </div>
  <!-- <Project  v-for="project in store.state.projects" :key="project.id" v-if="project.id == route.params.id"/> -->
</template>

<script setup>
    import Project from '../components/Project.vue'
    import { useStore } from 'vuex';
    import {useRoute} from 'vue-router';

    const route = useRoute();
    const store = useStore();
</script>

<style>
    .project_container{
        display: grid;
        grid-area: content;
        grid-template-columns: 1fr max(25vw, 235px);
        grid-template-rows: 7vh 85vh 1fr;
        grid-template-areas: 
        'hd hd'
        'main chat'
        'ft ft'
        ;
        overflow: hidden;
        /* z-index: 1; */
    }
    .project-container-active{
      z-index: 2;
    }
    .small-screen-placeholder{
      display: none;
      color: var(--neutral--400);
      text-align: center;
      font-feature-settings: 'liga' off;
      /* Heading XS/Regular */
      font-family: Montserrat;
      font-size: 1.5rem;
      font-style: normal;
      font-weight: 400;
      line-height: 2rem; /* 133.333% */
    }
    
    @media (max-width: 500px) {
        .project_container{
            display: none;
        }
        .small-screen-placeholder{
          grid-area: content;
          display: flex;
          justify-self: center;
          align-items: center;
        }
    }
</style>