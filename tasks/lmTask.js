// LM INSTRUCTIONS
function createLMInstructions() {
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
                        <br><br><br><br>
                        The following instructions will explain the task in detail.
                    </p>
                </div>`
            ], 
            [
                `<div style="width:500px; height: 60vh;">
                <div class="rectangle"></div>
                
                <div>
                    <img style="position: absolute; top: 50%; left: calc( 50% + 80px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                    <img style="position: absolute; top: 50%; left: calc( 50% - 80px);" src="stimuli/instructions/dist4.jpg" class="image-object"/>
                </div>
                
                <p class="instruction-paragraph-left">
                    <strong>1. Have you seen this image?</strong><br><br>
                    Now we would like to know if you can still remember the images from the task before. <br><br>
                    You will see 2 images. <strong>One image was shown in the task before, the other image is new</strong>. <br><br>
                    Please, try to remember which image you have seen in the previous task.
                    </p>
                </div>`
            ], 
            [
                `<div style="width:500px; height: 60vh;">
                <div class="rectangle"></div>
                
                <div>
                    <img style="position: absolute; top: 50%; left: calc( 50% + 80px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                    <img style="position: absolute; top: 50%; left: calc( 50% - 80px);" src="stimuli/instructions/dist4.jpg" class="image-object"/>
                </div>
                
                <p class="instruction-paragraph-left">
                    <strong>2. How to select an image</strong><br><br>
                    You can choose the image that you remember from the previous task by clicking on it.
                    <br><br>
                    If you don't recognize any of images, that's okay — just make your best guess.
                </p>
                </div>`
            ], 
            [
                `<div style="width:500px; height: 60vh;">
                <div class="rectangle"></div>
                
                <div>
                    <img style="position: absolute; top: 50%; left: calc( 50% + 80px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                    <img style="position: absolute; top: 50%; left: calc( 50% - 80px);" src="stimuli/instructions/dist4.jpg" class="image-object"/>
                </div>
                
                <p class="instruction-paragraph-left">
                    <strong>3. Timing</strong><br><br>
                    As before, you will have <strong>30 seconds</strong> to select an image on each trial. 
                    <br><br>
                    Please try to respond within this time window.
                    <br><br>
                    </p>
                </div>`
            ], 
            [
                `<div style="width:500px; height: 60vh;">
                <div class="rectangle"></div>
                
                <div>
                    <img style="position: absolute; top: 50%; left: calc( 50% + 80px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                    <img style="position: absolute; top: 50%; left: calc( 50% - 80px);" src="stimuli/instructions/dist4.jpg" class="image-object"/>
                </div>

                <div class="progress-bar" style="bottom: 140px;">
                    <div class="progress-bar-track">
                        <div class="progress-bar-fill" style="width: 10%;"></div>
                    </div>
                </div>
                
                <p class="instruction-paragraph-left">
                    <strong>4. What about breaks?</strong><br><br>
                    This is the final task of the experiment, which will take only 5-10 minutes. 
                    <br><br>
                    Therefore, there will be no breaks in this task. 
                    <br><br>
                    But you can track your progress on the progress bar at the bottom of the screen
                </p>
                </div>`
            ], 
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
                    This task will take <strong>5-10 minutes</strong>.
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
var lm_trial_counter = 0;
function createLM(timeline_variables, jsPsych) {
    var lm_timeline = [];  
    
    // preload
    lm_timeline.push(
    {
        type: jsPsychPreload,
        record_data: false,
        show_progress_bar: false,
        show_detailed_errors: true,
        message: function() {
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
            
            // progress bar
            const { lm_trials } = experimentSettings.memory_experiment;                
            var progress_percent = (lm_trial_counter / lm_trials) * 100
            var progress_bar = 
                `<div class="progress-bar">
                    <div class="progress-bar-track">
                        <div class="progress-bar-fill" style="width: ${progress_percent}%;"></div>
                    </div>
                </div>`
            html += progress_bar

        },
        
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
            `<div style="width:250px; height:80vh;">
                <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
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
            trial_duration: 31000,
            
            on_load: function() {
                startTimer(
                    radius=4,
                    delay=25000,
                    duration=5000, 
                    top=50, 
                    color="#f57c00"
                );
            },

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
                                position: absolute; top: 50%; left: calc( 50% - 75px); transform: translate(-50%, -50%);">
                    <img src="${left_image}" class="image-button" />
                    </div>`

                right_button = 
                    `<div style="cursor: pointer; width: 130px; height: 130px; 
                                position: absolute; top: 50%; left: calc( 50% + 75px); transform: translate(-50%, -50%);">
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
                    <div class="rectangle"></div>
                    </div>`
                
                // progress bar
                const { lm_trials } = experimentSettings.memory_experiment;                
                var progress_percent = (lm_trial_counter / lm_trials) * 100
                var progress_bar = 
                    `<div class="progress-bar">
                        <div class="progress-bar-track">
                            <div class="progress-bar-fill" style="width: ${progress_percent}%;"></div>
                        </div>
                    </div>`
                html += progress_bar
                
                return html;
            },

            on_finish: function(data) {  
                // reset time and update the counter
                resetTimer();             
                lm_trial_counter++

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
                data.timed_out = (data.response === null);
                data.timestamp = new Date().toLocaleTimeString()
            }
        })
    
    // Time-out
    lm_timeline.push(    
        {
            timeline: [{
                type: jsPsychHtmlKeyboardResponse, 
                stimulus: 
                    `<div class="timeout-warning">
                        <p class="instruction-header warning-header">
                            <strong>⏸ Time Out</strong>
                        </p>
                        <p class="instruction-paragraph warning-message"> 
                            You did not respond in the last trial.<br><br>
                            <strong>Please remember to respond within 30 seconds after the images appear.</strong><br><br>
                            You're doing well! Let's stay focused until the last task is over.
                        </p>
                        <p class="continue-prompt">
                            Press <strong>Enter</strong> to continue
                        </p>
                    </div>`,
                choices: ['Enter'],
            }],
            conditional_function: function() {
                return jsPsych.data.get().last(1).values()[0].timed_out;
            }
        }
    ) 

    return {timeline:lm_timeline, timeline_variables:timeline_variables};
}