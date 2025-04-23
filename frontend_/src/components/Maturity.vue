<template>
    <div id="maturity-container">
        <div id="chart-wrapper">
            <div class="header-wrapper">
                <select id="matruity-dropdown" v-model="selectedChart" @change="updateChart" placeholder="Choose a chart...">
                    <optgroup label="Diagrams">
                        <option v-for="chart in charts.slice(0, 4)" :key="chart" :value="chart">{{ chart }}</option>
                    </optgroup>
                    <optgroup label="Tables">
                        <option :value="charts[4]">{{ charts[4] }}</option>
                    </optgroup>
                </select>
                <button class="refresh-icon" title="Regenerate maturity assessment" @click="regenerateAsessment"></button>
            </div>

            <div id="maturity-content" class="maturity-content">
                <div id="radar-chart-area" ref="chartContainer"></div>
                <MaturityTable id="chart-table" :mat_data="table_data[this.selectedChart]"/>
            </div>
        </div>
        <div id="loading-wrapper">
            <div id="loading-spinner" class="maturity-load-btn"></div>
            <div id="loading-text"></div>
        </div>
    </div>

    <!-- Questionnaire -->
    <QuestionaireModal v-if="showQuestionnaireModal" @questionnaire-submitted="triggerAssesment" @close="closeQuestionnaire"/>
</template>
  
<script>
import * as echarts from 'echarts';
import { inject } from 'vue';
import QuestionaireModal from './QuestionaireModal.vue';
import MaturityTable from './MaturityTable.vue';
import chek_benchmarks from '../composables/chek_kma_benchmarks';
import { findBestMatchIndex } from '../composables/utils';
import axios from 'axios';


