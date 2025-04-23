<template>
    <div id="welcome-div">
        <div id="welcome-text-container">
            <div class="welcome-class" id="welcome-header">
                Hello, {{userinfo.first_name}}!
            </div>
            <div class="welcome-class" id="welcome-subtext">
              Welcome to CHEK Virtual Assistant for Digital Building Permit! <br>
              Take charge of your building permit evolution effortlessly with our step-by-step guidance.
            </div>
        </div>
        <!-- <div id="img-container"></div> -->        
        <img id="welcome-img" src="./images/workflow_homepage.png" alt="Workflow-Image">
        
        <div id="welcome-footer">
          <div class="basic-ui-button" @click="showModal = true">
              Start new Project 
            <span class="chevron-right"></span>
          </div>
        </div>
        
        <CreateProjectModal :show-modal="showModal" @close="showModal = false" title="Start New Project"></CreateProjectModal>

    </div>

</template>

<script setup>
    import CreateProjectModal from "./CreateProjectModal.vue";
    import {ref, onBeforeMount} from "vue";

    const userinfo = ref();
    const showModal = ref(false);

    onBeforeMount(() => {
        userinfo.value =  JSON.parse(window.sessionStorage.getItem("chek_user_info")); 
        console.log(userinfo.value);
    })

</script>

<style>
  #welcome-div{
    grid-area: content;
    /* display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6.25rem; */
    display: flex;
    /* padding: 4rem 3.125rem; */
    margin: 2vh 2vw;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    /* gap: 6.25rem; */
    /* flex: 1 0 0; */
    align-self: stretch;
  }
 #welcome-text-container{
    flex-direction: column;
    align-self: stretch;
    max-width: 100%;
  }

  .welcome-class{
    padding: 0.5rem;
  }

  #welcome-footer{
    display: flex;
    align-self: flex-end;
  }
  /* #img-container{
    display: flex;
    flex: auto;
    width: 100%;
    height: auto;
    background-image: url(images/workflow_homepage.png);
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    max-width:100%;
    max-height:100%;
  } */
  #welcome-img{
    display: block;
    max-width: 100%; /* Image will scale down if the container is too small */
    height: auto; /* Maintain aspect ratio */
  }

  #welcome-header{
    /* flex-shrink: 0; */
    color: var(--brand--700);
    text-align: center;
    font-feature-settings: 'liga' off;
    /* Heading L/Bold */
    font-family: Montserrat;
    /* font-family: Arial, Helvetica, sans-serif; */
    font-size: 3rem;
    font-style: normal;
    font-weight: 700;
    line-height: 3.75rem; /* 125% */
    letter-spacing: -0.06rem;
  }

  #welcome-subtext{
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

    .basic-ui-button{
    /* Layout */
    display: flex;
    flex-direction: row;
    width: 15.625rem;
    height: 3rem;
    padding: 0rem var(--button-padding-l, 1.25rem);
    justify-content: center;
    justify-items: center;
    align-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--button-gap-l, 0.625rem);
    /* Style */
    border-radius: var(--button---l, 0.75rem);
    background: var(--neutral--500, #6F7786);
    /* Typography */
    color: var(--neutral-0, var(--noble-black-0, #FFF));
    font-feature-settings: 'liga' off;
    /* Button/L */
    font-family: Arial, Helvetica, sans-serif;
    font-size: 1rem;
    font-style: normal;
    font-weight: 650;
    line-height: normal;
    cursor: pointer;
  }

  span.chevron-right{
    display: flex;
    background:  center / contain no-repeat url('./images/chevron-right-white.svg');
    /* justify-content: center;
    align-items: center; */
    width: 1rem;
    height: 1rem;  
  }

</style>