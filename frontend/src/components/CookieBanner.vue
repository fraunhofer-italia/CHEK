<template>
    <div v-if="showBanner" id="cookie-banner">
      <p class="banner-text">
        We use cookies to improve your experience. By continuing, you accept our &nbsp;
        <RouterLink :to="{ name: 'cookiePolicy' }" class="policy-link">cookie policy</RouterLink>.
      </p>
      <button @click="acceptCookies" class="accept-btn">Ok</button>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { RouterLink } from 'vue-router';
  
  const showBanner = ref(false);
  
  onMounted(() => {
    showBanner.value = localStorage.getItem('chek_cookiesAccepted') !== 'true';
  });
  
  function acceptCookies() {
    showBanner.value = false;
    localStorage.setItem('chek_cookiesAccepted', 'true');
  }
  </script>
  
  <style>
  #cookie-banner {
    position: fixed;
    bottom: 0;
    width: 100%;
    background-color: rgba(0, 0, 0, 0.8);
    color: white;
    text-align: center;
    padding: 1rem;
    z-index: 1050;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  
  .banner-text {
    font-family: Plus Jakarta Sans;
    font-size: 1.125rem;
    font-weight: 500;
    line-height: 1.75rem;
    color: var(--noble-black-300, #9B9C9E);
    margin: 0;
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
  }
  
  .policy-link {
    color: var(--heisenberg-blue-500, #82DBF7);
    text-decoration: underline;
    font-weight: 500;
  }
  
  .accept-btn {
    border-radius: var(--button-l, 0.75rem);
    background: var(--brand-600, #65BEDA);
    color: #f3f3f3;
    justify-content: center;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 1rem;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    cursor: pointer;
    border: none;
    outline: none;
  }
  </style>
  