<template>
  <div id="sidebar" class="box sidebar-base">
    <!-- HEADER -->
    <div id="sidebar-head" class="sidebar-box">
      <div id="user-icon">
        {{ userinfo.first_name.charAt(0).toUpperCase() }}
      </div>
      <div id="user-info-txt-box">
        <div id="username">
          {{ userinfo.first_name.toUpperCase() }}
        </div>
        <div id="userinfo">
          {{ userinfo.country }}
        </div>
      </div>
      
      <RouterLink :to="{name: 'welcome'}" @click="unselectProject">
        <div id="home-btn"></div>
      </RouterLink>

    </div>

    <!-- PROJECTS LIST -->
    <div class="sidebar-projects">
      <div class="project-label-wrapper">
        <div class="projects-label">MY PROJECTS</div>
        <button class="update-btn" @click="showUpdateProjectsModal=true" title="Change or delete projects"></button>
        <button class="create-btn" @click="showCreateProjectModal=true" title="Start new project"></button>
      </div>
      
      <div id="project-list-container" @click="selectProjectClick">
        <div v-if="!store.state.projects" class="empty-project-list">
            No projects
        </div>
        <div v-else :id="`li_${project.id}`" class="project-list-item" v-for="project in store.state.projects" :key="project.id">
          <RouterLink :to="{path:`/projects/${project.id}`}">
            <span class="file-folder-icon"></span> 
            <div class="project-name">
              {{ project.name }}
            </div>
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- TOGGLE-ARROW -->
    <button id="arrow-inward" class="collapsable" title="Collapse sidebar" @click="toggleSidebar"></button>

    <!-- FOOTER -->
    <div id="sidebar-foot">
      <!-- <div class="footer-btn">
        <span class="settings-icon"></span>
        <div class="footer-btn-label">Settings</div>
      </div> -->
      <div class="footer-btn" @click="logoutUser">
        <span class="logout-icon"></span>
        <div class="footer-btn-label">Logout</div>
      </div>
      <RouterLink :to="{name: 'impressum'}">
        <div class="footer-btn">
          <span class="briefcase-icon"></span>
          <div class="footer-btn-label">Impressum</div>
        </div>
      </RouterLink>
      <RouterLink :to="{name: 'termsAndConditions'}">
        <div class="footer-btn">
          <span class="briefcase-icon"></span>
          <div class="footer-btn-label">Terms And Conditions</div>
        </div>
      </RouterLink>
      <RouterLink :to="{name: 'cookiePolicy'}">
        <div class="footer-btn">
          <span class="briefcase-icon"></span>
          <div class="footer-btn-label">Privacy & Cookie Policy</div>
        </div>
      </RouterLink>
      <div id="logo-container">
        <img src="./images/eu_icon.png"/>
        <img src="./images/favicon.svg"/>
        <img src="./images/fhi_icon.png"/>
      </div>
    </div>
  </div>

  <UpdateProjectsModal v-if="showUpdateProjectsModal" @close="showUpdateProjectsModal =false"/>
  <CreateProjectModal :show-modal="showCreateProjectModal" @close="showCreateProjectModal = false" title="Start New Project"></CreateProjectModal>

</template>


