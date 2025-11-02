// INSTRUCTIONS
function createVisionInstructions() {
    var instructions = {
        type: jsPsychInstructions,
        key_forward: 'ArrowRight',
        key_backward: 'ArrowLeft',
        show_clickable_nav: false,
        record_data: false,
        pages: [
            [
            `<div>
                <p class="instruction-header"><strong>Instructions</strong></p>
                <p class="instruction-paragraph">
                    During this experiment, we will ask you to <strong>compare images to each other</strong>.
                    <br><br>
                    The following slide will explain in detail how the task works. 
                    After that we will start the experiment. The experiment will take ~15 minutes.
                </p>
                
                <p class="continue-prompt">
                    To continue press <strong>right arrow</strong>
                </p>
            </div>`
            ],
            [
            `<div>
                <p class="instruction-header"><strong>Instructions</strong></p>

                <div class="square2" 
                    style="left: left: calc( 50% - 320px); top: 50%;"
                </div>
                
                <div class="rectangle"></div>

                <div>
                    <img style="position: absolute; top: 50%; left: calc( 50% - 320px);"src="stimuli/instructions/sample1.jpg" class="image-object"/>
                    <img style="position: absolute; top: 50%; left: calc( 50% - 80px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                    <img style="position: absolute; top: 50%; left: calc( 50% + 80px);" src="stimuli/instructions/sample4.jpg" class="image-object"/>
                </div>

                <p class="instruction-paragraph-right">
                    <strong>Which image matches the image on the left better?</strong><br><br> 
                    During the experiment you will see <strong>3 images</strong>.<br><br>
                    Your task is to choose the image in the rectangle that 
                    <strong>matches the image on the left better</strong>.<br><br>
                    
                    You can pick the image by clicking on it.
                </p>
                <p class="continue-prompt">
                    To continue press <strong>right arrow</strong>
                </p>
            </div>`
            ], 
            [
            `<div>
                <p class="instruction-header"><strong>Instructions</strong></p>
                <p class="instruction-paragraph">
                    <strong>Important</strong>, there will be a ~1 second delay at the beginning of each 
                    trial during which you will not be able to select an imge.   
                    <br><br>
                    After this delay you can pick the better matching image.
                </p>
                
                <p class="continue-prompt">
                    To continue press <strong>right arrow</strong>
                </p>
            </div>`
            ]
        ]
    }
    return instructions
}

// STARTING SCREEN
function startingVisionTask () {
    // start wm experiment
    var start = {
        type: jsPsychInstructions,
        show_clickable_nav: false,
        key_forward: 'Enter',
        record_data: false,
        post_trial_gap: 200,
        min_viewing_time: 3000,
        pages: [
            [
            `<div>
                <p class="instruction-header">
                    <strong>Starting the experiment</strong>
                </p>
                <p class="instruction-paragraph">
                    Great, we will now start the experiment. 
                    The experiment will take ~15 minutes.<br><br>
                    Press <strong>enter</strong> to start.
                </p>
                <p class="continue-prompt">
                    To start the experiment <strong>ENTER</strong>
                </p>
            </div>`
            ]
        ],
    }
    return start
}

