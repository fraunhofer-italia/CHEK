<template>
    <div class="modal-overlay" v-show="showModal">
        <div class="modal">
            <div class="modal-header">
                <span class="modal-title">{{ title }}</span>
            </div>
            <div class="modal-body">
                <div class="project-form">
                    <input class="project-input" type="text" v-model="projectName" placeholder="Project Name">
                    <textarea class="project-input project-textarea" v-model="projectDescription" placeholder="Please describe your current building permit process as accurately as possible here..."></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="submit-btn" @click="submitForm"> 
                    <div v-if="loading" class="load-btn"></div>
                    <span>Create</span> 
                </button>
                <button class="close-btn" @click="closeModal"> Close </button>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, inject } from 'vue';
    import { useStore } from 'vuex';
    import { useRouter } from 'vue-router';

    const props = defineProps({
    showModal: {
        type: Boolean,
        required: true,
    },
    title: {
        type: String,
        default: "Modal Title",
    },
    });

    const emit = defineEmits(['close']);

    const base_api = inject('base_api');
    const projects_api = base_api + "/projects/";
    const project_description_api = (project_id) => `${projects_api}${project_id}/upload_text`;
    const transform_intial_description =  (project_id) => `${base_api}/intellichek/${project_id}/transform-initial-description`
    const store = useStore();
    const router = useRouter();

    const projectName = ref('');
    const projectDescription = ref('');
    const loading = ref(false);

    const closeModal = () => {
        loading.value = false;
        emit('close');
    };

    const alertInput = (inputClass) => {
        const inputElement = document.querySelector(`.${inputClass}`);
        inputElement.classList.toggle('alert-input');
        setTimeout(() => {
            inputElement.classList.toggle('alert-input');
        }, 2500);
    };

    const createTextFile = (text) => {
        const blob = new Blob([text], { type: 'text/plain' });
        return new File([blob], 'project_description.txt', { type: 'text/plain' });
    };

    const sendTextFile = async (file, id) => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(project_description_api(id), {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`
            },
            body: formData,
            });

            if (!response.ok) {
                return false
            }

            console.log('File uploaded successfully');
            return true
        } catch (error) {
            console.log(error);
            return false;
        }
    };

    const submitForm = async () => {
        if (projectName.value.trim() === ""){
            alertInput('project-input');
            return;
        }
        if (projectDescription.value.trim() === "") {
            alertInput('project-textarea');
            return;
        }

        const project_data = {
            name: projectName.value
        };


        loading.value = true;
        try {
            const response = await fetch(projects_api, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`
                },
                body: JSON.stringify(project_data),
            });

            if (response.ok) {
                const resData = await response.json();
                const file = createTextFile(projectDescription.value);
                console.log(resData);
                const file_send = await sendTextFile(file, resData.id);

                if(!file_send) throw new Error("file was not sent");

                fetch(transform_intial_description(resData.id), {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`
                    },
                    body: JSON.stringify({}),
                })
                .then((response)=>{
                    if(response.ok){
                        closeModal();
                        store.commit('loadProjects');
                        router.push(`/projects/${resData.id}`);
                    }
                })
                .catch((error) => {
                    loading.value = false;
                    console.log(error);
                });

                
            } else {
                loading.value = false;
                console.log(`status: ${response.status} - ${response.statusText}`);
                window.alert("Oops! It seems that we could not create the project. There seem to be a connection problem.");
            }
        } catch (error) {
            loading.value = false;
            console.log(error);
            window.alert("Oops! It seems that we could not create the project. There seem to be a connection problem.");
        }
    };
</script>

<!-- <script>
import {inject} from 'vue';
import { useStore } from 'vuex';



export default {
  props: {
    showModal: {
      type: Boolean,
      required: true,
    },
    title: {
      type: String,
      default: "Modal Title",
    },
  },
  setup() {
        const base_api = inject('base_api');
        const projects_api = base_api +"/projects/";
        const store = useStore();

        return {projects_api, store};
  },
  methods: {
    closeModal() {
      this.$emit("close");
    },

    async submitForm(){
        const inp = document.getElementById('pname');

        const project_data = {};
        
        let check_complete = true;

        const projects_error_msg = "Oops! It seems that we could not create the project. There seem to be a connection problem.";

        if(inp.value.trim() == ""){
            check_complete = false;
            inp.classList.toggle('alert-input');
            inp.value = "";
            setTimeout(() => {
                inp.classList.toggle('alert-input');
                }, 2500);
        }else{
            project_data["name"] = inp.value;
        }

        if (!check_complete){
            return;
        }else{
            fetch(this.projects_api, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {'Content-Type': 'application/json',
                                            'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`},
                body: JSON.stringify(project_data),
            })
            .then(response => {
                if(response.ok){
                    response.json()
                    .then(resData =>{
                        this.store.commit('loadProjects');
                        this.closeModal();
                        this.$router.push(`/projects/${resData.id}`);
                        console.log(resData);
                    })
                    .catch(error =>{
                        console.log(error);
                        window.alert("Oops! Something went wrong :/");
                    });

                }else{
                    console.log(`status: ${response.status} - ${response.statusText}`)
                    window.alert(projects_error_msg);
                }
            })
            .catch(error =>{
                console.log(error);
                window.alert(projects_error_msg);
            });   
            
        }


    },
  },
};
</script> -->