<script setup>
    import { RouterLink, useRouter, useRoute, onBeforeRouteLeave} from 'vue-router';
    import {ref, onBeforeMount, inject, nextTick, watch } from 'vue';
    import { useStore } from 'vuex';

    import UpdateProjectsModal from './UpdateProjectsModal.vue';
    import CreateProjectModal from "./CreateProjectModal.vue";


    const router = useRouter();
    const route = useRoute();

    const store = useStore();

    const base_api = inject('base_api');
    const logout_api = base_api +"/logout";

    const showUpdateProjectsModal = ref(false);
    const showCreateProjectModal = ref(false);


    let current_project = null;
    let current_project_content = null;

    const userinfo = ref();

    onBeforeMount(()=>{
        userinfo.value =  JSON.parse(window.sessionStorage.getItem("chek_user_info"));
    })

    watch(() => store.state.projects, () => {
        nextTick(() => {
          selectCurrentProject();
        });
        }, 
        { immediate: true }
    );

    function selectCurrentProject(){
        if (current_project){
            current_project.classList.toggle('active-project');
            const current_project_name = current_project.querySelector('.project-name');
            current_project_name.classList.toggle('active-project-name');

            current_project_content.classList.toggle('project-container-active');
        }
        if(route.params.id){
            const project_list_item = document.getElementById(`li_${route.params.id}`);
            project_list_item.classList.add('active-project');
            const project_name = project_list_item.querySelector('.project-name');
            project_name.classList.toggle('active-project-name');
            current_project = project_list_item;

            const project_container = document.getElementById(route.params.id);
            project_container.classList.toggle('project-container-active');
            current_project_content = project_container;
        }
    }

    function selectProjectClick(event) {
        let parent;
        const parent1 = event.target.parentElement;
        const parent2 = event.target.parentElement.parentElement;
        if(parent1.classList.contains('project-list-item') && !parent1.classList.contains('active-project')){
          parent = parent1;
        }
        else if(parent2.classList.contains('project-list-item') && !parent2.classList.contains('active-project')){
          parent = parent2;
        }
        else{
          return;
        }

        const proj_id = parent.id.replace("li_","");
        const project_container = document.getElementById(proj_id);

        if (current_project){
            current_project.classList.toggle('active-project');
            const current_project_name = current_project.querySelector('.project-name');
            current_project_name.classList.toggle('active-project-name');

            current_project_content.classList.toggle('project-container-active');
        }
        
        parent.classList.add('active-project');
        const project_name = parent.querySelector('.project-name');
        project_name.classList.toggle('active-project-name');
        current_project = parent;
        
        project_container.classList.toggle('project-container-active');
        current_project_content = project_container;
    }

    function unselectProject(){
        if (current_project){
            const current_project_name = current_project.querySelector('.project-name');
            current_project_name.classList.toggle('active-project-name');
            current_project.classList.toggle('active-project');
            current_project = null;
        }
    }

    function toggleSidebar(){
        const sidebar = document.getElementById("sidebar");
        sidebar.classList.toggle("collapsed");
    }
    
    async function logoutUser(){
        fetch(logout_api, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {'Content-Type': 'application/json',
                            'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`},
        })
        .then(response => {
            if(response.ok){
                console.log("Logout sucessfull!");
            }else{
                console.log(`status: ${response.status} - ${response.statusText}`)
            }
        })
        .catch(error =>{
            console.log(error);
        })
        .finally(() => {
            store.commit("unloadProjects");
            userinfo.value = null;
            window.sessionStorage.removeItem('chek_user_info');
            window.sessionStorage.removeItem('chek_access_token');
            router.push("/login");
        }); 
    }

</script>


<style>
#sidebar{
    grid-area: sd;
    display: flex;
    flex-direction: column;
    transition: 
      min-width 1s ease,
      width 1s ease,
      padding 1s ease,
      margin 1s ease;
}

.sidebar-base{
    padding: 1.5rem 0.9375rem;
    justify-content: flex-start;
    width: 15vw;
    min-width: 180px;
    /* max-width: 300px; */
}

.collapsed{
  padding: 0 0.2rem;
  width: 1.5rem;
  min-width: 1.5rem;
  justify-content: center;
  align-items: center;
}

#sidebar.collapsed > div {
  display: none;
}