function createVisionTask(timeline_variables, jsPsych) {
    task_timeline = []
    
    // preload
    task_timeline.push(
    {
        type: jsPsychPreload,
        record_data: false,
        show_progress_bar: false,
        show_detailed_errors: true,
        message: 
            `<div style="width:300px; height: 65vh;">
                <p style="font-family: 'Courier New', monospace; font-size: x-large; position: absolute; left: 50%;
                    transform: translate(-50%, -50%); color:#4682B4; text-align: center;">
                    <strong>Which image matches the image on the left better?</strong>
                </p>
                <div class="rectangle"></div>
            </div>`,
        images: function() {
            var files = []
            files.push(jsPsych.evaluateTimelineVariable(`exp_file`));
            files.push(jsPsych.evaluateTimelineVariable(`context_file`));
            files.push(jsPsych.evaluateTimelineVariable(`sample_file`));
            return files;
        }
    })

    // inter trial delay
    task_timeline.push(
    {
        type: jsPsychHtmlKeyboardResponse,
        choices: "NO_KEYS",
        trial_duration: experimentSettings.vision_experiment.inter_trial_delay,
        record_data: false,
        stimulus: function(){
            var html = 
            `<div style="width:300px; height: 65vh;">
                <p style="font-family: 'Courier New', monospace; font-size: x-large; position: absolute; left: 50%;
                    transform: translate(-50%, -50%); color:#4682B4; text-align: center;">
                    <strong>Which image matches the image on the left better?</strong>
                </p>
                <div class="rectangle"></div>
            </div>`
            return html;
        }
    })

    // task
    task_timeline.push(
        {
            type: jsPsychHtmlButtonResponse,
            choices: ["left", "right"],
            button_layout: 'grid',
            enable_button_after: experimentSettings.vision_experiment.enable_button_after,
            button_html: (choice) => {
                var exp_file = jsPsych.evaluateTimelineVariable(`exp_file`)
                var context_file = jsPsych.evaluateTimelineVariable(`context_file`)
                var exp_right = jsPsych.evaluateTimelineVariable(`exp_right`) 
                
                if (exp_right === 1) {
                    var left_image = context_file
                    var right_image = exp_file
                } else {
                    var left_image = exp_file
                    var right_image = context_file
                }
            
                left_button = 
                    `<button class="image-button" style="background: none; border: none; padding: 0; cursor: pointer; width: 130px; 
                        height: 130px; position: absolute; top: 50%; left: calc(50% - 80px);">
                    <img src="${left_image}" style="width: 100%; height: 100%; border-radius: 10px;" />
                    </button>`

                // `<div style="cursor: pointer; width: 130px; height: 130px; 
                //                 position: absolute; top: 50%; left: calc(50% - 80px); transform: translate(-50%, -50%);">
                //     <img src="${left_image}" class="image-button" />
                //     </div>`
                
                right_button = 
                    `<button class="image-button" style="background: none; border: none; padding: 0; cursor: pointer; width: 130px; height: 130px; 
                        position: absolute; top: 50%; left: calc(50% + 80px);">
                    <img src="${right_image}" style="width: 100%; height: 100%; border-radius: 10px;" />
                    </button>`
                
                // `<div style="cursor: pointer; width: 130px; height: 130px; 
                //             position: absolute; top: 50%; left: calc( 50% + 80px); transform: translate(-50%, -50%);">
                // <img src="${right_image}" class="image-button" />
                // </div>`
            
                if (choice == "left") {
                    return left_button;
                } else {
                    return right_button;
                }
            },

            stimulus: function() {
                var sample_file = jsPsych.evaluateTimelineVariable(`sample_file`)

                var html = 
                    `<div style="width:300px; height: 65vh;">
                        <p style="font-family: 'Courier New', monospace; font-size: x-large; position: absolute; left: 50%;
                            transform: translate(-50%, -50%); color:#4682B4; text-align: center;">
                            <strong>Which image matches the image on the left better?</strong>
                        </p>

                        <div> 
                            <div class="square large" 
                                style="top: calc(50%); left: calc(50% - 320px);"
                            </div>
                        </div>

                        <div> 
                            <img src="${sample_file}" class="image-object large" 
                            style="top: calc(50%); left: calc(50% - 320px);"/>
                        </div>

                        <div class="rectangle"></div>

                    </div>`
                return html;
            },

            on_finish: function(data) { 
                var files = [
                    jsPsych.evaluateTimelineVariable(`sample_file`),
                    jsPsych.evaluateTimelineVariable(`exp_file`), 
                    jsPsych.evaluateTimelineVariable(`context_file`)
                ]

                data.stimulus = files
                data.trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                data.set_id = jsPsych.evaluateTimelineVariable('set_id')
                data.sample_file = jsPsych.evaluateTimelineVariable(`sample_file`)
                data.exp_stimulus = jsPsych.evaluateTimelineVariable('exp_file')
                data.correct_response = jsPsych.evaluateTimelineVariable('correct_response')
                data.context_file = jsPsych.evaluateTimelineVariable('context_file')
                data.exp_right = jsPsych.evaluateTimelineVariable('exp_right') 
                data.condition_code = jsPsych.evaluateTimelineVariable('condition_code') 
                data.timestamp = new Date().toLocaleTimeString()
            }
        }
    )
    return {timeline:task_timeline, timeline_variables:timeline_variables};
}

function endingVisionTask() {
    var end = {
        type: jsPsychHtmlKeyboardResponse, 
        stimulus: 
            `<div>
                <p class="instruction-paragraph"> 
                    <strong>Great, you have successfully completed the task!</strong><br><br>
                </p>
                <p class="continue-prompt">
                    To continue press <strong>right arrow</strong>
                </p>
            </div>`,
        choices: ['ArrowRight'],
        trial_duration: 120000
    }
    return end
}

