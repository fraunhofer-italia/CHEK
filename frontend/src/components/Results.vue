<template>
    <div id="results-container">
        <div id="report-container">
            <div class="header-wrapper">
                <select id="matruity-dropdown" v-model="selectedReport" @change="selectReport" placeholder="Reports...">
                    <option v-for="report in reports" :key="report.label" :value="report.label">{{ report.label }}</option>
                </select>
                <button class="download-icon" title="Download complete report as PDF" @click="printToPdf"></button>
                <button class="refresh-icon" title="Regenerate report" @click="regenerateReport"></button>
            </div>
            <div class="report-mark-down" v-html="compiledMarkdown"></div>
        </div>
        <div id="loading-wrapper-results">
            <div id="loading-spinner-results" class="results-load-btn"></div>
            <div id="loading-text-results"></div>
        </div>
    </div>
</template>
  
<script setup>
    import { ref, onMounted, inject } from 'vue';
    import { useRoute } from 'vue-router';
    import { useStore } from 'vuex';
    import {marked} from 'marked';
    // import { jsPDF } from "jspdf";
    // import "jspdf-autotable";
    import html2pdf from 'html2pdf.js';

    import * as echarts from 'echarts';

    import axios from 'axios';
    
    const route = useRoute();
    const store = useStore();
    
    const base_api = inject('base_api');
    const projects_api = base_api +"/projects/";
    const as_is_report_api = base_api +"/reports/as_is_process/";
    const maturity_report_api = base_api + "/reports/maturity/";
    const roadmap_report_api = base_api + "/reports/roadmap/";

    let selectedReport = '';

    const compiledMarkdown = ref('');


    const reports = [
                        {label: "As-Is Process", api: as_is_report_api}, 
                        {label: "Maturity", api: maturity_report_api},
                        {label: "Roadmap", api: roadmap_report_api}
    ]
    let reports_markdown = {
                            "As-Is Process": null,
                            "Maturity": null,
                            "Roadmap": null
    }

    let current_project, project_id;

    let app;
    let overlay;
    let project_container;
    let project_content_window,report_container, loading_container;

    onMounted(async () => {
        project_id = route.params.id;
        // set reference of html elements
        report_container = document.getElementById("report-container");
        loading_container = document.getElementById("loading-wrapper-results");

        app = document.getElementById("app");
        overlay = document.getElementById("overlay-block");
        project_container = document.getElementById(`${project_id}`);
        project_content_window = document.getElementById("project-content");

        const user_projects = store.state.projects;
        current_project = user_projects.find(project => project.id == project_id);
        let report_created =  current_project.report_created;
        const maturity_asessed = current_project.maturity_assessment;
        const roadmap_created = current_project.roadmap_created;

        blockApp();


        if(!maturity_asessed){
            loading_container.style.display = "flex";
            showError(true,"You need to do the maturity assessment first. Go to the 'Maturity' Tab.")
            return;
        }
        else if(!roadmap_created){
            loading_container.style.display = "flex";
            showError(true, "We need to create the roadmap first. Go to the 'Roadmap' Tab.")
            return;
        }

        if(report_created){
            const fetched_report = await getReportData();
            if(fetched_report){
                loading_container.style.display = "none";
                report_container.style.display = "flex";
            }else{
                loading_container.style.display = "flex";
                showError();
                return;
            }
        }else{
            // show loading spinner and text
            loading_container.style.display = "flex";
            const report_created = await createReport();
            if(report_created){
                loading_container.style.display = "none";
                report_container.style.display = "flex";
            }else{
                showError();
                return;
            }

        }
        blockApp(false);
        selectReport();

    });

    function selectReport(){
        switch (selectedReport) {
            case reports[0].label:
                compiledMarkdown.value = reports_markdown[reports[0].label];
                break;
            case reports[1].label:
                compiledMarkdown.value = reports_markdown[reports[1].label];
                break;
            case reports[2].label:
                compiledMarkdown.value = reports_markdown[reports[2].label];
                break;
            default:
                selectedReport = reports[0].label;
                compiledMarkdown.value = reports_markdown[reports[0].label];
                break;
            }        
    }
    
    async function createReport () {
        const loading_text = document.getElementById("loading-text-results");
        
        const dummy_body = {
                                language: "English",
                            };
        for (const  [index, report] of reports.entries()) {
            loading_text.textContent = `The following process can take a couple of minutes. Please be patient.\r\nCreate ${report.label} Report... (${index+1}/${reports.length})`;
            try {
                const response = await fetch(`${report.api}${project_id}`, {
                                    method: 'POST',
                                    credentials: 'same-origin',
                                    headers: {'Content-Type': 'application/json',
                                            'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`},
                                    body: JSON.stringify(dummy_body),
                                });
                if(!response.ok){
                    console.log(`status: ${response.status} - ${response.statusText}`);
                    return false;
                }
                const markdown = await response.json();
                console.log(markdown);
                if(report.label == "Maturity"){
                    const text_with_charts = await includeCharts(markdown.message);                    
                    reports_markdown[report.label] = marked(text_with_charts);
                }else{
                    reports_markdown[report.label] = marked(markdown.message);
                }
            } catch (error) {
                console.error(error);
                return false;
            }
        }

        console.log("Report creation completed!");

        const updated_project_data = { report_created: true}
        await updateProjectData(updated_project_data)
        return true;
    };
    async function getReportData(){
        for (const  [index, report] of reports.entries()) {
            try {
                const response = await fetch(`${report.api}${project_id}`, {
                                    method: 'GET',
                                    credentials: 'same-origin',
                                    headers: {'Content-Type': 'application/json',
                                            'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`},
                                });
                if(!response.ok){
                    console.log(`status: ${response.status} - ${response.statusText}`);
                    return false;
                }
                const markdown = await response.json();
                if(report.label == "Maturity"){
                    const text_with_charts = await includeCharts(markdown.last_content);
                    
                    reports_markdown[report.label] = marked(text_with_charts);
                }else{
                    reports_markdown[report.label] = marked(markdown.last_content);
                }

            } catch (error) {
                console.error(error);
                return false;
            }
        }
        return true;
    };
    async function regenerateReport (){
        const answer = window.confirm('This action cannot be undone. Would you like to continue?')
        if(!answer) return;
        const data_reset = { report_created: false}
        const success = await updateProjectData(data_reset);
        if(!success){
            window.alert("There has been a problem, we could not reset your data. Try again later.");
            return
        }
        
        blockApp();
        loading_container.style.display = "flex";
        report_container.style.display = "none";
        const report_created = await createReport();
        if(report_created){
            loading_container.style.display = "none";
            report_container.style.display = "flex";
        }else{
            showError();
            return;
        }
        blockApp(false);
        selectReport();

    };

    async function updateProjectData(updated_project_data){
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
                console.log("Successfully updated report status of project...");
                console.log(response);
                return true
            })
            .catch((error)=>{
                console.log(error);
                return false;
            })
    }

    function showError(spinner=true, message='There has been an error :/'){
        if (spinner){
            const loading_spinner = document.getElementById("loading-spinner-results");
            loading_spinner.style.display = "none";
        }
        const loading_text = document.getElementById("loading-text-results");
        loading_text.textContent = message;
        blockApp(false);
    }

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
    }
    // const printToPdf = async () => {
    //     const final_pdf = new jsPDF({
    //         format: 'a4',
    //         unit: 'cm',
    //     });

    //     for (const [key, value] of Object.entries(reports_markdown)) {
    //         const sub_pdf = new jsPDF({
    //             format: 'a4',
    //             unit: 'cm',
    //         });
    //         const htmlContent = value;

    //         // Extract tables from HTML content
    //         const parser = new DOMParser();
    //         const doc = parser.parseFromString(htmlContent, 'text/html');
    //         const tables = doc.querySelectorAll('table');

    //         // Render non-table content
    //         let nonTableHtml = doc.body.innerHTML;
    //         tables.forEach((table) => {
    //             nonTableHtml = nonTableHtml.replace(table.outerHTML, '');
    //         });
    //         // console.log("Non-tables: " ,nonTableHtml);
    //         // console.log("Tables:", tables);

    //         // // Render each table separately using AutoTable
    //         // tables.forEach((table, index) => {
    //         //     let pdf = new jsPDF({
    //         //         format: 'a4',
    //         //         unit: 'cm',
    //         //     });
    //         //     pdf.autoTable({ html: table, theme: 'plain'});
    //         //     // yPosition = pdf.previousAutoTable.finalY + 2;
    //         //     pdf.save(`Check_report_table${index}.pdf`);
    //         // });
    //         // Remove <code> and </code> tags using regex
    //         nonTableHtml = nonTableHtml.replace(/<code>/g, '');
    //         nonTableHtml = nonTableHtml.replace(/<\/code>/g, '');
    //         console.log(nonTableHtml);

    //         await sub_pdf.html(nonTableHtml, {
    //             // callback: function (pdf) {
                    
    //             // },
    //             x: 0,
    //             y: 0,
    //             margin: [2, 2, 2, 2], // 2 cm margin on all sides
    //             width: sub_pdf.internal.pageSize.getWidth(),
    //             height: sub_pdf.internal.pageSize.getHeight(),
    //             windowWidth: 800,
    //             autoPaging: 'text',
    //         });
    //         sub_pdf.save('Chek_report.pdf');
    //     }

    //     // final_pdf.save('Chek_report.pdf');
    // };

    const printToPdf = async () => {
        let htmlContent = ''
        for (const [key, value] of Object.entries(reports_markdown)) {
            htmlContent += value;

        }
        // // Find the position of the first <h1> tag
        // let h1Start = htmlContent.indexOf("<h1");

        // // Check if <h1> tag is found
        // if (h1Start !== -1) {
        //     // Insert the id attribute right after the <h1 tag
        //     let insertionPoint = h1Start + 3; // 3 is the length of "<h1"
        //     htmlContent = htmlContent.slice(0, insertionPoint) + " id='first_header'" + htmlContent.slice(insertionPoint);
        // }

        // Create a container element to hold the HTML content
        const container = document.createElement('div');
        container.style.fontFamily = 'MyriadPro';
        container.innerHTML = htmlContent;

        // Use html2pdf.js to render the HTML content to PDF
        const opt = {
            margin: [1, 1, 1, 1], // 1 cm margin on all sides
            filename: 'Check_report.pdf',
            image: { type: 'png', quality: 0.98 },
            html2canvas: { scale: 3 },
            jsPDF: { unit: 'cm', format: 'a4', orientation: 'portrait' },
            pagebreak: { mode: 'avoid-all', before: '', after: '', avoid:'' }
        };

        await html2pdf().from(container).set(opt).save();
    };

    const includeCharts = async (report_text)=>{
        let text_with_charts = report_text;
        const placeholderId = '§$%PICTURE§$%';
        let chart_data = store.state.maturity_data[route.params.id];
        if(!chart_data){
            await store.dispatch('loadMaturityData', route.params.id);
            chart_data = store.state.maturity_data[route.params.id];
        }
        for (const [key, value] of Object.entries(chart_data)) {
            text_with_charts = generateChartImage(placeholderId, text_with_charts, value)
        }
        return text_with_charts;
    }

    // Function to convert the chart to an image and replace the placeholder
    function generateChartImage(placeholderId, reportText, data, width = '750px', height = '750px') {
        const chart_temp_div = document.createElement('div');
        chart_temp_div.id = "chart_temp";
        chart_temp_div.style.height = "1000px";
        chart_temp_div.style.width = "1000px";
        // chart_temp_div.style.padding = "100px";
        // document.body.appendChild(chart_temp_div)
        const chartInstance = echarts.init(chart_temp_div);
        const chart_data = writeChartData(data);
        chartInstance.setOption(chart_data);
        chartInstance.resize();

        const base64Image = chartInstance.getDataURL({
            type: 'png',
            pixelRatio: 2,
            backgroundColor: '#fff'
        });

        // const markdownImage = `![Radar Chart](${base64Image})`;
        const markdownImage = `<br><br><img src="${base64Image}" alt="Radar Chart" style="width:${width};height:${height};"/>`;

        const updatedReportText = reportText.replace(placeholderId, markdownImage);
        return updatedReportText;
       }

    function writeChartData(api_data) {
        const indicatorData = api_data.map((item, index) => {
            let showAxisLabel = index === 0;
            let label = item.label.length > 20 ? breakLines(item.label, 20) : item.label;
            return { name: label, max: 5, axisLabel: { show: showAxisLabel } };
        });

        const seriesData = api_data.map((item) => item.level);
        const benchmark_data = api_data.map((item) => item.benchmark);

        // Function to break lines
        function breakLines(text, linelength) {
            const linebreak = '\n';
            let counter = 0;
            let line = '';
            let returntext = '';
            let bMatchFound = false;
            let linelen = 20;

            if (linelength) {
                linelen = linelength;
            }

            if (!text) { return ''; }
            if (text.length < linelen + 1) { return text.trim(); }

            while (counter < text.length) {
                line = text.slice(counter, counter + linelen);
                bMatchFound = false;

                if (line.length === linelen) {
                    for (let i = line.length; i > -1; i--) {
                        if (line.slice(i, i + 1) === ' ') {
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
        }


        return {
            legend: {
                data: ['CHEK Benchmark', 'Your Maturity Level'],
                selectedMode: false
            },
            radar: {
                indicator: indicatorData,
                // Set the center and radius of the radar chart
                center: ['50%', '50%'],
                radius: '60%', // Adjust the radius to leave enough space for labels
            },
            series: [{
                type: 'radar',
                name: "dummy-name",
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
                ]
            }]
        };
    }


</script>

<style>
    #results-container{
        display: flex;
        width: 100%;
        height: 100%;
        justify-content: center;
    }
    #report-container{
        display: none;
        padding: 1rem;
        flex-direction: column;       
        width: 100%;
        gap: 1rem;
    }

    .report-mark-down{
        display: block;
        font-family: MyriadPro;
        color: var(--noble-black-500);
        flex-grow: 1;
        overflow-y: auto;
    }

    #loading-wrapper-results{
        display: none;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 1rem;
    }

    .results-load-btn {
        display: flex;
        border: 0.5rem solid #f3f3f3; /* Light grey */
        border-top: 0.5rem solid grey; /* Blue */
        border-radius: 50%;
        width: 10rem;
        height: 10rem;
        animation: spin 3s linear infinite;
    }
    #loading-text-results{
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

    .download-icon{
        display: flex;
        background: center / contain no-repeat url(images/download_icon.svg);
        border: none;
        outline: none;
        width: 1.5rem;
        height: 1.5rem;
        cursor: pointer;
        align-self: center;
    }  
    /* Add this CSS to your existing styles */
    h1, h2, h3, h4, h5, h6 {
    page-break-inside: avoid;
    }
</style>
  