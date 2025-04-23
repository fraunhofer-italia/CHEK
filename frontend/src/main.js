import './assets/main.css';

import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

import { createStore } from 'vuex';
import VueGtag from "vue-gtag";

import axios from 'axios';

import { findBestMatchIndex } from './composables/utils';
import chek_benchmarks from './composables/chek_kma_benchmarks';

// const base_api = "http://10.30.104.70:9980/api/v1";
const base_api = "https://chek1.fraunhofer.app/api/v1";
const google_analytics_measurement_id = "G-E7X6G2PXHK";



// Create a new store instance.
const store = createStore({
    state () {
      return {
        projects: null,
        maturity_data: {},
      }
    },
    mutations: {
        loadProjects(state){
            const projects_error_msg = "Oops! It seems that we could not load your projects. There seem to be a connection problem.";

            fetch( base_api +"/projects/", {
                method: 'GET',
                credentials: 'same-origin',
                headers: {'Content-Type': 'application/json',
                            'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`}
            })
            .then(response => {
                if(response.ok){
                    response.json()
                    .then((response) => {
                        console.log("Projects: ", response);
                        state.projects = response
                    })
                    .catch(error =>{
                        console.log(error);
                        state.projects = null;
                        window.alert(projects_error_msg);
                    }); 
                }else{
                    console.log(`status: ${response.status} - ${response.statusText}`)
                    state.projects = null;
                }
            })
            .catch(error =>{
                console.log(error);
                state.projects = null;
                window.alert(projects_error_msg);
            });   
        },
        unloadProjects(state){
            state.projects = null;
        },
        setMaturityData(state, data){
            state.maturity_data[data.id] = data.data;
            console.log(state.maturity_data);
        }
    },
    actions: {
        async loadMaturityData({commit}, id){
            const maturity_data = {};

            const get_technology_api = base_api + "/get_maturity_entries_technology";
            const get_orga_api = base_api + "/get_maturity_entries_organisation";
            const get_info_api = base_api + "/get_maturity_entries_information";
            const get_process_api = base_api + "/get_maturity_entries_process";
            const api_label_map =   {Technology: get_technology_api,
                                    Organisation: get_orga_api,
                                    Information:  get_info_api,
                                    Process: get_process_api
            }
            for (const category in api_label_map) {
                const api = api_label_map[category];
                await axios.get(api,
                    {            
                        headers: {
                            'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`
                        },
                        params: {project_id: id}
                    }
                )
                .then((response)=>{
                    const add_benchmark = response.data.map((item, index) => {
                        let benchmark;
                        const found_index = findBestMatchIndex(chek_benchmarks[category], item.label);
                        if (found_index != -1){
                            benchmark = chek_benchmarks[category][found_index].level;
                        }
                        else{
                            benchmark = null;
                        }  
                        return {
                            ...item,
                            benchmark:   benchmark
                        };
                    });
                    maturity_data[category] = add_benchmark
                })
                .catch((error)=>{
                    console.log(error);
                    maturity_data[category] = [];
                })
            }
            commit('setMaturityData', {id: id, data: maturity_data});    
        },
    }
  });

const app = createApp(App);

app.use(VueGtag, {
    config: { id:  google_analytics_measurement_id}
});

app.provide('base_api', base_api);

app.use(router);

// Install the store instance as a plugin
app.use(store);

app.mount('#app');