#sidebar.collapsed > button {
  /* margin-top: 1rem; */
  margin: 0;
  -webkit-transform: rotateY(180deg);
            transform: rotateY(180deg);
}

    #sidebar-head{
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
      align-self: stretch;
      gap:1rem;
      padding: 0 0.62rem 1rem;
      border-bottom: 1px solid var(--neutral--500);
    } 

      a{
        display: flex;
        text-decoration: none;
        flex-direction: row;
        justify-content: flex-start;
        align-items: center;
        gap: 0.5rem;
        overflow: hidden;
      }

      #user-icon{
        display: flex;
        width: 2.5rem;
        height: 2.5rem;
        flex-direction: column;
        justify-content: center;
        flex-shrink: 0;

        border-radius: 50%;
        /* border-radius: var(--full, 624.9375rem); */
        border: 2px solid var(--heisenberg-blue-600);
        background: var(--heisenberg-blue-100);

        color: var(--heisenberg-blue-700);
        text-align: center;
        font-feature-settings: 'liga' off;
        /* Paragraph M/Bold */
        font-family: Plus Jakarta Sans;
        font-size: 1.25rem;
        font-style: normal;
        font-weight: 700;
        line-height: 1.5rem; /* 150% */
      }

      #user-info-txt-box{
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.25rem;
        overflow: hidden;
        flex: 1;
      }
        #username{
        color: var(--neutral--700);
        text-align: center;
        /* Body/L/SemiBold */
        font-family: Plus Jakarta Sans;
        font-size: 1rem;
        font-style: normal;
        font-weight: 600;
        line-height: 1.5rem; /* 150% */
        letter-spacing: 0.00938rem;
        /* text-wrap: nowrap; */
        white-space:nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
        }
        #userinfo{
          color: var(--brand--600, var(--heisenberg-blue-600));
          text-align: center;
          /* Body/S/Medium */
          font-family: Plus Jakarta Sans;
          font-size: 0.75rem;
          font-style: normal;
          font-weight: 500;
          line-height: 1.125rem; /* 150% */
          letter-spacing: 0.00938rem;
        }

      #home-btn{
        display: flex;
        background: url(images/home_icon.svg) no-repeat center center;
        width: 2.5rem;
        height: 2.5rem;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
      }

    .sidebar-projects{
      display: flex;
      flex-direction: column;
      padding-top: 3rem;
      max-height: 40vh;
    }
      .empty-project-list{
        color: var(--noble-black-300);
        padding: 0.5rem 0 0.5rem 0.5rem;
        font-feature-settings: 'liga' off;
        /* Paragraph M/Bold */
        font-family: MyriadPro;
        font-size: 1rem;
        font-style: normal;
        font-weight: 500;
        line-height: 1.5rem; /* 150% */
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .project-label-wrapper{
        display: flex;
        justify-content: flex-start;
        gap: 1rem;
        padding-bottom: 0.5rem;
      }
      .projects-label{
        color: var(--heisenberg-blue-600);
        font-feature-settings: 'liga' off;
        /* Paragraph S/Bold */
        font-family: MyriadPro;
        font-size: 0.875rem;
        font-style: normal;
        font-weight: bold;
        line-height: 1.25rem; /* 142.857% */
      }
      
      #project-list-container{
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        overflow-y: auto;

      }
      
      #project-list-container::-webkit-scrollbar {
          display: block;
      }
      .project-list-item{
        display: flex;
        border-radius: 0.625rem;
        padding: 0.5rem 0 0.5rem 0.5rem;
      }
      .active-project{
        background: var(--brand--25, #F9FDFE);
      }
      .file-folder-icon{
        display: flex;
        background:  center / contain no-repeat url(images/folder_outlined.svg);
        width: 1rem;
        height: 1rem;
        flex-shrink: 0;
      }
      .project-name{
        display: inline-block;
        color: var(--noble-black-400);
        font-feature-settings: 'liga' off;
        /* Paragraph M/Bold */
        font-family: MyriadPro;
        font-size: 1rem;
        font-style: normal;
        font-weight: 700;
        line-height: 1.5rem; /* 150% */
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .active-project-name{
        color: var(--brand--900, var(--heisenberg-blue-900, #193037));
      }
    
    #arrow-inward{
        display: flex;
        align-self: flex-end;
        width: 1.5rem;
        height: 1.5rem;
        background: url(images/toggle_sidebar.svg) no-repeat center center;
        border: none;
        outline: none;
        cursor: pointer;
        margin-top: auto;
        transition: all 1s ease;
    }   
    #sidebar-foot{
      display: flex;
      flex-direction: column;
      padding: 0.625rem 0 0.625rem;
      border-top: 1px solid var(--neutral--500);
      margin-top: 1.5rem;    
    }
      .footer-btn{
        display: flex;
        padding: 0.2rem 0;
        flex-direction: row;
        justify-content: flex-start;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
      }
        .settings-icon{
          display: flex;
          background: center / contain no-repeat url(images/settings.svg);
          width: 1rem;
          height: 1rem;
        }
        .update-btn{
          display: flex;
          outline: none;
          border: none;
          align-self: center;
          background: center / contain no-repeat url(images/pencil_icon.svg);
          width: 1rem;
          height: 1rem;
          cursor: pointer;
        }
        .create-btn{
          display: flex;
          outline: none;
          border: none;
          align-self: center;
          background: center / contain no-repeat url(images/plus-bold.svg);
          width: 1rem;
          height: 1rem;
          cursor: pointer;
        }
        .info-icon{
          display: flex;
          background: center / contain no-repeat url(images/info.svg);
          width: 1rem;
          height: 1rem;
        }
        .briefcase-icon{
          display: flex;
          background: center / contain no-repeat url(images/briefcase.svg);
          width: 1rem;
          height: 1rem;
        }
        .logout-icon{
          display: flex;
          background: center / contain no-repeat url(images/logout.svg);
          width: 1rem;
          height: 1rem;
        }
        .footer-btn-label{
          color: var(--noble-black-400);
          font-feature-settings: 'liga' off;
          /* Paragraph M/Bold */
          font-family: MyriadPro;
          font-size: 1rem;
          font-style: normal;
          font-weight: bold;
          line-height: 1.5rem; /* 150% */
        }
      #logo-container{
        display: flex;
        /* padding: 0.2rem 0; */
        padding: 0.5rem 0rem;
        justify-content: center;
        align-items: center;
        gap: 0.9375rem;
        /* align-self: stretch; */
      }
</style>
