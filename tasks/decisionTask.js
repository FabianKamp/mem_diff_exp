// INSTRUCTIONS
function decisionInstructions() {
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
                    During this experiment, we will ask you to decide which image match better to each other.
                    <br><br>
                    The following instructions will explain in detail how the task works.
                    <br><br><br>
                    <strong>The instructions are self-paced</strong>. 
                    You can navigate back and forth through the instructions using the arrow keys on your keyboard.
                </p>
                
                <p class="continue-prompt">
                    To continue press <strong>right arrow</strong>
                </p>
            </div>`
            ],
            [
            `<div class="square2" 
                style="left: left: calc( 50% - 320px); top: 50%;"
            </div>

            <div>
                <img style="position: absolute; top: 50%; left: calc( 50% - 320px);"src="stimuli/instructions/sample1.jpg" class="image-object"/>
                <img style="position: absolute; top: 50%; left: calc( 50% - 80);" src="stimuli/instructions/sample4.jpg" class="image-object"/>
                <img style="position: absolute; top: 50%; left: calc( 50% + 80px);" src="stimuli/instructions/sample4.jpg" class="image-object"/>
            </div>

            <p class="instruction-paragraph-left">
                <strong>3. Which image matches the left image better?</strong><br><br> 
                You will see <strong>3 images</strong>, i.e. one on the left and two on the right.<br><br>
                Your task is to <strong>choose the image that matches the left image better</strong>.
                <br><br>
                You can choose the image by clicking on it.
            </p>
            <p class="continue-prompt">
                To continue press <strong>right arrow</strong>
            </p>`
            ]
        ]
    }
    return instructions
}

// STARTING SCREEN
function startingDecisionTask () {
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
                    Amazing! We will now start the experiment.
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

function createDecisionTask(timeline_variables, jsPsych) {
    task_timeline = []
    // inter trial delay
    task_timeline.push(
    {
        type: jsPsychHtmlKeyboardResponse,
        choices: "NO_KEYS",
        trial_duration: experimentSettings.timing.inter_trial_delay,
        record_data: false,
        stimulus: function(){
            var html = 
            `<div style="width:250px; height:75vh;">
                <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
            </div>`
            return html;
        }
    })

    task_timeline.push(
        {
            type: jsPsychHtmlButtonResponse,
            choices: ["left", "right"],
            button_layout: 'grid',
            button_html: (choice) => {
                var trial_id = jsPsych.evaluateTimelineVariable(`trial_id`)
                var exp_file = jsPsych.evaluateTimelineVariable(`exp_file`)
                var context_file = jsPsych.evaluateTimelineVariable(`context_file`)
                var exp_left = jsPsych.evaluateTimelineVariable(`exp_left`) 
                
                if (exp_left === 1) {
                    var left_image = exp_file
                    var right_image = context_file
                } else {
                    var left_image = context_file
                    var right_image = exp_file 
                }
            
                left_button = 
                    `<div style="cursor: pointer; width: 130px; height: 130px; 
                                position: absolute; top: 50%; left: calc(50% - 80px); transform: translate(-50%, -50%);">
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
                var sample_file = jsPsych.evaluateTimelineVariable(`sample_file`)
                var html = 
                    `<div style="width:300px; height: 65vh;">
                        <p style="font-family: 'Courier New', monospace; font-size: x-large; position: absolute; left: 50%;
                            transform: translate(-50%, -50%); color:#4682B4; text-align: center;">
                            <strong>Which image matches the image on the left better?</strong>
                        </p>

                        <div> 
                            <div class="square" 
                                style="top: calc(50%); left: calc(50% - 320px);"
                            </div>
                        </div>

                        <div> 
                            <img src="${sample_file}" class="image-object" 
                            style="top: calc(50%); left: calc(50% - 320px);"/>
                        </div>

                        <div class="rectangle"></div>

                    </div>`
                return html;
            },

            on_finish: function(data) { 
                var files = [
                    jsPsych.evaluateTimelineVariable(`exp_file`), 
                    jsPsych.evaluateTimelineVariable(`context_file`)
                ]
                console.log(jsPsych.evaluateTimelineVariable('correct_response'))
                data.stimulus = files
                data.trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                data.set_id = jsPsych.evaluateTimelineVariable('set_id')
                data.exp_stimulus = jsPsych.evaluateTimelineVariable('exp_file')
                data.correct_response = jsPsych.evaluateTimelineVariable('correct_response')
                data.context_file = jsPsych.evaluateTimelineVariable('context_file')
                data.exp_left = jsPsych.evaluateTimelineVariable('exp_left') 
                data.condition_code = jsPsych.evaluateTimelineVariable('condition_code') 
                data.timestamp = new Date().toLocaleTimeString()
            }
        }
    )
    return {timeline:task_timeline, timeline_variables:timeline_variables};
}

// slide after WM
function endingDecisionTask() {
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

