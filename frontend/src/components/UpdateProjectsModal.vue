<template>
    <div class="modal-overlay">
        <div class="modal">
            <div class="modal-header">
                <span class="modal-title">{{ title }}</span>
            </div>
            <div class="modal-body">
                <div class="project-form">
                    <label for="project-select" class="modal-label">Select Project:</label>
                    <select id="project-select" v-model="selectedProjectId" @change="onProjectChange" class="project-select">
                        <option v-for="project in projects" :key="project.id" :value="project.id">
                            {{ project.name }}
                        </option>
                    </select>
                </div>
                <form class="update-form" @submit.prevent="updateProject" v-if="selectedProject">
                    <div class="project-form">
                        <label for="project-name" class="modal-label">Update Project Name:</label>
                        <input id="project-name" class="project-input" type="text" v-model="projectName" required placeholder="Project Name">
                    </div>
                    <div class="modal-footer">
                        <button type="submit" class="update-btn">
                            <div v-if="loading" class="load-btn"></div>
                            <span>Change name</span>
                        </button>
                        <button type="button" class="delete-btn" @click="deleteProject">
                            <div v-if="loadingDelete" class="load-btn"></div>
                            <span>Delete project</span>
                        </button>
                    </div>
                </form>
                <div class="modal-footer">
                    <button type="button" class="closing-btn" @click="closeModal">Close</button>
                </div>
            </div>
        </div>
    </div>
</template>


<script setup>
import { ref, inject, computed } from 'vue';
import { useStore } from 'vuex';
import axios from 'axios';

const props = defineProps({
    title: {
        type: String,
        default: "Update Projects",
    }
});

const emit = defineEmits(['close']);

const base_api = inject('base_api');
const projects_api = `${base_api}/projects/`;
const store = useStore();

const selectedProjectId = ref(null);
const projectName = ref('');
const loading = ref(false);
const loadingDelete = ref(false);

const projects = computed(() => store.state.projects);

const selectedProject = computed(() => {
    return projects.value.find(project => project.id === selectedProjectId.value);
});

const onProjectChange = () => {
    if (selectedProject.value) {
        projectName.value = selectedProject.value.name;
    }
};

const closeModal = () => {
    loading.value = false;
    loadingDelete.value = false;
    emit('close');
};

const updateProject = async () => {

    const project_data = { name: projectName.value };
    loading.value = true;

    try {
        const response = await axios.put(`${projects_api}${selectedProjectId.value}`, project_data, {
            headers: { 'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}` }
        });

        if (response.status === 200) {
            store.commit('loadProjects');
            closeModal();
        } else {
            console.error(`Error: ${response.status} - ${response.statusText}`);
            alert("Failed to update the project. Please try again.");
        }
    } catch (error) {
        console.error(error);
        alert("Failed to update the project. Please try again.");
    } finally {
        loading.value = false;
    }
};

const deleteProject = async () => {
    const answer = window.confirm('Do you really want to delete this project? This action cannot be undone...');
    if (!answer) {
        return;
    }
    loadingDelete.value = true;

    try {
        const response = await axios.delete(`${projects_api}${selectedProjectId.value}`, {
            headers: { 'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}` }
        });

        if (response.status === 200) {
            store.commit('loadProjects');
            closeModal();
        } else {
            console.error(`Error: ${response.status} - ${response.statusText}`);
            alert("Failed to delete the project. Please try again.");
        }
    } catch (error) {
        console.error(error);
        alert("Failed to delete the project. Please try again.");
    } finally {
        loadingDelete.value = false;
    }
};
</script>


<style scoped>
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
    font-family: Plus Jakarta Sans;
    font-size: 1.5rem;
    font-weight: 700;
}

.modal-body {
    display: flex;
    flex-direction: column;
    padding: 2rem;
}

.project-list {

    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-self: flex-start;
    gap: 1rem;
    align-items: flex-end;
    margin-bottom: 1.5rem;
}

.project-select {
    width: 100%;
    /* height: max-content; */
    border-radius: 1rem;
    background: var(--noble-black-50);
    outline: none;
    border: none;
    font-family: MyriadPro;
    font-size: 1rem;
    font-weight: 700;
    color: var(--noble-black-400);
    padding: 0.5rem;
    cursor: pointer;
}

.project-form {
    display: flex;
    flex-direction: column;
    gap: .5rem;
    margin-bottom: 0.5rem;
}

.project-input {
    height: 100%;
    color: var(--noble-black-700, #9B9C9E);
    background: var(--noble-black-100);
    border: var(--noble-black-700);
    border-radius: 0.3rem;
    outline: none;
    padding: 0.5rem;
    font-family: Plus Jakarta Sans;
    font-size: 1rem;
    font-weight: 500;
    line-height: 1.5rem;
}

.alert-input {
    border: 2px solid var(--error--700);
}
.update-form{
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.modal-footer {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    padding: 0;
    margin-bottom: 1rem;
}

.closing-btn,
.update-btn,
.delete-btn {
    display: flex;
    width: 50%;
    border-radius: 0.75rem;
    height: 2rem;
    /* padding: 0 1rem; */
    border: none;
    color: var(--neutral-0, #FFF);
    font-family: Roboto;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    justify-content: center;
    align-items: center;
    gap: 0.5rem
}

.update-btn {
    background: var(--heisenberg-blue-700, #4c8fa4);
}

.delete-btn {
    background: var(--error--700, #d9534f);
}

.closing-btn {
    background: var(--neutral--500, #6F7786);
    width: 100%;
    margin-top: 2rem;
}

.modal-label {
    color: var(--noble-black-400);
    font-family: Plus Jakarta Sans;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}
</style>