<style scoped>
/* Add your modal styles here */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal {
    display: flex;
    flex-direction: column;
    background: #fff;
    border-radius: 1rem;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.5);
    min-width: 50vw;
    /* width: 400px; */
}

.modal-header {
    background: var(--noble-black-50);
    padding: 2rem;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    border-radius: 1rem 1rem 0 0;
}

.modal-title {
    color: var(--noble-black-400);
    font-feature-settings: 'liga' off;
    /* Paragraph M/Bold */
    font-family:  Plus Jakarta Sans;
    font-size: 1.5rem;
    font-style: normal;
    font-weight: 700;
    line-height: 1.5rem; /* 150% */
}

.modal-body {
    display: flex;
    flex-direction: column;
    padding: 2rem;
}

.project-form{
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.project-input{
    display: flex;
    height: 100%;
    color: var(--noble-black-700, #9B9C9E);
    background: var(--noble-black-100);
    border: var(--noble-black-700);
    border-radius: 0.3rem;
    outline: none;
    padding: 0.5rem;
    /* Body/L/Medium */
    font-family: Plus Jakarta Sans;
    font-size: 1rem;
    font-style: normal;
    font-weight: 500;
    line-height: 1.5rem; /* 150% */
    letter-spacing: 0.00938rem;
    flex-grow: 1;
}
.project-textarea{
    min-height: 200px;
    font-family: Plus Jakarta Sans;
    font-size: 0.8rem;
    font-style: normal;
    font-weight: 500;
    line-height: 1rem; /* 150% */
    letter-spacing: 0.00938rem;
}

.alert-input{
    border: 2px solid var(--error--700);
}


.modal-footer{
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    padding: 0 2rem 2rem;
}
.close-btn{
    /* Style */ 
    border-radius: 0.75rem;
    height: 2rem;
    padding: 0 1rem;
    background: var(--neutral--500, #6F7786);
    /* Typography */
    border: none;
    color: var(--neutral-0, var(--noble-black-0, #FFF));
    font-feature-settings: 'liga' off;
    /* Button/L */
    font-family: Roboto;
    font-size: 1rem;
    font-style: normal;
    font-weight: 500;
    line-height: normal;
    cursor: pointer;
}
.submit-btn{
    display: flex;
    gap: 1rem;
    align-items: center;
    justify-content: center;
    /* Style */ 
    border-radius: 0.75rem;
    height: 2rem;
    width:50%;
    background: var(--heisenberg-blue-700, #4c8fa4);
    /* Typography */
    border: none;
    color: #FFF; 
    /* var(--neutral--700, var(--noble-black-100, #FFF)); */
    font-feature-settings: 'liga' off;
    /* Button/L */
    font-family: Roboto;
    font-size: 1rem;
    font-style: normal;
    font-weight: 500;
    line-height: normal;
    cursor: pointer;
}

</style>