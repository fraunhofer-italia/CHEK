<template>
    <!-- TAB-BAR -->
    <div id="tab-bar" @click="selectTabClick">
        <div id="as-is-pmap" class="tab-item">
            <span class="tab-icon process-icon"></span>
            <div class="tab-item-label">
                AS-IS PROCESS MAP
            </div>
        </div>
        <div id="maturity" class="tab-item">
            <span class="tab-icon maturity-icon"></span>
            <div class="tab-item-label">
                MATURITY MODEL
            </div>
        </div>
        <div id="roadmap" class="tab-item">
            <span class="tab-icon roadmap-icon"></span>
            <div class="tab-item-label">
                ROADMAP
            </div>
        </div>
        <div id="results" class="tab-item" >
            <span class="tab-icon results-icon"></span>
            <div class="tab-item-label">
                RESULTS AND REPORT
            </div>
        </div>
    </div>

    <!-- CONTENT -->
    <div id="project-content" :class="['project-content-normal', { extended: isExtended }]">
        <div id="content-wrapper" v-show="current_tab_content == 'as-is-pmap'">
            <BPMN_modeler @task-changed="postBPMNchat" @break-out="breakOutAssessment" ref="BPMNComponentRef"></BPMN_modeler>
        </div>
        
        <Maturity v-if="current_tab_content == 'maturity'"></Maturity>
        <RoadMap v-if="current_tab_content == 'roadmap'"></RoadMap>
        <Results v-if="current_tab_content == 'results'"></Results>
    </div>

    <!-- CHAT -->
    <div id="chat" v-show="current_tab_content == 'as-is-pmap'">
        <!-- HERE ALL CHAT-MESSAGES WILL BE ADDED DYNAMICALLY -->
    </div>

    <!-- CHAT-INPUT-MESSAGE -->
    <div id="chat-input" class="box" v-show="current_tab_content == 'as-is-pmap'">

      <input type="text" id="chat-text-field" @keyup.enter="pushUserInputToChat" placeholder="Write your message...">

      <!-- <div id="chat-file-upload"></div> -->

      <div id="chat-submit-btn" @click="pushUserInputToChat">
        <span id="submit-icon"></span>
      </div>
    </div>

    <!-- Maturity Modal -->
    <div class="mat-modal" v-if="showMaturityModal">
        <!-- Modal content -->
        <div class="mat-modal-content">
            <p class="mat-modal-text">Before we can assess the maturity, we need further information on some of your processes. If you continue, follow the instructions in the chat!</p>
            <div class="modal-footer">
                <button class="submit-btn" @click="confirmModal">Yes, let's do it!</button>
                <button class="close-btn" @click="cancelModal">No, I want to continue editing the process map.</button>
            </div>
        </div>
    </div>

    <!--PreassesmentCompleteModal-->
    <div class="mat-modal" v-if="showPreassesmentCompleteModal">
        <!-- Modal content -->
        <div class="mat-modal-content">
            <p class="mat-modal-text">Yeay, now we have all the information regarding your processes. We can continue now with the maturity assesment! You just have to close this dialog and click on the "Maturity" tab...</p>
            <div class="modal-footer">
                <button class="submit-btn" @click="showPreassesmentCompleteModal= false">Ok</button>
            </div>
        </div>
    </div>
</template>


