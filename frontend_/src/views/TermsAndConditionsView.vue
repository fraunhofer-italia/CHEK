<script setup>
    import TermsAndConditions from '../components/TermsAndConditions.vue';
</script>

<template>
    <div class="full-screen">
        <TermsAndConditions />

    </div>
</template>

<style scoped>
.full-screen {
  position: fixed; /* Take the element out of the grid layout */
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: flex-start; /* Align items at the top */
  padding: 20px; /* Optional: Space at the top */
  overflow: auto;
}

</style>