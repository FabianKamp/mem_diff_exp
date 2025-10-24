// LM INSTRUCTIONS
function createLMInstructions() {
    const lm_base_layout = () => `
        <div>
            <p style="font-family: 'Courier New', monospace; font-size: x-large; position: absolute; top: 50px; left: 50%;
                    transform: translateX(-50%); color:#4682B4; text-align: center;">
                <strong>Have you seen this image before?</strong>
            </p>
            <img src="stimuli/instructions/sample1.jpg" style="position: absolute; border-radius:10px;
                                    height:200px; width:200px; top: 45%; left: 50%;
                                    transform: translate(-50%, -50%);"/>
            `;

    const lm_scale_labels = () => `
            <div style="position: absolute; top: 68%; left: 50%; transform: translateX(-50%);
                        width: 100px; height: 10px; display: flex; align-items: center;">
                <div style="width: 0; height: 0; border-right: 8px solid rgba(51, 51, 51, 0.2); border-top: 5px solid transparent; border-bottom: 5px solid transparent;"></div>
                <div style="flex: 1; height: 2px; background: linear-gradient(to right, rgba(51, 51, 51, 0.2) 0%, rgba(51, 51, 51, 0.15) 10%, rgba(51, 51, 51, 0.05) 40%, rgba(51, 51, 51, 0.01) 50%, rgba(51, 51, 51, 0.05) 60%, rgba(51, 51, 51, 0.15) 90%, rgba(51, 51, 51, 0.2) 100%);"></div>
                <div style="width: 0; height: 0; border-left: 8px solid rgba(51, 51, 51, 0.2); border-top: 5px solid transparent; border-bottom: 5px solid transparent;"></div>
            </div>
            <p style="font-family: 'Courier New', monospace; font-size: large; position: absolute; top: 65%; left: 40%; transform: translateX(-50%);">No</p>
            <p style="font-family: 'Courier New', monospace; font-size: large; position: absolute; top: 65%; left: 60%; transform: translateX(-50%);">Yes</p>`;

    const lm_slider = () => `
        <div style="position: absolute; top: 70%; left: 50%; transform: translateX(-50%); width: 320px;">
                <input type="range" class="jspsych-slider" value="50" min="5" max="95" step="15" disabled/>
                <div>
                    ${['certain', 'probably', 'guess', ' ', 'guess', 'probably', 'certain'].map((label, i) =>
                        `<div style="border: 1px solid transparent; display: inline-block; position: absolute; left:calc(${i * 16.67}% - (16.67% / 2) - ${i === 1 ? '-1.25px' : i === 2 ? '-2.5px' : i === 4 ? '2.5px' : i === 5 ? '1.25px' : '0px'}); text-align: center; width: 16.67%;"><span style="text-align: center; font-size: 80%; font-family: 'Courier New', monospace; transform: rotate(-30deg); display: inline-block;">${label}</span></div>`
                    ).join('')}
                </div>
            </div>`;

    // LM recognition slides
    lm_recognition_slide_1 = lm_base_layout() + `
            <p class="instruction-paragraph-left">
                <strong>Have you seen this image?</strong><br><br>
                Now we would like to know if you can still remember the images from the task before. <br><br>
                You will see images which were shown in the task before as well as some new images. <br><br>
                Please, try to remember if you have seen the image before or not.
            </p>
        </div>`;
    
    lm_recognition_slide_2 = lm_base_layout() + lm_scale_labels() + lm_slider() + `
            <p class="instruction-paragraph-left">
                <strong>Use the slider to respond</strong><br><br>
                The <strong>right side</strong> of the slider indicates that the image has been shown before (i.e. it is <strong>old</strong>).<br><br>
                The <strong>left side</strong>  means that has not been shown (i.e. it is <strong>new</strong>).
            </p>
        </div>`;

    lm_recognition_slide_3 = lm_base_layout() + lm_scale_labels() + lm_slider() + `
            <p class="instruction-paragraph-left">
                <strong>Use the slider to respond to indicate your confidence</strong><br><br>
                You have three options: <strong>guess - probably - certain</strong>.<br><br>
                Please, move the slider to the position that indicates your confidence level.
            </p>
        </div>`;

    // instructions long term memory 
    var lm_instructions =         
        {
            type: jsPsychInstructions,
            key_forward: 'ArrowRight',
            show_clickable_nav: true,
            record_data: false,
            pages:[[
                `<div>
                    <p class="instruction-header">
                        <strong>Instructions</strong>
                    </p>
                    <p class="instruction-paragraph"> 
                        <strong>Great, you are almost done!</strong>
                        <br><br><br>
                        In the last task we will show you again some images. We want to know if you still remember the images from the first task.
                        <br><br>
                        For each image we will ask if you have seen it before (i.e. during the first/second block of the experiment)
                        <br><br><br><br>
                        The following instructions will explain the task in detail.
                    </p>
                </div>`
            ], 
            lm_recognition_slide_1, 
            lm_recognition_slide_2, 
            lm_recognition_slide_3, 
            ],
        };
    return lm_instructions
}

