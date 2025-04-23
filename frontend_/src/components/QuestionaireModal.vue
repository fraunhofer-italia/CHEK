<template>
    <div class="modal-overlay">
      <form @submit.prevent="submitForm" class="modal">
        <div class="modal-header">
          <span class="modal-title"> Questionnaire </span>
        </div>
        <div class="modal-body">
            <span class="modal-text">Please, indicate the most suitable answer for each of the following questions.</span>
            <br/>
          <div class="question-form">
            <div v-for="(question, qindex) in questions" :key="qindex" class="question-item">
              <label class="question-label">{{ question.label }}</label>
              <select v-model="answers[qindex]" class="question-select" required>
                <option v-for="(option, oindex) in question.options" :key="oindex" :value="oindex">{{ option }}</option>
              </select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="submit" class="submit-btn">
            <div v-if="loading" class="load-btn"></div>
            <span>Submit</span>
          </button>
          <button class="close-btn" @click="closeModal">Close</button>
        </div>
      </form>
    </div>
  </template>
  
<script setup>
  import { ref , onMounted, inject} from 'vue';
  import {questions} from "../composables/questionnaire";
  import {useRoute} from 'vue-router';
  import { useStore } from 'vuex';
  import axios from "axios";

  const route = useRoute();
  const store = useStore();
  const loading = ref(false);
  const answers = ref([]);
  const base_api = inject('base_api');
  const questionnaire_api = (project_id) => `${base_api}/questionaire/projects/${project_id}/submit_questionnaire`
  const projects_api = (project_id) => `${base_api}/projects/${project_id}`

  const emit = defineEmits(['questionnaireSubmitted', 'close']);

  onMounted(()=>{

  })
   
  const submitForm = () => {
    loading.value = true;
    // Handle form submission
    console.log(answers.value);
    const questionnaire_data = questions.map((q, index) => ({
      category: q.category,
      maturity_category: q.maturity_category,
      question_number: q.count,
      answer_number: answers.value[index]
    }));
    axios.post(
      questionnaire_api(route.params.id),
      {entries: questionnaire_data},
      {
        headers: {
            'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`
        }
      }
    )
    .then(async (response) =>{
      console.log(response);
      await updateProjectData({questionnair_submitted: true})
      success();
    })
    .catch(error =>{
      console.log(error);
      window.alert("Oops, something went wrong :/");
    })

  };

  async function updateProjectData(updated_project_data){
      const completed = await axios.put(
          projects_api(route.params.id),
          updated_project_data,
          {
              headers: {'Content-Type': 'application/json',
                      'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`}
          },
      )
      .then((response)=>{
          store.commit('loadProjects');
          console.log("Successfully updated questionaire status of project...");
          console.log(response);
          return true;
      })
      .catch((error)=>{
          console.log(error);
          return false;
      })
      return completed;
  }
  
  const closeModal = () => {
    emit('close');
  };

  const success = () =>{
    loading.value = false;
    emit('questionnaireSubmitted');
    emit('close');
  }

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
  }
  
  .modal {
    display: flex;
    flex-direction: column;
    background: #fff;
    border-radius: 1rem;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.5);
    min-width: 50vw;
    max-height: 90vh;
    overflow: auto;
    margin: 1rem;
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
    overflow: auto;
  }
  
  .question-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    overflow: auto;
    padding: 0.1rem;
  }
  
  .question-item {
    display: flex;
    flex-direction: column;
  }
  
  .question-label {
    font-family: Plus Jakarta Sans;
    font-size: 1rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
  }
  
  .question-select {
    font-family: Plus Jakarta Sans;
    font-size: 1rem;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 0.3rem;
  }
  
  .modal-footer {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    padding: 0 2rem 2rem;
  }
  
  .close-btn, .submit-btn {
    border-radius: 0.75rem;
    height: 2rem;
    padding: 0 1rem;
    font-family: Roboto;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    gap: 0.5rem;
  }
  
  .close-btn {
    background: var(--neutral--500, #6F7786);
    color: #FFF;
    border: none;
  }
  
  .submit-btn {
    background: var(--heisenberg-blue-700, #4c8fa4);
    color: #FFF;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .modal-text{
    color: var(--neutral--500);
    text-align: center;
    font-feature-settings: 'liga' off;
    /* Heading XS/Regular */
    font-family: Plus Jakarta Sans;
    font-size: 1rem;
    font-style: normal;
    font-weight: 400;
    line-height: 2rem; /* 133.333% */
}
</style>
  