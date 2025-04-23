<template>
    <div id="overlay-modeler"></div>
    <div class="button-container">
        <button id="break-out-btn" @click="emit('breakOut')" title="Unblock and break out of assesment"></button>
        <button v-if="!modeler_blocked" class="download-icon" @click="downloadBPMNFile" title="Download BPMN-file"></button>
    </div>

    <div class="content" id="js-drop-zone">
       <div class="canvas" id="js-canvas"></div>
    </div>
</template>

<script setup>
    import { onMounted, onBeforeUnmount, inject, ref } from 'vue';
    import {useRoute} from 'vue-router';

    import 'bpmn-js/dist/assets/diagram-js.css';
    import 'bpmn-js/dist/assets/bpmn-js.css';

    import 'bpmn-js/dist/assets/bpmn-font/css/bpmn-embedded.css';

    import $ from 'jquery';

    import BpmnModeler from 'bpmn-js/lib/Modeler';

    const route = useRoute();

    const base_api = inject('base_api');
    const bpmn_saving_api = base_api +"/bpmn/autosave";
    const bpmn_saved_api = base_api +"/bpmn/lastsave";

    let overlay, break_out_btn ,modeler, modeling, elementRegistry, canvas, container, selection,
        eventBus,label_editing_callback, missing_elements_maturity;
    let block_ai_request = false;
    const modeler_blocked = ref(false);

    const maturity_attr_name = "maturity_level";
    const maturity_descr_attr_name = "user_description";

    const maturity_color_code = {   
                                    "0": "#E6F7FF", // Very Light Blue
                                    "1": "#B3D9FF",
                                    "2": "#80BFFF",
                                    "3": "#4D9EFF",
                                    "4": "#1A80FF",
                                    "5": "#005CB2" // Moderately Dark Blue
                                }

    const maturity_model_extension = {
                                        name: "Maturity",
                                        prefix: "maturity",
                                        uri: "http://maturity",
                                        xml: {
                                            "tagAlias": "lowerCase"
                                        },
                                        associations: [],
                                        types: [{
                                            name: "ElementCHEK",
                                            extends: ["bpmn:BaseElement"],
                                            properties: [
                                                {
                                                "name": maturity_attr_name,
                                                "isAttr": true,
                                                "type": "String"
                                                },
                                                {
                                                "name": maturity_descr_attr_name,
                                                "isAttr": true,
                                                "type": "String"
                                                },
                                            ]
                                        }]
                                    }

    const emit = defineEmits(['taskChanged', 'breakOut']);

    defineExpose({updateBPMNLabel, setMaturityLevel, loadBPMNmodel,
                enableBpmnEditing, disableBpmnEditing, checkMetadataCompleteness, getLabelbyId, centerAndSelectElement, modeler_blocked});

    onMounted(async () => {
        overlay = document.getElementById("overlay-modeler");   
        break_out_btn = document.getElementById("break-out-btn");   
        container = $('#js-drop-zone');

        modeler = new BpmnModeler({
                  container: '#js-canvas',
                  keyboard: {
                      bindTo: window
                  },
                  moddleExtensions: {maturity: maturity_model_extension}
                });

        modeling = modeler.get('modeling');
        elementRegistry = modeler.get('elementRegistry');
        canvas = modeler.get('canvas');
        console.log(canvas);
        selection = modeler.get('selection');
        eventBus = modeler.get('eventBus');
        label_editing_callback = eventBus._listeners['element.dblclick'].callback;
        
        modeler.on('commandStack.element.updateLabel.executed', emitLabelUpdate); // This could make problems, maybe better to use the approach above (interactionLogger example)
        modeler.on('commandStack.changed', saveBPMNtoDatabase);        
    })

    onBeforeUnmount(()=>{
        // console.log("BMPN about to unmount!");
        document.getElementById("js-canvas").innerHTML = "";
    });

    async function loadBPMNmodel() {

        // Check if there is a saved bpmn model in the database
        fetch(`${bpmn_saved_api}/${route.params.id}/`, {
                    method: 'GET',
                    credentials: 'same-origin',
                    headers: {'Content-Type': 'application/json',
                            'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`}
        })
        .then(response => {
            if(!response.ok){
                console.log(response);
                console.log(`status: ${response.status} - ${response.statusText}`)
                window.alert("Oops! We could not fetch the last saved bpmn-model for this project.");
            }else{
                response.json()
                .then(response =>{
                    if(response.bpmnData){
                        loadXMLFile(response.bpmnData);
                    }else{
                        console.log("load TEMPLATE!");
                        loadXMLFile();
                    }
                    console.log(response);
                })
                .catch(error =>{
                    console.log(error);
                    window.alert("Oops! We could not fetch the last saved bpmn-model for this project.");
                });
            }
        })
        .catch(error =>{
            console.log(error);
            window.alert("Oops! We could not fetch the last saved bpmn-model for this project.");
        });

        async function loadXMLFile(savedModel = null){
            let xml;
            if(!savedModel){
                const file_stream = await fetch('/AS_IS_Map4GPT.bpmn');
                // const file_stream = await fetch('/AS_IS_Map4GPT_completed.bpmn');
                xml = await file_stream.text();
                console.log("BPMN template loaded");
            }else{
                xml = savedModel;
                console.log("Saved BPMN model loaded from database");
            }


            try {

                await modeler.importXML(xml);

                container
                .removeClass('with-error')
                .addClass('with-diagram');
            } catch (err) {

                container
                .removeClass('with-diagram')
                .addClass('with-error');

                container.find('.error pre').text(err.message);

                console.error(err);
            }
        }

    }

    function emitLabelUpdate(event){
        console.log(event);
        
        // // This is meant to prevent the user from changing the label of the building authority lane.
        // // But this can not be done here because we are at this point still in the excution phase of a command..
        // // Instead of directly reverting the label change within the event listener, you can use the commandInterceptor 
        // // to intercept the command and prevent it from being executed if the conditions are met.

        // if (event.context.element.type == "bpmn:Participant" && event.context.oldLabel.toLowerCase() === "building authority") {
        //     // Prevent the label change
        //     console.log("Label change prevented for participant 'Building authority'.");
        //     // Revert the label change
        //     modeling.updateLabel(event.context.element, event.context.oldLabel);
        //     return;
        // }
        
        if(!event.context.newLabel || block_ai_request || event.context.newLabel == event.context.oldLabel) return;

        const participant = findParticipant(event.context.element);
        if(!participant || participant.businessObject.name.toLowerCase() != "building authority") return;

        // if(event.context.element.type == "bpmn:Task"){
        if(event.context.element.type.toLowerCase().includes("task") || event.context.element.type.toLowerCase().includes("activity")){
            console.log(`Update label from '${event.context.oldLabel}' to '${event.context.newLabel}'`);
            const chatMessage = { chat_message: {
                                            human_message: `The user changed an action name to '${event.context.newLabel}'. Is there an associated action 
                                            in the document, which could be related to the new one?`
                                  },
                                  chat_settings: {
                                    language: "English",
                                    diagram_id: `${event.context.element.id}`
                                  }
                                };  
            
            disableBpmnEditing();
            emit('taskChanged', chatMessage);
        }
        else if (event.context.element.type.toLowerCase().includes("event")){
            let diagram_id;
            try {
                diagram_id = event.context.element.labels[0].id;
            } catch (error) {
                console.log("Label update could not be processed for AI.")
                return;
            }
            console.log(`Update label from '${event.context.oldLabel}' to '${event.context.newLabel}'`);
            const chatMessage = { chat_message: {
                human_message: `The user changed an event name to '${event.context.newLabel}'. Is there an associated event 
                                            in the document, which could be related to the new one?`
                                    },
                                    chat_settings: {
                                    language: "English",
                                    diagram_id: `${diagram_id}`
                                    }
                                };  
            
            emit('taskChanged', chatMessage);
            disableBpmnEditing();
        }
        // // For now we decided to exclude gateways
        // else if(event.context.element.type.toLowerCase().includes("gateway")){
        //     let diagram_id;
        //     try {
        //         diagram_id = event.context.element.labels[0].id;
        //     } catch (error) {
        //         console.log("Label update could not be processed for AI.")
        //         return;
        //     }
        //     console.log(`Update label from '${event.context.oldLabel}' to '${event.context.newLabel}'`);
        //     const chatMessage = { chat_message: {
        //                             human_message: `The user changed a gateway name to '${event.context.newLabel}'. Is there an associated gateway 
        //                                     in the document, which could be related to the new one?`
        //                             },
        //                             chat_settings: {
        //                             language: "English",
        //                             diagram_id: `${diagram_id}`
        //                             }
        //                         };  
            
        //     emit('taskChanged', chatMessage);
        //     disableBpmnEditing();
        // }
        else if(event.context.element.type == "label"){
            if(event.context.element.id.toLowerCase().includes("event")){
                console.log(`Update label from '${event.context.oldLabel}' to '${event.context.newLabel}'`);
                const chatMessage = { chat_message: {
                                                human_message: `The user changed an event name to '${event.context.newLabel}'. Is there an associated event 
                                                in the document, which could be related to the new one?`
                                      },
                                      chat_settings: {
                                        language: "English",
                                        diagram_id: `${event.context.element.id}`
                                      }
                                    };  
                
                emit('taskChanged', chatMessage);
                disableBpmnEditing();
            }
            // // For now we decided to exclude gateways
            // else if (event.context.element.id.toLowerCase().includes("gateway")){
            //     console.log(`Update label from '${event.context.oldLabel}' to '${event.context.newLabel}'`);
            //     const chatMessage = { chat_message: {
            //                             human_message: `The user changed a gateway name to '${event.context.newLabel}'. Is there an associated gateway 
            //                                     in the document, which could be related to the new one?`
            //                           },
            //                           chat_settings: {
            //                             language: "English",
            //                             diagram_id: `${event.context.element.id}`
            //                           }
            //                         };  
                
            //     emit('taskChanged', chatMessage);
            //     disableBpmnEditing();
            // }
        }
        
    }

    function findParticipant(element) {
        while (element) {
            if (element.type === 'bpmn:Participant') {
                return element;
            }
            element = element.parent;
        }
        return null;
    }


    function updateBPMNLabel(element_data){
        block_ai_request = true;
        modeling.updateLabel(elementRegistry.get(element_data.id), element_data.label_name);
        centerAndSelectElement(element_data.id);
        block_ai_request = false;
    }

    function getLabelbyId(id){
        // centerAndSelectElement(id);
        const label_name = elementRegistry.get(id).businessObject.name;
        return label_name;
    }

    async function setMaturityLevel(element_data_maturity){
        // centerAndSelectElement(element_data_maturity.id)
        let element = elementRegistry.get(element_data_maturity.id);
        if(element.type == "label"){
            const host_element = elementRegistry.get(element_data_maturity.id.replace("_label",""));
            if(host_element){
                element = host_element;
            }
        }
        const customPropertyString = `{ "${maturity_attr_name}" : "${element_data_maturity.level}" , "${maturity_descr_attr_name}" : "${element_data_maturity.description}" }`;
        const customPropertyJson = JSON.parse(customPropertyString);

        modeling.updateProperties(element, customPropertyJson);

        modeling.setColor([element], {
            stroke: "black",
            fill: maturity_color_code[element_data_maturity.level]
        });
        // enableBpmnEditing();
        await saveBPMNtoDatabase();
    }

    function centerAndSelectElement(elementId, just_center = false) {
        // assuming we center on a shape.
        // for connections we must compute the bounding box
        // based on the connection's waypoints
        var bbox = elementRegistry.get(elementId);

        var currentViewbox = canvas.viewbox();

        var elementMid = {
          x: bbox.x + bbox.width / 2,
          y: bbox.y + bbox.height / 2
        };

        const scaled_width = bbox.width/0.1;
        const scale_factor = scaled_width / currentViewbox.width
        // canvas.viewbox({
        //   x: elementMid.x - currentViewbox.width / 2,
        //   y: elementMid.y - currentViewbox.height / 2,
        //   width: currentViewbox.width,
        //   height: currentViewbox.height
        // });
        canvas.viewbox({
          x: elementMid.x - scaled_width / 2,
          y: elementMid.y - currentViewbox.height*scale_factor / 2,
          width: scaled_width,
          height: currentViewbox.height*scale_factor
        });
        if(!just_center){
            selection.select(bbox);
        }
    }

    async function saveBPMNtoDatabase(){
        await modeler.saveXML().then( async (xml) => {
            console.log("Model will be saved to database...");
            const timestamp = new Date( Date.now()).toISOString();
            const data = {bpmnData: xml.xml, created_at: timestamp};
            await fetch(`${bpmn_saving_api}/?project_id=${route.params.id}`, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {'Content-Type': 'application/json',
                            'Authorization': `Bearer ${window.sessionStorage.getItem("chek_access_token")}`},
                    body: JSON.stringify(data),
            })
            .then(response => {
                if(!response.ok){
                    console.log(`status: ${response.status} - ${response.statusText}`)
                    window.alert("Oops! It seems that your changes could not be saved. There seem to be a connection problem.");
                }
                else{
                    console.log("Model saved sucessfully!");
                }
            })
            .catch(error =>{
                console.log(error);
                window.alert("Oops! It seems that your changes could not be saved. There seem to be a connection problem.");
            });
            
        });
    }

    function disableBpmnEditing(){
        modeler_blocked.value = true;
        overlay.style.display = 'block';
        break_out_btn.style.display = 'flex';
        modeler.get('keyboard').unbind();
    }

    function enableBpmnEditing(){
        modeler_blocked.value = false;
        overlay.style.display = 'none';
        break_out_btn.style.display = 'none';
        modeler.get('keyboard').bind(document);        
    }

    function disableLabelEditing(){
        eventBus._listeners['element.dblclick'].priority = 100
        eventBus.on('element.dblclick', 1000, function(event) {
            return false; // will cancel event
        });
        console.log("Label editing disabled!");
        eventBus._listeners['element.dblclick'].next = null;
        console.log(eventBus);
    }

    function enableLabelEditing(){
        eventBus._listeners['element.dblclick'].priority = 100
        eventBus.on('element.dblclick', 1000, label_editing_callback);
        console.log("Label editing enabled!");
        eventBus._listeners['element.dblclick'].next = null;
        console.log(eventBus);
    }

    function checkMetadataCompleteness(){
        missing_elements_maturity = [];
        elementRegistry.forEach(function(element) {
            const participant = findParticipant(element);
            if(!participant || participant.businessObject.name.toLowerCase() != "building authority") return;

            if ((element.businessObject.$type && !element.businessObject.$type.toLowerCase().includes("gateway")) &&
                !(element.businessObject.$instanceOf("bpmn:Participant") || element.businessObject.$instanceOf("bpmn:StartEvent") ||
                element.businessObject.$instanceOf("bpmn:EndEvent") || element.businessObject.$instanceOf("bpmn:SequenceFlow") || 
                element.businessObject.$instanceOf("bpmn:MessageFlow") ||
                element.type == "label" || !element.parent)
                    && !element.businessObject[maturity_attr_name])
            {
                if(element.id && element.businessObject.name){
                    console.log(element.businessObject.$type);
                    missing_elements_maturity.push({id: element.id, name: element.businessObject.name});
                }
            }
        });
        // console.log(missing_elements_maturity);
        return missing_elements_maturity;
    }

    async function downloadBPMNFile() {
        await modeler.saveXML().then((xml) => {
            const blob = new Blob([xml.xml], { type: 'application/xml' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'model.bpmn';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            console.log("Model downloaded successfully!");
        }).catch(error => {
            console.log(error);
            window.alert("Oops! It seems that your model could not be downloaded.");
        });
    }

</script>

<style scoped>
    a:link {
    text-decoration: none;
    }

    .content,
    .content > div {
    width: 100%;
    height: 100%;
    overflow: hidden;
    }

    .content > .message {
    text-align: center;
    display: table;

    font-size: 16px;
    color: #111;
    }

    .content > .message .note {
    vertical-align: middle;
    text-align: center;
    display: table-cell;
    }

    .content .error .details {
    max-width: 500px;
    font-size: 12px;
    margin: 20px auto;
    text-align: left;
    }

    .content .error pre {
    border: solid 1px #CCC;
    background: #EEE;
    padding: 10px;
    }

    .content:not(.with-error) .error,
    .content.with-error .intro,
    .content.with-diagram .intro {
    display: none;
    }


    .content .canvas,
    .content.with-error .canvas {
    visibility: hidden;
    }

    .content.with-diagram .canvas {
    visibility: visible;
    }

    .buttons {
    position: relative;
    bottom: 2rem;
    left: 2rem;

    padding: 0;
    margin: 0;
    list-style: none;
    }

    .buttons > li {
    display: inline-block;
    margin-right: 10px;
    }
    .buttons > li > a {
    /* border: solid 1px #666; */
    display: inline-block;
    padding: 5px;
    /* Style */
    border-radius: var(--button---l, 0.75rem);
    background: var(--neutral--500, #6F7786);
    /* Typography */
    color: var(--neutral-0, var(--noble-black-0, #FFF));
    font-feature-settings: 'liga' off;
    /* Button/L */
    font-family: Arial, Helvetica, sans-serif;
    font-size: 0.7rem;
    font-style: normal;
    font-weight: 650;
    line-height: normal;
    /* cursor: pointer; */
    }

    .buttons a {
    opacity: 0.3;
    }

    .buttons a.active {
    opacity: 1.0;
    }

    #overlay-modeler{
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.5);
        /* some bpmn modeler items have z-index 100 */
        z-index: 101;
        display: none;
    }
    .button-container{
        display: flex;
        gap: 1rem;
        position: absolute;
        right: 0.5rem;
        top: 0.5rem;
        z-index: 102;
    }
    #break-out-btn{
        display: none;
        width:  1.25rem;
        height:  1.25rem;
        outline: none;
        border: none;
        background: center / contain no-repeat url(images/unlock.svg);
        flex-shrink: 0;
        cursor: pointer;

    }
    .download-icon{
        display: flex;
        background: center / contain no-repeat url(images/download_icon.svg);
        border: none;
        outline: none;
        width:  1.25rem;
        height:  1.25rem;
        cursor: pointer;
        align-self: center;
        filter: brightness(0) invert(0);
    } 
</style>