<script setup>
    import { onMounted, onBeforeUnmount, ref, inject, computed } from 'vue';
    import { useRoute} from 'vue-router';
    import Maturity from './Maturity.vue';
    import RoadMap from './RoadMap.vue';
    import Results from './Results.vue';
    import BPMN_modeler from './BPMN_modeler.vue';
    import axios from 'axios';
    import { useStore } from 'vuex';

    const store = useStore()

    const base_api = inject('base_api');
    const projects_api = base_api +"/projects/";
    let ai_chat_api_base = base_api +"/intellichek/basic_chat/";
    const ai_chat_api_intro = base_api +"/intellichek/introduction";
    const ai_chat_api_bpmn = base_api +"/intellichek/get-task-name";
    const ai_chat_api_maturity_alpha = (project_id) => `${base_api}/intellichek/${project_id}/maturity/alpha`;
    const ai_chat_api_maturity_intro = base_api +"/intellichek/maturity/introduction";
    const ai_chat_api_maturity_beta = base_api +"/intellichek/maturity/beta";
    const ai_chat_api_maturity_omega = base_api +"/intellichek/maturity/omega";

    const standard_chat_mode = "standard";
    const introduction_chat_mode = "intro";
    const maturity_chat_mode_beta = "maturity_assesment_beta";
    const maturity_chat_mode_omega = "maturity_assesment_omega";

    const current_tab_content = ref('');

    // Computed property to determine if the extended class should be added
    const isExtended = computed(() => current_tab_content.value !== 'as-is-pmap');

    const BPMNComponentRef = ref(null);

    const route = useRoute();

    const showMaturityModal = ref(false);
    const showPreassesmentCompleteModal = ref(false);

    // const props = defineProps({project_id: String})

    let chat_mode = standard_chat_mode;
    let current_action_data, missing_elements_maturity;
    let pre_maturity_assessed = false;
    
    let current_tab, chat, user_info, current_project;
    let sugg_count = 0;

    onMounted(() => {

        // assign HTML-Element of chat
        chat = document.getElementById("chat");
        chat.addEventListener('click', copyToClipboard);
        user_info = JSON.parse(window.sessionStorage.getItem("chek_user_info"));
        // Select first Tab by default
        current_tab = document.getElementById("tab-bar").children.item(0);
        current_tab.classList.toggle('active-item');
        const tab_icon = current_tab.children.item(0);
        const tab_label = current_tab.children.item(1);
        const tab_icon_name = tab_icon.classList.item(1);
        tab_icon.classList.toggle(tab_icon_name +'-active');
        tab_icon.classList.toggle(tab_icon_name);
        tab_label.classList.toggle('tab-item-label-active');

        current_tab_content.value = current_tab.id;

        
        BPMNComponentRef.value.loadBPMNmodel();

        // Intitalize chat: send project info from user as first chat message automatically then fetch ai response
        initializeChat();

    });

    onBeforeUnmount(() => {
        console.log('About to umount project page...');
        chat.removeEventListener('click', copyToClipboard);
        current_tab.classList.toggle('active-item');
        const current_icon = current_tab.children.item(0);
        const current_label = current_tab.children.item(1);
        const current_icon_class = current_icon.classList.item(1);

        current_icon.classList.toggle(current_icon_class.replace('-active', ''));
        current_icon.classList.toggle(current_icon_class);
        current_label.classList.toggle('tab-item-label-active');

        current_tab_content.value = '';
        console.log(current_tab);
    });

    function confirmModal(){
        showMaturityModal.value = false;
        completeMissingData();
    }
    function cancelModal(){
        showMaturityModal.value = false;
    }

    function breakOutAssessment(){
        if(document.getElementById('type-indicator')){
            window.alert("Please, wait for IntelliCheks response first!");
            return;
        }
        // chat mode back to standard and insert seperation line
        switchChatMode();
        const horizontal_line = `<hr class="sep-line">`;
        chat.insertAdjacentHTML('afterbegin', horizontal_line);

        const input_element = document.getElementById("chat-text-field");
        input_element.disabled = false;

        // unblock bpmn editor
        BPMNComponentRef.value.enableBpmnEditing();
        missing_elements_maturity= null;
        current_action_data = null;
        pre_maturity_assessed = false;
    }

    function selectTabClick(event) {
        if (BPMNComponentRef.value.modeler_blocked){
            window.alert("Either unblock the modeler and break out of the assessment or answer the questions in the chat before you continue...");
            return;
        }
        const tab_bar = document.getElementById("tab-bar");
        const parent = event.target.parentElement.parentElement;

        if(parent.isSameNode(tab_bar)){
            const tab_item = event.target.parentElement;
            if (!tab_item.isSameNode(current_tab)){
                
                const user_projects = store.state.projects;
                const current_project = user_projects.find(project => project.id == route.params.id);
                switch (tab_item.id) {
                    case "maturity":
                        if(!pre_maturity_assessed){
                            missing_elements_maturity = BPMNComponentRef.value.checkMetadataCompleteness();
                            if(missing_elements_maturity.length != 0){
                                showMaturityModal.value = true;
                                return;
                            }
                            else{
                                pre_maturity_assessed = true;
                            }
                        }
                        break;
                    case "roadmap":
                        if(!current_project.maturity_assessment){
                            window.alert('You have to complete the maturity assessment first!')
                            return;
                        }
                        break;
                    case "results":
                        if(!current_project.roadmap_created){
                            window.alert('You have to generate the roadmap first!')
                            return;
                        }
                        break;
                
                    default:
                        break;
                }

                // if(tab_item.id == "maturity" && !pre_maturity_assessed){
                //     missing_elements_maturity = BPMNComponentRef.value.checkMetadataCompleteness();
                //     if(missing_elements_maturity.length != 0){
                //         showMaturityModal.value = true;
                //         return;
                //     }
                //     else{
                //         pre_maturity_assessed = true;
                //     }
                // }

                // Remove old selection (label, icon , underlining)
                current_tab.classList.toggle('active-item');
                const current_icon = current_tab.children.item(0);
                const current_label = current_tab.children.item(1);
                const current_icon_class = current_icon.classList.item(1);

                current_icon.classList.toggle(current_icon_class.replace('-active', ''));
                current_icon.classList.toggle(current_icon_class);

                current_label.classList.toggle('tab-item-label-active');

                // Add new selection (label, icon , underlining)
                tab_item.classList.toggle('active-item');
                const tab_icon = tab_item.children.item(0);
                const tab_label = tab_item.children.item(1);

                const tab_icon_name = tab_icon.classList.item(1);
                tab_icon.classList.toggle(tab_icon_name+'-active');
                tab_icon.classList.toggle(tab_icon_name);

                tab_label.classList.toggle('tab-item-label-active');

                // Set new tab to current selection
                current_tab = tab_item;
                current_tab_content.value = tab_item.id;
                // console.log(current_tab_content);
            }

        }
    }

    async function initializeChat(){
        switchChatMode(introduction_chat_mode);
        chat_bot_typing();

        const backend_response = await getCurrentProject();
        if(backend_response){
            current_project = backend_response.name;
            ai_chat_api_base = `${ai_chat_api_base}${backend_response.id}`;
        }else{
            console.log("Could not get project info!");
            pushAiResponseToChat("There has been a connection problem. Please try again later and contact the support.");
            return;
        }

        const initial_user_input = {human_message: `My name is ${user_info.first_name} ${user_info.last_name}. The name of the municipality is ${user_info.municipality}.
                                            The project name is ${current_project}. The conversation has to be in ${user_info.language}.`};

        let ai_response_text;

        const ai_response = await post_message(initial_user_input, ai_chat_api_intro);
        if (ai_response){
            ai_response_text = ai_response.message;
        }else{
            ai_response_text = 'There has been a connection problem. Please try again later and contact the support.'
        }

        pushAiResponseToChat(ai_response_text,null, true);
        switchChatMode();
    }

    async function post_message(user_input, api){
        try{
            const res = await fetch(api, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {'Content-Type': 'application/json',
                            'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`},
                    body: JSON.stringify(user_input),
                    })


            const ai_response = await res.json();
            console.log("Used api: ", api);
            console.log("Send data: ",user_input);
            console.log("Response: ", ai_response);
            if (ai_response.message){
                return ai_response;
            }else{
                return null;
            }
        }catch(error){
            console.log(error);
            return null;
        }
    }

    async function postBPMNchat(chatMessage_object){
        chatMessage_object.chat_settings.language = user_info.language;
        chat_bot_typing();

        let ai_response_text;
        let meta_data;

        const ai_response = await post_message(chatMessage_object, ai_chat_api_bpmn);
       
        if (ai_response){
            ai_response_text = ai_response.message.chat_response;
            meta_data = ai_response; 
        }else{
            ai_response_text = 'There has been a connection problem. Please try again later and contact the support.';
        }

        pushAiResponseToChat(ai_response_text, meta_data, true);
    }

    function chat_bot_typing(){
        const typing_chat =
                    `<div id="type-indicator" class="chat-message-box">
                        <i class="check-icon"></i>
                        <div class="chat-message-container">
                            <div class="chat-message-header">
                                <div class="chat-name">IntelliCHEK</div>
                            </div>
                            <div class="chat-message">
                                <span class="dot"></span>
                                <span class="dot"></span>
                                <span class="dot"></span>
                            </div>
                        </div>
                    </div>`;
        chat.insertAdjacentHTML('afterbegin', typing_chat);        
    }

    async function pushUserInputToChat(){
        const input_element = document.getElementById("chat-text-field");
        const user_input = input_element.value.trim()

        if (user_input.length > 0){
            const new_user_message =
                `<div class="chat-message-box">
                    <!-- icon -->
                    <div class="user-icon">
                        ${user_info.first_name.charAt(0)}
                    </div>
                    <div class="chat-message-container">
                        <div class="chat-message-header">
                            <div class="chat-name">${user_info.first_name}</div>
                            <div class="chat-timestamp">${getCompactTimestamp()}</div>
                        </div>
                        <div class="chat-message">
                            ${user_input}
                        </div>
                    </div>
                </div>`;
            chat.insertAdjacentHTML('afterbegin', new_user_message)
            document.getElementById("chat-text-field").value = '';
            input_element.disabled = true;

            chat_bot_typing();
            let ai_api, ai_input;
            if(chat_mode == maturity_chat_mode_beta){
                ai_api = ai_chat_api_maturity_beta;
                ai_input = {maturity: {
                                action: current_action_data.label_name,
                                description: user_input,
                                },
                            chat_settings: {
                                language: user_info.language,
                                diagram_id: current_action_data.id,
                                }
                            };
            }
            else if (chat_mode == maturity_chat_mode_omega){
                ai_api = ai_chat_api_maturity_omega;
                ai_input = {maturity: {
                                action: current_action_data.label_name,
                                description: user_input,
                                },
                            chat_settings: {
                                language: user_info.language,
                                diagram_id: current_action_data.id,
                                }
                            };
            }
            else if(chat_mode == introduction_chat_mode){
                ai_api = ai_chat_api_intro;
                ai_input = {human_message: user_input};
            }
            else{
                ai_api = ai_chat_api_base;
                ai_input = {
                                chat_message: {human_message: user_input},
                                chat_settings: {
                                    language: user_info.language
                                }
                            };
            }


            const ai_response = await post_message(ai_input, ai_api);
            let ai_response_text;

            if (ai_response){
                if (chat_mode == maturity_chat_mode_beta){
                    ai_response_text = ai_response.message.chat_response;
                    if(ai_response.message.code.includes("Fail")){
                        switchChatMode(maturity_chat_mode_omega);
                        pushAiResponseToChat(ai_response_text, null, true);
                        return;
                    }else{
                        await finalizeMaturityLevel(ai_response)
                    }

                }else if(chat_mode == maturity_chat_mode_omega){
                    ai_response_text = ai_response.message.chat_response;
                    await finalizeMaturityLevel(ai_response);
                }
                else{
                    ai_response_text = ai_response.message;
                }
                
            }else{
                ai_response_text = 'There has been a connection problem. Please try again later and contact the support.'
            }
            pushAiResponseToChat(ai_response_text);
        }
        else{
            document.getElementById("chat-text-field").value = '';
        }

        async function finalizeMaturityLevel(ai_response){
            const maturity_level = cleanAiGeneratedLevel(ai_response);

            const element_data_maturity = {id: ai_response.diagram_id, 
                                            level: maturity_level,
                                            description: user_input
            };
                    
            await BPMNComponentRef.value.setMaturityLevel(element_data_maturity);

            if(missing_elements_maturity && missing_elements_maturity.length > 0){
                const index = missing_elements_maturity.findIndex(element => element.id === element_data_maturity.id);
                if(index != -1){
                    missing_elements_maturity.splice(index, 1);
                }
            }
            switchChatMode(); // switch back to standard
            BPMNComponentRef.value.enableBpmnEditing();
        }
    }

    function cleanAiGeneratedLevel(ai_response){
        let maturity_level;
        if(typeof ai_response.message.status === 'string' || ai_response.message.status instanceof String){
            maturity_level = ai_response.message.status.replaceAll("$", '');
        }
        else{
            maturity_level = String(ai_response.message.status);
        }
        return maturity_level;
    }

    function pushAiResponseToChat(message, meta_data = null, checking_blocked = false){
        const input_element = document.getElementById("chat-text-field");
        sugg_count += 1;
        const suggestion_container_id = `sugestions_${sugg_count}`;
        let suggestions = ``; 
        if (meta_data && meta_data.message.list_of_actions != "NONE"){
            meta_data.message.list_of_actions.forEach(suggestion => {
                suggestions += `<div class="chat-suggestions">
                                    ${suggestion}
                                </div>`
            });
            suggestions += `<div class="chat-suggestions keep-mine">
                                Keep my version
                            </div>`
        }else if(meta_data && meta_data.message.list_of_actions == "NONE"){
            BPMNComponentRef.value.enableBpmnEditing();
        }
        // for loop for suggestion - also tag id - add event listener on click
        const ai_response_html =
                        `<div class="chat-message-box">
                            <i class="check-icon"></i>
                            <div class="chat-message-container">
                                <div class="chat-message-header">
                                    <div class="chat-name">IntelliCHEK</div>
                                    <div class="chat-timestamp">${getCompactTimestamp()}</div>
                                    <div class="copy-btn" data-message="${message}"></div>
                                </div>
                                <div class="chat-message">
                                    ${message}
                                </div>
                                <div id="${suggestion_container_id}" class="suggestion-container">
                                    ${suggestions}
                                </div>
                            </div>
                        </div>`;
        
        if(document.getElementById('type-indicator')){
            document.getElementById('type-indicator').remove();
        }
        chat.insertAdjacentHTML('afterbegin', ai_response_html);
        input_element.disabled = false;

        if(suggestions != ""){
            input_element.disabled = true;
            const suggestion_container = document.getElementById(suggestion_container_id);
            suggestion_container.addEventListener("click", updateLabelAI);

            async function updateLabelAI(event){
                if(event.target.classList.contains("chat-suggestions") && meta_data){
                    let label_name;
                    if(event.target.classList.contains("keep-mine")){
                        label_name = BPMNComponentRef.value.getLabelbyId(meta_data.diagram_id);
                        current_action_data = {id: meta_data.diagram_id, label_name: label_name}
                    }else{
                        label_name = event.target.textContent.trim();
                        current_action_data = {id: meta_data.diagram_id, label_name: label_name}
                        BPMNComponentRef.value.updateBPMNLabel(current_action_data);
                    }
                    triggerMaturityIntro(label_name, meta_data.diagram_id);
                    suggestion_container.removeEventListener("click", updateLabelAI);
                }

            }
        }

        if(missing_elements_maturity && !checking_blocked){
            if(missing_elements_maturity.length > 0){
                console.log("Elements with missing level evaluation: ",missing_elements_maturity);
                completeMissingData();
            }else{
                if(BPMNComponentRef.value.checkMetadataCompleteness().length == 0){
                    showPreassesmentCompleteModal.value = true;
                }
            }
        }

    }

    function switchChatMode(mode = standard_chat_mode){
        chat_mode = mode;
        console.log(`Chat mode switched to '${mode}'`);
    }

    function getCompactTimestamp() {
        const now = new Date();
        const datePart = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const timePart = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

        return `${datePart} ${timePart}`;
    }

    const copyToClipboard = (event) => {
        if (event.target.classList.contains('copy-btn')) {
            const messageToCopy = event.target.getAttribute('data-message');
            navigator.clipboard.writeText(messageToCopy).then(function() {
                console.log('Text copied to clipboard');
            }).catch(function(err) {
                console.error('Could not copy text: ', err);
            });
        }
    }

    async function getCurrentProject(){
        const api = projects_api + `${route.params.id}`
        try{
            const res = await fetch(api, {
                    method: 'GET',
                    credentials: 'same-origin',
                    headers: {'Content-Type': 'application/json',
                            'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`},
                    })


            const backend_response = await res.json();
            console.log(backend_response);
            if (backend_response.name){
                return backend_response;
            }else{
                return null;
            }
        }catch(error){
            console.log(error);
            return null;
        }
    }

    async function completeMissingData(){
        const elem = missing_elements_maturity.at(0);
        console.log("Current BPMN element: " ,elem);
        current_action_data = {id: elem.id, label_name: elem.name};

        triggerMaturityIntro(elem.name, elem.id);
    }

    async function triggerMaturityIntro(element_name, element_id){
        BPMNComponentRef.value.disableBpmnEditing();
        BPMNComponentRef.value.centerAndSelectElement(element_id, true);
        chat_bot_typing();

        // 1st check if evaliuation of level can be done based on already existing information
        const data_alpha = {language: "English", diagram_id:element_id};
        const parameters = {project_id: route.params.id, maturity_action: element_name};
        const alpha_assesment = await axios.post(
            ai_chat_api_maturity_alpha(route.params.id), 
            data_alpha,
            {
                headers: {
                    'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`
                },
                params: parameters
        }
        )
        .then((response) => {
            console.log("Used api: ", ai_chat_api_maturity_alpha(route.params.id));
            console.log("Send data: ",parameters, data_alpha);
            console.log("Response: ", response.data);
            if(response.data.message.code.includes("Fail")){
                return null;
            }else{
                return response.data;
            }           
        })
        .catch(error => {
            console.log(error)
            return null;
        })

        // if yes, this action can already evaluated without any user input required
        if(alpha_assesment){
            console.log(alpha_assesment);
            const maturity_level = cleanAiGeneratedLevel(alpha_assesment);
            const element_data_maturity = {id: element_id, 
                                            level: maturity_level,
                                            description: alpha_assesment.message.description
            };
            await BPMNComponentRef.value.setMaturityLevel(element_data_maturity);
            if(missing_elements_maturity && missing_elements_maturity.length > 0){
                const index = missing_elements_maturity.findIndex(element => element.id === element_data_maturity.id);
                if(index != -1){
                    missing_elements_maturity.splice(index, 1);
                }
            }
            BPMNComponentRef.value.enableBpmnEditing();
            pushAiResponseToChat(alpha_assesment.message.chat_response);
            return;
        }

        // if no, the user will be asked to describe this action...
        const message_object = {chat_message: {
                                    human_message: element_name,
                                    },
                                chat_settings: {
                                    language: user_info.language,
                                    diagram_id: element_id
                                    }
                                };
        const ai_response = await post_message(message_object, ai_chat_api_maturity_intro);
        let ai_response_text;

        if (ai_response){
            ai_response_text = ai_response.message;
            switchChatMode(maturity_chat_mode_beta);
        }else{
            ai_response_text = 'There has been a connection problem. Please try again later and contact the support.'
        }

        pushAiResponseToChat(ai_response_text, null, true);        
    }

    // window.addEventListener('beforeunload', (event) => {
    //     const answer = window.confirm('Do you really want to leave? All processes will be aborted...')
    //     if (!answer) {
    //         event.preventDefault();
    //         event.returnValue = '';
    //     }
    // })
    
    // window.onbeforeunload = function(event)
    // {
    //     return confirm("Are you sure you want to leave? All your running processes will be aborted...");
    // };

    function logCaller() {
        try {
            throw new Error();
        } catch (e) {
            const stackLines = e.stack.split('\n');
            // The caller function should be in the 3rd line of the stack trace
            const callerLine = stackLines[3].trim();
            console.log('Caller:', callerLine);
        }
    }
</script>

<style>

/* TAB-BAR STYLES */

    #tab-bar{
        grid-area: hd;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        gap: 1rem;
        align-items: center;
        margin: 2vh 0.5vh 0.5vh;
        padding: 0 2rem;
    }
        .tab-item{
            display: flex;
            flex-direction: row;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
            border-bottom: 1px solid var(--neutral--100, #DCDEE2);
            height: 100%;
            width: 19.5%;
            flex-wrap: nowrap;
        }
        .active-item{
            border-bottom: 3px solid var(--brand--500, #82DBF7);
        }
            .tab-item-label{
                color: var(--neutral--300, #A8ADB6);
                font-feature-settings: 'liga' off;
                /* Button/L */
                font-family: Roboto;
                font-size: 0.95rem;
                font-style: normal;
                font-weight: 650;
                line-height: normal;
                cursor: pointer;
                text-wrap: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .tab-item-label-active{
                color: var(--brand--700, var(--heisenberg-blue-700, #4C8FA4));
            }
            .tab-icon{
                display: flex;
                width: 1.25rem;
                height: 1.25rem;
                cursor: pointer;
                flex-shrink: 0;
            }
            .process-icon{
                background: center / contain no-repeat url(images/process_inactive.svg);
            }
            .process-icon-active{
                background: center / contain no-repeat url(images/process_active.svg);
            }
            .maturity-icon{
                background: center / contain no-repeat url(images/maturity_inactive.svg);
            }
            .maturity-icon-active{
                background: center / contain no-repeat url(images/maturity_active.svg);
            }
            .roadmap-icon{
                background: center / contain no-repeat url(images/roadmap_inactive.svg);
            }
            .roadmap-icon-active{
                background: center / contain no-repeat url(images/roadmap_active.svg);
            }
            .results-icon{
                background: center / contain no-repeat url(images/results_inactive.svg);
            }
            .results-icon-active{
                background: center / contain no-repeat url(images/results_active.svg);
            }

/* CONTENT SYTLES */
    #project-content{

    }
    .project-content-normal{
        grid-area: main;
        margin: 0.5rem;
        overflow: hidden;
        border-radius: 0.2rem;
        /* flex-grow: 0; */
    }
    .project-content-loading{
        z-index: 11;
        background-color: #ffffff9a;
        border-radius: 0.3rem;
    }
    .extended {
        grid-area: main / main / ft / chat;
    }
    #content-wrapper{
        /* display: flex;
        flex-direction: column; */
        position: relative;
        width: 100%;
        height: 100%;
    }

/* CHAT STYLES */

    #chat{
        grid-area: chat;
        display: flex;
        /* flex-direction: column; */
        flex-direction: column-reverse;
        background: var(--noble-black-100, #E8E9E9);
        justify-content: flex-start;
        align-items: center;
        gap: 0.5rem;
        padding: 0.625rem;
        overflow-y: auto;
        /* overflow-x: hidden; */
    }
        .chat-message-box{
            display: flex;
            flex-direction: row;
            justify-content: flex-start;
            padding: 1rem;
            align-self: stretch;
            background: var(--noble-black-50, #F5F5F5);
            gap: 1.5rem;
            /* Shadow/S */
            box-shadow: 0px 1px 2px 0px rgba(24, 30, 39, 0.06), 0px 1px 3px 0px rgba(24, 30, 39, 0.10);
            /* flex-wrap: wrap; */
        }
        .chat-template{
            display: none;
        }
            .check-icon{
                display: flex;
                flex-shrink: 0;
                background: center / contain no-repeat url(images/favicon.svg);
                width: 2rem;
                height: 2rem;
            }
            .user-icon{
                display: flex;
                width: 2rem;
                height: 2rem;
                justify-content: center;
                align-items: center;
                flex-shrink: 0;

                border-radius: 50%;
                /* border-radius: var(--full, 624.9375rem); */
                border: 2px solid var(--heisenberg-blue-600);
                background: transparent;

                color: var(--brand--700, var(--heisenberg-blue-700, #4C8FA4));
                text-align: center;
                font-feature-settings: 'liga' off;
                /* Paragraph M/Bold */
                font-family: Plus Jakarta Sans;
                font-size: 1rem;
                font-style: normal;
                font-weight: 700;
                line-height: 1.5rem; /* 150% */
            }
            .chat-message-container{
                display: flex;
                flex-direction: column;
                align-self: stretch;
                flex-grow: 1;
                gap: 0.62rem;
                max-width: 100%;
            }
                .chat-message-header{
                    display: flex;
                    flex-direction: row;
                    justify-content: flex-start;
                    align-items: center;
                    flex-grow: 1;
                    gap: 0.75rem;
                    flex-wrap: wrap;
                }
                    .chat-name{
                        color: var(--heisenberg-blue-800, #335F6D);
                        /* Body/L/SemiBold */
                        font-family: Plus Jakarta Sans;
                        font-size: 1rem;
                        font-style: normal;
                        font-weight: 600;
                        line-height: 1.5rem; /* 150% */
                        letter-spacing: 0.00938rem;
                    }
                    .chat-timestamp{
                        color: var(--noble-black-400, #686B6E);
                        /* Body/S/Medium */
                        font-family: Plus Jakarta Sans;
                        font-size: 0.75rem;
                        font-style: normal;
                        font-weight: 500;
                        line-height: 1.125rem; /* 150% */
                        letter-spacing: 0.00938rem;
                    }
                    .copy-btn{
                        background:  center / contain no-repeat url(images/clipboard_copy.svg);
                        width: 1rem;
                        height: 1rem;
                        flex-shrink: 0;
                        margin-left: auto;
                        cursor: pointer;
                    }
                .chat-message{
                    display: flex;
                    color: var(--noble-black-400, #686B6E);
                    /* Body/L/Medium */
                    font-family: Plus Jakarta Sans;
                    font-size: 1rem;
                    font-style: normal;
                    font-weight: 500;
                    line-height: 1.5rem; /* 150% */
                    letter-spacing: 0.00938rem;
                    align-self: stretch;
                    /* word-break: break-all;  */
                    word-wrap: break-word;
                }
                .suggestion-container{
                    display: flex;
                    flex-direction: column;
                    gap: 0.5rem;
                }
                .chat-suggestions{
                    border-radius: 0.5rem;
                    border: 1px solid var(--neutral--100, #DCDEE2);
                    color: var(--neutral--500, #6F7786);
                    font-feature-settings: 'liga' off;
                    /* Button/S */
                    font-family: Arial, Helvetica, sans-serif;
                    font-size: 0.8rem;
                    font-style: normal;
                    font-weight: 650;
                    line-height: normal;
                    padding: 0.25rem 0.5rem;
                    /* max-width:100%; */
                    width: fit-content;
                    cursor: pointer;
                    word-wrap: break-word;
                    /* word-break: break-all; */
                }
                .keep-mine{
                    /* border: none; */
                    font-weight: 300;
                    font-size: 0.7rem;
                }

                .dot {
                    animation: dot 1s infinite;
                    height: 0.4rem;
                    width: 0.4rem;
                    background-color: var(--noble-black-300);
                    border-radius: 50%;
                    display: flex;
                }

                .dot:nth-child(2) {
                    animation-delay: 0.2s;
                }

                .dot:nth-child(3) {
                    animation-delay: 0.4s;
                }

                @keyframes dot {

                    0%,
                    80%,
                    100% {
                        transform: scale(0);
                    }

                    40% {
                        transform: scale(1);
                    }
                }


/* CHAT USER-INPUT FIELD STYLES */

    #chat-input{
        grid-area: ft;
        display: flex;
        flex-direction: row;
        justify-content: flex-end;
        align-items: center;
        padding: 0 1.5rem;
        gap: 1.5rem;
    }
        #chat-text-field{
            display: flex;
            height: 100%;
            color: var(--noble-black-500, #686B6E);
            background: transparent;
            border: none;
            outline: none;
            /* Body/L/Medium */
            font-family: Plus Jakarta Sans;
            font-size: 1rem;
            font-style: normal;
            font-weight: 500;
            line-height: 1.5rem; /* 150% */
            letter-spacing: 0.00938rem;
            flex-grow: 1
        }
        #chat-file-upload{
            display: flex;
            width:  1.25rem;
            height:  1.25rem;
            background: center / contain no-repeat url(images/attach.svg);
            flex-shrink: 0;
            cursor: pointer;
        }
        #chat-submit-btn{
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 0.75rem;
            background: var(--brand--500, #82DBF7);
            width: 2.5rem;
            height: 2.5rem;
            /* Shadow/XS */
            box-shadow: 0px 1px 2px 0px rgba(24, 30, 39, 0.08);
            cursor: pointer;
        }
            #submit-icon{
                display: flex;
                background: url(images/submit.svg);
                width: 1.25rem;
                height: 1.25rem;
            }
/* The Modal (background) */
.mat-modal {
    display: flex;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    justify-content: center;
    align-items: center;
    z-index: 1;
}

/* Modal Content/Box */
.mat-modal-content {
    display: flex;
    flex-direction: column;
    background: #fff;
    border-radius: 1rem;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.5);
    min-width: 50vw;
    padding: 2rem;
}
.mat-modal-text{
    color: var(--neutral--500);
    text-align: center;
    font-feature-settings: 'liga' off;
    /* Heading XS/Regular */
    font-family: Montserrat;
    font-size: 1rem;
    font-style: normal;
    font-weight: 400;
    line-height: 2rem; /* 133.333% */
}

.modal-footer{
    display: flex;
    flex-direction: row;
    /* justify-content: space-between; */
    justify-content: center;
    padding: 0 2rem 2rem;
    gap: 1rem;
}
.close-btn{
    /* Style */ 
    border-radius: 0.75rem;
    width:50%;
    min-height: 2rem;
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
    padding: 0.5rem;
}
.submit-btn{
    /* Style */ 
    border-radius: 0.75rem;
    width:50%;
    min-height: 2rem;
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
    padding: 0.5rem;
}
.sep-line{
    border-top: 1px solid var(--noble-black-300, #686B6E);
    width: 100%;
}

</style>