// STARTING LM
function startingLM() {
    // start lm
    var start_lm = {
        type: jsPsychInstructions,
        show_clickable_nav: false,
        record_data: false,
        key_forward: 'Enter',
        post_trial_gap: 200,
        min_viewing_time: 3000,
        pages: [
            [
            `<div>
                <p class="instruction-header"><strong>Starting the last task</strong></p>
                <p class="instruction-paragraph">
                    We will now start the last task of this experiment.<br><br>
                    There will be <strong>no practice</strong>, you will directly start the real task.<br><br>
                    This task will take approx. <strong>10 minutes</strong>.
                </p>
                <p class="continue-prompt">
                    To start, press <strong>Enter</strong> to start. 
                </p>
            </div>`
            ]
        ], 
    }
    return start_lm
}

// LM TASK
function createLM(timeline_variables, jsPsych) {
    var lm_timeline = [];  
    
    // preload
    lm_timeline.push(
    {
        type: jsPsychPreload,
        record_data: false,
        show_progress_bar: false,
        show_detailed_errors: true,
        message:
            `<div style="width:500px; height: 60vh;">
                <p style="font-family: 'Courier New', monospace; font-size: x-large; position: absolute; top: 20%; left: 50%;
                    transform: translateX(-50%); color:#4682B4; text-align: center;">
                    <strong>Which image do you remember from the previous task?</strong>
                </p>
                <div style="width:250px; height:75vh;">
                    <div class="cross">
                        <div class="cross-vertical" style="background-color: rgba(0, 0, 0, 0.05);"></div>
                        <div class="cross-horizontal" style="background-color: rgba(0, 0, 0, 0.05);"></div>
                    </div>
                </div>
                <div class="rectangle"></div>
            </div>`
            ,
        
        images: function() {
            var files = []
            files.push(jsPsych.evaluateTimelineVariable(`recognition_control_file`));
            files.push(jsPsych.evaluateTimelineVariable(`recognition_target_file`));
            return files;
        }
    })

    // inter trial delay
    lm_timeline.push(
    {
        type: jsPsychHtmlKeyboardResponse,
        choices: "NO_KEYS",
        trial_duration: experimentSettings.timing.lm_inter_trial_delay,
        record_data: false,
        stimulus: function(){
            var html =
            `<div style="width:500px; height: 60vh;">
                <p style="font-family: 'Courier New', monospace; font-size: x-large; position: absolute; top: 20%; left: 50%;
                    transform: translateX(-50%); color:#4682B4; text-align: center;">
                    <strong>Which image do you remember from the previous task?</strong>
                </p>
                <div style="width:250px; height:75vh;">
                    <div class="cross">
                        <div class="cross-vertical" style="background-color: rgba(0, 0, 0, 0.05);"></div>
                        <div class="cross-horizontal" style="background-color: rgba(0, 0, 0, 0.05);"></div>
                    </div>
                </div>
                <div class="rectangle"></div>
            </div>`
            return html;
        }
    })
    
    // recognition
    lm_timeline.push(
        {
            type: jsPsychHtmlButtonResponse,
            choices: ["left", "right"],
            button_layout: 'grid',
            button_html: (choice) => {
                var control_file = jsPsych.evaluateTimelineVariable(`recognition_control_file`)
                var target_file = jsPsych.evaluateTimelineVariable(`recognition_target_file`)
                var left_target = jsPsych.evaluateTimelineVariable(`left_target`) 

                if (left_target === 1) {
                    var left_image = target_file
                    var right_image = control_file
                } else {
                    var left_image = control_file
                    var right_image = target_file 
                }
            
                left_button = 
                    `<div style="cursor: pointer; width: 130px; height: 130px; 
                                position: absolute; top: 50%; left: calc( 50% - 80px); transform: translate(-50%, -50%);">
                    <img src="${left_image}" class="image-button" />
                    </div>`

                right_button = 
                    `<div style="cursor: pointer; width: 130px; height: 130px; 
                                position: absolute; top: 50%; left: calc( 50% + 80px); transform: translate(-50%, -50%);">
                    <img src="${right_image}" class="image-button"/>
                    </div>`
            
                if (choice == "left") {
                    return left_button;
                } else {
                    return right_button;
                }
            },

            stimulus: function() {
                var html =
                    `<div style="width:500px; height: 60vh;">
                    <p style="font-family: 'Courier New', monospace; font-size: x-large; position: absolute; top: 20%; left: 50%;
                        transform: translateX(-50%); color:#4682B4; text-align: center;">
                        <strong>Which image do you remember from the previous task?</strong>
                    </p>

                        <div style="width:250px; height:75vh;">
                            <div class="cross">
                                <div class="cross-vertical" style="background-color: rgba(0, 0, 0, 0.05);"></div>
                                <div class="cross-horizontal" style="background-color: rgba(0, 0, 0, 0.05);"></div>
                            </div>
                        </div>
                        <div class="rectangle"></div>
                    </div>`
                return html;
            },

            on_finish: function(data) {               
                // stimulus
                var control_file = jsPsych.evaluateTimelineVariable(`recognition_control_file`)
                var target_file = jsPsych.evaluateTimelineVariable(`recognition_target_file`)
                var left_target = jsPsych.evaluateTimelineVariable(`left_target`)

                data.stimulus = [target_file, control_file]
                if (left_target === 1) {
                    data.stimulus_left = target_file
                    data.stimulus_right = control_file
                } else {
                    data.stimulus_left = control_file
                    data.stimulus_right = target_file
                }

                // encoding time
                var long_encoding = jsPsych.evaluateTimelineVariable(`long_encoding`)
                if (long_encoding == 1) {
                    data.encoding_time = experimentSettings.timing.encoding_time_long
                } else {
                    data.encoding_time = experimentSettings.timing.encoding_time_short
                }

                data.trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                data.phase = 'recognition'
                data.image_id = jsPsych.evaluateTimelineVariable('lm_id')
                data.target = jsPsych.evaluateTimelineVariable('recognition_target_file')
                data.correct_response = jsPsych.evaluateTimelineVariable('correct_response')
                data.control = jsPsych.evaluateTimelineVariable('recognition_control_file')
                data.condition = jsPsych.evaluateTimelineVariable('condition')
                data.condition_name = jsPsych.evaluateTimelineVariable('condition_name')
                data.sample_position = jsPsych.evaluateTimelineVariable('sample_position')
                data.left_target = jsPsych.evaluateTimelineVariable('left_target') 
                data.trial_type = jsPsych.evaluateTimelineVariable('trial_type') 
                data.timestamp = new Date().toLocaleTimeString()
            }
        })

    return {timeline:lm_timeline, timeline_variables:timeline_variables};
}