export default {
    components: {
        QuestionaireModal,
        MaturityTable
    },
    data() {
        const base_api = inject('base_api');

        const projects_api = base_api + "/projects/";

        const textify_model_api = base_api + "/intellichek/extraction";

        const evaluate_technology_api = base_api + "/intellichek/evaluate_technology"; 
        const get_technology_api = base_api + "/get_maturity_entries_technology";

        const evaluate_orga_api = base_api + "/intellichek/evaluate_organisation";
        const get_orga_api = base_api + "/get_maturity_entries_organisation";

        const evaluate_info_api = base_api + "/intellichek/evaluate_information";
        const get_info_api = base_api + "/get_maturity_entries_information";

        const evaluate_process_api = base_api + "/intellichek/evaluate_process";
        const get_process_api = base_api + "/get_maturity_entries_process";

        const charts = ['Technology', 'Organisation', 'Information', 'Process', 'Summary'];
        const api_label_map =   {Technology: {evaluate: evaluate_technology_api, get_from_db: get_technology_api},
                                Organisation: {evaluate: evaluate_orga_api, get_from_db: get_orga_api},
                                Information: {evaluate: evaluate_info_api, get_from_db: get_info_api},
                                Process: {evaluate: evaluate_process_api, get_from_db: get_process_api}
                                }


        return {
            project_id: null,
            current_project: null,
            projects_api: projects_api,
            textify_model_api: textify_model_api,
            api_label_map: api_label_map,
            selectedChart: '',
            charts: charts,
            chart_data: {},
            chartInstance: null,
            app: null,
            overlay: null,
            project_container: null,
            project_content_window: null,
            showQuestionnaireModal: false,
            chart_container: null,
            loading_container: null,
            table_data: {}
        };
    },

    async mounted() {
        window.addEventListener("resize", this.updateChart);
        this.project_id = this.$route.params.id;
        this.chartInstance = echarts.init(this.$refs.chartContainer);

        this.app = document.getElementById("app");
        this.overlay = document.getElementById("overlay-block");
        this.project_container = document.getElementById(`${this.project_id}`);
        this.project_content_window = document.getElementById("project-content");

        this.chart_container = document.getElementById("chart-wrapper");
        this.loading_container = document.getElementById("loading-wrapper");

        const questionnaire_submitted = this.checkQuestionnaire();
        if(!questionnaire_submitted){
            this.showQuestionnaireModal = true;
            return;
        }
        const maturity_assessed = this.checkMaturityStatus();



        if(maturity_assessed){
            // get data from database
            const loaded = await this.getMaturityData();
            if (!loaded){
                this.loading_container.style.display = "flex";
                this.showError();
                return;
            }else{
                this.chart_container.style.display = "flex";
                this.updateChart();
            }
        }else{
            this.triggerAssesment();
        }
    
    },
    beforeUnmount(){
        window.removeEventListener("resize", this.updateChart);
    },

    methods: {
        closeQuestionnaire(){
            this.showQuestionnaireModal = false;
        },
        updateChart() {
            // const chart_area = document.getElementById("radar-chart-area");
            // const chart_table = document.getElementById("chart-table");
            const chart_area = document.getElementById("maturity-content");
            const table_wrapper = document.getElementById("table-wrapper");
            let option;
            switch (this.selectedChart) {
            case this.charts[0]:
                option = this.chart_data[this.charts[0]];
                chart_area.style.display = 'flex';
                table_wrapper.style.display = 'none';
                break;
            case this.charts[1]:
                option = this.chart_data[this.charts[1]];
                chart_area.style.display = 'flex';
                table_wrapper.style.display = 'none';
                break;
            case this.charts[2]:
                option = this.chart_data[this.charts[2]];
                chart_area.style.display = 'flex';
                table_wrapper.style.display = 'none';
                break;
            case this.charts[3]:
                option = this.chart_data[this.charts[3]];
                chart_area.style.display = 'flex';
                table_wrapper.style.display = 'none';
                break;
            case this.charts[4]:
                chart_area.style.display = 'none';
                table_wrapper.style.display = 'flex';
                return;
            default:
                option = this.chart_data[this.charts[0]];
                chart_area.style.display = 'flex';
                    table_wrapper.style.display = 'none';
                this.selectedChart = this.charts[0];
            }
            this.chartInstance.setOption(option);
            this.chartInstance.resize();
        },

        checkMaturityStatus(){
            const user_projects = this.$store.state.projects;
            this.current_project = user_projects.find(project => project.id == this.project_id);
            return this.current_project.maturity_assessment;
        },
        checkQuestionnaire(){
            const user_projects = this.$store.state.projects;
            this.current_project = user_projects.find(project => project.id == this.project_id);
            return this.current_project.questionnair_submitted;
        },

        async triggerAssesment(){
            // show loading spinner and text
            this.loading_container.style.display = "flex";
            this.chart_container.style.display = "none";

            // trigger maturity assesment
            const success = await this.executeMaturityAssessment();
            console.log(`Success: ${success}`);

            if (success){
                // get data from database
                const loaded = await this.getMaturityData();
                if (!loaded){
                    this.showError();
                    return;
                }else{
                    this.loading_container.style.display = "none";
                    this.chart_container.style.display = "flex";
                    this.updateChart();
                }
            }else{
                // show error
                this.showError();
                return;
            }
        },

        async executeMaturityAssessment(){
            this.blockApp();
            let completed = true;
            const loading_text = document.getElementById("loading-text");
            loading_text.textContent = "The following process can take a couple of minutes. Please be patient.\r\nExtract data from process-map... (1/5)";

            const dummy_body = {chat_message: {
                                        human_message: "string"
                                    },
                                    chat_settings: {
                                        language: "English",
                                        diagram_id: "string"
                                    }
                                }
            // 1st Phase: textify BPMN Model
            await fetch(`${this.textify_model_api}?project_id=${this.project_id}` , {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {'Content-Type': 'application/json',
                            'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`},
                    body: JSON.stringify(dummy_body),
            })
            .then(response => {
                if(response.ok){
                    console.log("Successfully textified BPMN-Model");
                    console.log(response);
                }else{
                    console.log(`status: ${response.status} - ${response.statusText}`);
                    completed = false;
                }
            })
            .catch(error =>{
                console.log(error);
                completed = false;
            })

            if(!completed){
                return false;
            }

            // 2nd Phase: evaluate on different Key-Maturity areas
            let count = 2;
            for (const key_area in this.api_label_map) {
                loading_text.textContent = `The following process can take a couple of minutes. Please be patient.\r\nAssess maturity regarding ${key_area}... (${count}/5)`;
                count++;
                console.log(`${key_area}: ${this.api_label_map[key_area]}`);
                const api = this.api_label_map[key_area].evaluate;

                await fetch(`${api}?project_id=${this.project_id}`, {
                        method: 'POST',
                        credentials: 'same-origin',
                        headers: {'Content-Type': 'application/json',
                                'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`},
                        body: JSON.stringify(dummy_body),
                })
                .then(response => {
                    if(response.ok){
                        console.log("Successfully evaluated BPMN-Model");
                        console.log(response);
                    }else{
                        console.log(`status: ${response.status} - ${response.statusText}`);
                        completed = false;
                    }
                })
                .catch(error =>{
                    console.log(error);
                    completed = false;
                })

                if(!completed){
                    return false;
                }
            }
            console.log("Maturity Assessment complete!");

            const updated_project_data = { maturity_assessment: true}
            await this.updateProjectData(updated_project_data)
            this.blockApp(false);
            // When everything completed sucessfully
            return completed;
        },

        async regenerateAsessment(){
            const answer = window.confirm('Be aware, that this also effects the roadmap and the report. They will be regenerated as well. Would you like to continue?')
            if(!answer) return;
            const data_reset = {questionnair_submitted: false, maturity_assessment: false, roadmap_created:false, report_created: false}
            const success = await this.updateProjectData(data_reset);
            if(!success){
                window.alert("There has been a problem, we could not reset your data. Try again later.");
                return
            }
            const table_wrapper = document.getElementById("table-wrapper");
            if (table_wrapper) {
                table_wrapper.remove();
            }
            this.showQuestionnaireModal = true;
        },

        async updateProjectData(updated_project_data){
            const completed = await axios.put(
                `${this.projects_api}${this.project_id}`,
                updated_project_data,
                {
                    headers: {'Content-Type': 'application/json',
                            'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`}
                },
            )
            .then((response)=>{
                this.$store.commit('loadProjects');
                console.log("Successfully updated maturity status of project...");
                console.log(response);
                return true;
            })
            .catch((error)=>{
                console.log(error);
                return false;
            })
            return completed;
        },

        async getMaturityData(){
            let completed = true;
            let stored_data = [];
            for (const key_area in this.api_label_map) {
                const api = this.api_label_map[key_area].get_from_db;
                try {
                    const response = await fetch(`${api}?project_id=${this.project_id}` , {
                        method: 'GET',
                        credentials: 'same-origin',
                        headers: {'Content-Type': 'application/json',
                                'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`},
                    });
                    if(response.ok){
                        console.log(`Successfully loaded data for ${key_area} Maturity...`);
                        const data = await response.json();
                        this.writeChartData(key_area, data);
                        console.log(data);
                        const add_benchmark = data.map((item, index) => {
                            let benchmark;
                            const found_index = findBestMatchIndex(chek_benchmarks[key_area], item.label);
                            if(found_index != -1){
                                benchmark = chek_benchmarks[key_area][found_index].level;
                            }else{
                                benchmark = null;
                            }
                            return {
                                ...item,
                                benchmark:   benchmark
                            };
                        });
                        this.table_data[key_area] = add_benchmark;
                        stored_data.push({label: key_area, data: add_benchmark});
                    } else {
                        console.log(`status: ${response.status} - ${response.statusText}`);
                        completed = false;
                    }
                } catch(error) {
                    console.log(error);
                    completed = false;
                }

                if(!completed){
                    return completed
                }
            }
            this.$store.commit('setMaturityData', {id: this.project_id, data: this.table_data})
            this.createDataTable(stored_data);
            return completed;
        },

        writeChartData(chart_label, api_data){
            // Prepare data for ECharts
            const benchmark_data = [];
            const indicatorData = api_data.map((item, index) => {
                let showAxisLabel = index == 0;
                let label = item.label.length > 20 ? breakLines(item.label, 20) : item.label;
                const found_index = findBestMatchIndex(chek_benchmarks[chart_label], item.label);
                if(found_index != -1){
                    benchmark_data.push(chek_benchmarks[chart_label][found_index].level);
                }
                else{
                    benchmark_data.push(null)
                }
                return { name: label, max: 5, axisLabel: { show: showAxisLabel } };
            });
            const seriesData = api_data.map((item) => {
                return item.level;
            });
            // const benchmark_data = chek_benchmarks[chart_label].map((item) => item.level);

            // console.log("Assessed Level", api_data);
            // console.log("Benchmark Level", chek_benchmarks[chart_label]);

            this.chart_data[chart_label] = {
                                                tooltip: {
                                                    trigger: 'item',
                                                    formatter: function (params) {
                                                        return `${params.name}`;
                                      
                                                    }
                                                },
                                                legend: {
                                                    data: [ 'CHEK Benchmark', 'Your Maturity Level'],
                                                    selectedMode: false // Disable toggling of series
                                                },
                                                radar: {
                                                    indicator: indicatorData,
                                                    // Set the center and radius of the radar chart
                                                    center: ['50%', '50%'],
                                                    radius: '60%', // Adjust the radius to leave enough space for labels
                                                },
                                                series: [{
                                                            type: 'radar',
                                                            name: chart_label,
                                                            data: [
                                                                {
                                                                    value: benchmark_data,
                                                                    name: 'CHEK Benchmark',
                                                                    itemStyle: {
                                                                        color: '#686b6e'
                                                                    }
                                                                },
                                                                {
                                                                    value: seriesData,
                                                                    name: 'Your Maturity Level',
                                                                    itemStyle: {
                                                                        color: '#65beda'
                                                                    }
                                                                }
                                                            ],
                                                        }]
                                            }
        function breakLines(text, linelength) {
            var linebreak = '\n';
            var counter = 0;
            var line = '';
            var returntext = '';
            var bMatchFound = false;
            var linelen = 20; // 20 characters per line is default

            if (linelength) {
                linelen = linelength;
            }

            if (!text) { return ''; }
            if (text.length < linelen+1) { return text.trim(); }

            while (counter < text.length) {
                line = text.slice(counter, counter + linelen);
                bMatchFound = false;

                if (line.length == linelen) {
                    for (var i=line.length; i > -1; i--) {
                        if (line.slice(i, i + 1) == ' ') {
                            counter += line.slice(0, i).length;
                            line = line.slice(0, i).trim() + linebreak;
                            returntext += line;
                            bMatchFound = true;
                            break;
                        }
                    }

                    if (!bMatchFound) {
                        counter += line.length;
                        line = line.trim() + linebreak;
                        returntext += line;
                    }
                } else {
                    returntext += line.trim();
                    break;
                }
            }

            return returntext;
        };
        
        },
        createDataTable(stored_maturity_data){
            console.log(stored_maturity_data);

            // Create table wrapper
            const table_wrapper = document.createElement('div');
            table_wrapper.id = "table-wrapper";

            for (const item of stored_maturity_data) {
                // const data = item.data.map((value, index) => {
                //             return {
                //                 ...value,
                //                 benchmark: index < chek_benchmarks[item.label].length ? chek_benchmarks[item.label][index].level : null
                //             };
                //         });
                const data = item.data;
                // Create button
                const button = document.createElement('button');
                button.textContent = item.label;
                button.className = 'collapsible';

                // Create content div
                const contentDiv = document.createElement('div');
                contentDiv.className = 'table-content';

                // Create table
                const table = document.createElement('table');

                // Create table header
                const thead = document.createElement('thead');
                let headerRow = document.createElement('tr');
                ['Key Maturity Area', 'Assessed Level', 'CHEK Benchmark','IntelliCHEK Justification'].forEach(function(text) {
                let th = document.createElement('th');
                th.textContent = text;
                headerRow.appendChild(th);
                });
                thead.appendChild(headerRow);
                table.appendChild(thead);

                // Create table body
                const tbody = document.createElement('tbody');
                data.forEach(function(object) {
                    let row = document.createElement('tr');
                    ['label', 'level', 'benchmark', 'justification'].forEach(function(key) {
                        let td = document.createElement('td');
                        td.textContent = object[key];
                        row.appendChild(td);
                    });
                    tbody.appendChild(row);
                });
                table.appendChild(tbody);

                // Append table to content div
                contentDiv.appendChild(table);

                // Append button and content div to fragment
                table_wrapper.appendChild(button);
                table_wrapper.appendChild(contentDiv);

                // Add event listener to button
                button.addEventListener('click', function() {
                    this.classList.toggle('table-active');
                    let content = this.nextElementSibling;
                    if (content.style.display === 'block') {
                        content.style.display = 'none';
                    } else {
                        content.style.display = 'block';
                    }
                });                
            }

            // Append fragment to body (or wherever you want the table)
            const radar_chart_area = document.getElementById("chart-wrapper");
            radar_chart_area.appendChild(table_wrapper);

        },
        showError(spinner=true){
            if (spinner){
                const loading_spinner = document.getElementById("loading-spinner");
                loading_spinner.style.display = "none";
            }
            const loading_text = document.getElementById("loading-text");
            loading_text.textContent = "There has been an error :/";
            this.blockApp(false);
        },
        blockApp(block=true){
            this.app.classList.toggle("app-blocked");
            this.project_container.classList.toggle("project-container-active");
            this.project_content_window.classList.toggle("project-content-loading");
            if(block){
                this.overlay.style.display = "block";
            }
            else{
                this.overlay.style.display = "none";
            }
        },
        // Function to download the chart as an image
        downloadChart() {
            // Get the base64 URL of the chart image
            const imgURL = this.chartInstance.getDataURL({
                type: 'png',
                pixelRatio: 2,
                backgroundColor: '#fff'
            });

            // Create a temporary link element
            const link = document.createElement('a');
            link.href = imgURL;
            link.download = 'chart.png';

            // Append the link to the body
            document.body.appendChild(link);

            // Trigger the download
            link.click();

            // Remove the link from the document
            document.body.removeChild(link);
        }
    },
};
</script>
  
<style>

    #maturity-container{
        display: flex;
        width: 100%;
        height: 100%;
        justify-content: center;
        overflow: hidden;
    }

    #chart-wrapper{
        display: none;
        flex-direction: column;
        justify-content: flex-start;
        width: 100%;
        height: 100%;
        padding: 1rem;
        gap: 2rem;
        overflow: hidden;
    }
    .maturity-content{
        display: flex;
        width: 100%;
        height: 80%;
        justify-content: space-around;
        align-items: flex-start;
        overflow: hidden;
    }
    #radar-chart-area{
        display: flex;
        width: max-content;
        min-width: 50%;
        height: 100%;
    }
    #chart-table{
        display: flex;
        width: max-content;
        height: max-content;
        max-width: 40%;
        border-radius: 0.5rem;
        margin-top: 0;
        max-height: 100%;
        overflow: auto;
    }
    #chart-table::-webkit-scrollbar {
        display: block; /* Override to display scrollbar */
    }
    #matruity-dropdown{
        width: max-content;
        max-width: 25%;
        height: max-content;
        border-radius: 1rem;
        background: var(--noble-black-50);
        outline: none;
        border: none;
        font-family: MyriadPro;
        font-size: 1rem;
        font-style: normal;
        font-weight: 700;
        color: var(--noble-black-400);
        padding: 0.5rem;
        cursor: pointer;
    }

    #loading-wrapper{
        display: none;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 1rem;
    }

    .maturity-load-btn {
        display: flex;
        border: 0.5rem solid #f3f3f3; /* Light grey */
        border-top: 0.5rem solid grey; /* Blue */
        border-radius: 50%;
        width: 10rem;
        height: 10rem;
        animation: spin 3s linear infinite;
    }
    #loading-text{
        font-family: MyriadPro;
        font-size: 1.1rem;
        font-style: normal;
        font-weight: 700;
        color: var(--noble-black-400); 
        white-space: pre;
        text-align: center;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    #table-wrapper{
        display: none;
        flex-direction: column;
        gap: 0.5rem;
        background-color: var(--noble-black-50);
        border-radius: 0.5rem 0.5rem 0 0;
        overflow: auto;
    }
    .collapsible{
        font-family: MyriadPro;
        font-size: 1.2rem;
        font-weight: 500;
        color: var(--noble-black-500);
        background-color: var(--neutral--100);
        outline: none;
        border-style: none none solid;
        border-color:  var(--heisenberg-blue-900);
        border-radius: 0.5rem 0.5rem 0 0;
        text-align: left;
    }

    .table-active, .collapsible:hover {
    background-color: var(--heisenberg-blue-600);
    }
    .table-content {
    padding: 0 18px;
    display: none;
    overflow: auto;
    background-color: #f1f1f1;
    margin-top: -0.5rem;
    }

    table {
    width: 100%;
    border-collapse: collapse;
    font-family: MyriadPro;
    }

    th, td {
    vertical-align: top;
    padding-bottom: 0.5rem;
    color: var(--noble-black-500);
    }

    th{
        text-align: left;
        border-bottom: 1px solid var(--heisenberg-blue-900);
        font-size: 1rem;
        font-weight: 700;
    }
</style>
  