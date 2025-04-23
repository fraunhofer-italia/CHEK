<template>
    <div v-if="!loading && !error" id="roadmap-wrapper">
        <button class="refresh-icon" title="Regenerate roadmap" @click="regenerateRoadmap" style="align-self: flex-start;margin: 1rem;"></button>
        <div  id="roadmap-gantt"></div>
        <div id="custom-tooltip" class="tooltip" v-html="tooltipContent"></div>
    </div>
    <div v-else class="loading-wrapper-roadmap">
        <div v-if="!error" class="results-load-btn"></div>
        <div class="loading-text-results">{{ loading_text }}</div>
    </div>
</template>

<script setup>
    import { ref, onMounted, inject } from 'vue';
    import { useStore } from 'vuex';
    import {useRoute} from 'vue-router';
    import axios from 'axios';
    
    const store = useStore();
    const route = useRoute();

    const tooltipContent = ref('');
    const mouseX = ref(0);
    const mouseY = ref(0);
    const loading = ref(false);
    const chartData = ref([]);
    const loading_text = ref('')
    const error = ref(false);

    
    const base_api = inject('base_api');
    const projects_api = base_api + "/projects/";
    const create_roadmap_api_1 = `${base_api}/roadmap/evaluate_benchmark_chek`;
    const create_roadmap_api_2 = `${base_api}/roadmap/evaluate_benchmark_chek_roadmap`;
    const get_roadmap_api = (project_id) => `${base_api}/roadmap/${project_id}/get-roadmap`;

    let app;
    let overlay;
    let project_container;
    let project_content_window;

    onMounted(async () => {
        app = document.getElementById("app");
        overlay = document.getElementById("overlay-block");
        project_container = document.getElementById(`${route.params.id}`);
        project_content_window = document.getElementById("project-content");

        loading.value = true;
        blockApp();

        const user_projects = store.state.projects;
        const current_project = user_projects.find(project => project.id == route.params.id);

        await loadGoogleCharts();
        const roadmap_created = current_project.roadmap_created;
        if(!roadmap_created){
            loading_text.value = "We are creating the roadmap for you, this can take some time. Please, be patient :)";
            const success = await triggerRoadmapCreation();
            if(!success){
                showError();
                return;
            };
            const success_1 = await getRoadmap();
            if(!success_1){
                showError();
                return;
            };
            loading.value = false;
            blockApp(false);
        }else{
            loading_text.value =  "We are loading your roadmap :)";
            const success = await getRoadmap();
            if(!success){
                showError();
                return;
            };
            loading.value = false;
            blockApp(false);
        }
        setTimeout(() => {
            drawChart();
            document.getElementById('roadmap-wrapper').addEventListener('mousemove', handleMouseMove);
        }, 500);

    });

    const loadGoogleCharts = () => {
        return new Promise((resolve) => {
            google.charts.load('current', { packages: ['gantt'] });
            google.charts.setOnLoadCallback(resolve);
        });
    };

    const drawChart = () => {
        const data = new google.visualization.DataTable();
        data.addColumn('string', 'Task ID');
        data.addColumn('string', 'Task Name');
        data.addColumn('string', 'Resources');
        data.addColumn('date', 'Start Date');
        data.addColumn('date', 'End Date');
        data.addColumn('number', 'Duration');
        data.addColumn('number', 'Percent Complete');
        data.addColumn('string', 'Dependencies');
        data.addColumn({type: 'string', 'p': {'html': true}});

        data.addRows(chartData.value); 

        // Calculate the height based on the number of rows
        const rowHeight = 42; // Adjust this value as needed
        const rowWidth = 100; // Adjust this value as needed
        const numRows = chartData.value.length;
        const chartHeight = rowHeight * numRows + 3*rowHeight; // Add some padding
        const chartWidth = rowWidth * numRows + 1*rowWidth; // Add some padding

        const chartOptions = {
            height: chartHeight,
            width: chartWidth,
            gantt: {
            criticalPathEnabled: false,
            arrow: {
                color: '#363a3d',
                width: 2,
                // angle: 45,
                // radius: 0,
            },
            palette: [
                {
                color: '#4c8fa4', // Heisenberg Blue
                dark: '#4c8fa4',
                light: '#a1e4f9'
                }
            ]
            },
            backgroundColor: '#f1f8e9',
            colors: ['#4c8fa4'],
        };

        const chart = new google.visualization.Gantt(document.getElementById('roadmap-gantt'));
        chart.draw(data, chartOptions);

        google.visualization.events.addListener(chart, 'onmouseover', (e) => {
            const tooltip = document.getElementById('custom-tooltip');
            const row = e.row;
            tooltipContent.value = chartData.value[row][8]; // Custom tooltip content from the data array
            tooltip.style.display = 'block';
            tooltip.style.left = `${mouseX.value + 10}px`; // Adjust position
            tooltip.style.top = `${mouseY.value + 10}px`;

            // Hide the default tooltip
            hideDefaultTooltip();
        });

        google.visualization.events.addListener(chart, 'onmouseout', () => {
            const tooltip = document.getElementById('custom-tooltip');
            tooltip.style.display = 'none';
        });

    };
    function removeChart() {
        const chartContainer = document.getElementById('roadmap-gantt');
        chartContainer.innerHTML = ''; // Clear the chart
    }

    const hideDefaultTooltip = () => {
        const ganttElement = document.getElementById('roadmap-gantt');
        if (ganttElement) {
            const svgElement = ganttElement.querySelector('svg');
            if (svgElement) {
                const lastChild = svgElement.lastElementChild;
                if (lastChild && lastChild.tagName === 'g' && lastChild.firstElementChild && lastChild.firstElementChild.tagName === 'g') {
                    lastChild.style.display = 'none';
                }
            }
        }
    };

    const handleMouseMove = (event) => {
        mouseX.value = event.clientX;
        mouseY.value = event.clientY;
    };

    const triggerRoadmapCreation = async () =>{
        return await axios.post(
            create_roadmap_api_1, 
            {},
            {            
                headers: {
                    'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`
                },
                params: {project_id: route.params.id}
            }
        )
        .then(async (response)=>{
            console.log("Used api: ", create_roadmap_api_1);
            console.log("Response: ", response.data);
            return await axios.post(
                create_roadmap_api_2, 
                {},
                {            
                    headers: {
                        'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`
                    },
                    params: {project_id: route.params.id}
                }
            )
            .then((response) =>{
                console.log("Used api: ", create_roadmap_api_2);
                console.log("Response: ", response.data);
                updateProjectData({roadmap_created: true})
                return true;
            })
            .catch((error)=>{
                console.log(error);
                return false;
            })

        })
        .catch((error)=>{
            console.log(error);
            return false;
        })
    }

    const getRoadmap = async ()=>{
        return await axios.get(
            get_roadmap_api(route.params.id),
            {            
                headers: {
                    'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`
                }
            }
        )
        .then((response)=>{
            console.log("Used api: ", get_roadmap_api(route.params.id));
            console.log("Response: ", response.data);
            chartData.value = processData(response.data)
            return true;

        })
        .catch((error)=>{
            console.log(error)
            return false;

        })
    }

    const regenerateRoadmap = async()=>{
        const answer = window.confirm('Be aware, that this also effects the report. It will be regenerated as well. Would you like to continue?')
        if(!answer) return;
        const data_reset = {roadmap_created:false, report_created: false}
        const success = await updateProjectData(data_reset);
        if(!success){
            window.alert("There has been a problem, we could not reset your data. Try again later.");
            return
        }
        removeChart();
        loading.value = true;
        blockApp();
        loading_text.value = "We are creating the roadmap for you, this can take some time. Please, be patient :)";
        const success_0 = await triggerRoadmapCreation();
        if(!success_0){
            showError();
            return;
        };
        const success_1 = await getRoadmap();
        if(!success_1){
            showError();
            return;
        };
        loading.value = false;
        blockApp(false);
        setTimeout(() => {
            drawChart();
            document.getElementById('roadmap-wrapper').addEventListener('mousemove', handleMouseMove);
        }, 500);
    }

    const updateProjectData = async (updated_project_data) =>{
            return await axios.put(
                `${projects_api}${route.params.id}`,
                updated_project_data,
                {
                    headers: {'Content-Type': 'application/json',
                            'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`}
                },
            )
            .then((response)=>{
                store.commit('loadProjects');
                console.log("Successfully updated roadmap status of project...");
                console.log(response);
                return true
            })
            .catch((error)=>{
                console.log(error);
                return false;
            })

    };

    const calculateDurationInMonths = (startDate, endDate) => {
        const startYear = startDate.getFullYear();
        const startMonth = startDate.getMonth();
        const endYear = endDate.getFullYear();
        const endMonth = endDate.getMonth();
        return (endYear - startYear) * 12 + (endMonth - startMonth);
    };

    const processData = (data) => {
        // Create a map to store action to id mapping
        const actionIdMap = {};
        const kmaMap = {}

        // First, assign IDs and build the action map
        data.forEach((item, index) => {
            kmaMap[index] = item.kma;
            item.actions.forEach(action => {
                actionIdMap[action] = index;
            });
        });
        return data.map((item,index) => {
            const startDate = new Date(item.start_date);
            const endDate = new Date(item.end_date);
            const duration = calculateDurationInMonths(startDate, endDate); // Calculate duration in months
            const dependency_list = item.dependencies.map(dep => actionIdMap[dep] !== undefined && actionIdMap[dep] !== index ? actionIdMap[dep] : undefined).filter(Boolean)
            const dependencies = dependency_list.join(',');
            
            // console.log("KMA: ",item.kma, index)
            // console.log("Dependencies: ",item.dependencies)
            // console.log("Actions: ", item.actions)
            // console.log("Dependencies FILTERED: ",dependency_list)
            // console.log("---------------------------------")
            const tooltip = `
            <div>
                <strong>${item.kma}</strong> (${duration} months)<br>
                Dependencies: ${dependency_list.map(i => kmaMap[i] ).join(', ')}<br>
                Actions: ${item.actions.join(', ')}<br>
                Check Tools: ${item.chek_tools.join(', ')}<br>
            </div>`;
            return [
            index.toString(),
            item.kma,
            '', // Actions column (empty string)
            startDate,
            endDate,
            null, // Duration column (null)
            0, // Percent Complete column (0)
            dependencies,
            tooltip // Custom tooltip
            ];
        });
    };

    function blockApp(block=true){
        app.classList.toggle("app-blocked");
        project_container.classList.toggle("project-container-active");
        project_content_window.classList.toggle("project-content-loading");
        if(block){
            overlay.style.display = "block";
        }
        else{
            overlay.style.display = "none";
        }
    };

    
    function showError(message="There has been an error :/"){
        error.value = true;
        loading_text.value =  message;
        blockApp(false);
    }
</script>

<style>
    #roadmap-wrapper{
        width: 100%; /* Adjust width to 100% for the wrapper */
        height: 100%;
        display: flex;
        flex-direction: column;

    }
    #roadmap-gantt {
        display: flex;
        width: 100%;
        height:  100%;
        overflow: auto;
        padding: 1rem;
    }

    #roadmap-wrapper::-webkit-scrollbar {
        display: block;
        /* Override to display scrollbar */
    }


    #roadmap-wrapper>*::-webkit-scrollbar {
        display: block;
        /* Override to display scrollbar */
    }
    #roadmap-wrapper text {
        white-space: normal;
        word-wrap: break-word;
    }

    .tooltip {
        position: absolute;
        display: none;
        top:0;
        left: 0;
        background-color: #fff;
        border: 1px solid #ccc;
        padding: 10px;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        white-space: nowrap;
        border-radius: 0.5rem;
        color: var(--noble-black-400);
        font-feature-settings: 'liga' off;
        /* Paragraph M/Bold */
        font-family: MyriadPro;
        font-size: 1rem;
        font-style: normal;
        font-weight: 200;
        line-height: 1.5rem; 
    }

    .loading-wrapper-roadmap{
        display: flex;
        width: 100%;
        height: 100%;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 1rem;
    }

    .chek-fonts{
        color: var(--noble-black-400);
        font-feature-settings: 'liga' off;
        /* Paragraph M/Bold */
        font-family: MyriadPro;
        font-size: 1rem;
        font-style: normal;
        font-weight: 200;
        line-height: 1.5rem; 
    }
    .loading-text-results{
        font-family: MyriadPro;
        font-size: 1.1rem;
        font-style: normal;
        font-weight: 700;
        color: var(--noble-black-400);
        white-space: pre;
        text-align: center;
    }

</style>

