// LM INSTRUCTIONS
function createLMInstructions() {
    // instructions long term memory 
    var lm_instruction_timeline = []
    const button_x = experimentSettings.spatial.button_x

    // initial break
    lm_instruction_timeline.push(
        {
            type: jsPsychHtmlKeyboardResponse, 
            trial_duration: 121000,
            stimulus: 
                `<div>
                    <p class="instruction-header"><strong>Last Break</strong></p>
                    <p class="instruction-paragraph"> 
                        <strong>Congratulations, you have successfully completed the first task!</strong><br><br>

                        You are now free to take a short break (max. 2 minutes) before 
                        beginning the next task.
                        This will be the last task of the experiment and it will be much shorter
                        than the previous one. <br><br>
                        
                        The following slides will have the detailed instructions.
                    </p>
                    <p class="continue-prompt">
                        To continue press <strong>Enter</strong>
                    </p>
                </div>`,
            choices: ['Enter'],
            on_load: function() {
                startTrialTimer(
                    radius=12,
                    delay=100,
                    duration=120000,
                    top=80,
                    color="#f0f0f0  "
                );
            },
            on_finish: function(data) {
                resetTrialTimer();

                if(data.rt === null) {
                    data.break_ending = "ended by timeout after 2 minutes";
                } 
                else {
                    data.break_ending = "ended by participant's action after " + data.rt + " ms";
                }
                data.stimulus = null;
                data.trial_type = "starting-lm-instructions";
                data.timestamp = new Date().toLocaleTimeString()
            }
        }
    )

    // instruction
    lm_instruction_timeline.push(        
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
                        Great, in our second task we want to know 
                        if you can still recognize the images from the previous task.
                        <br><br>
                        Just as before you can navigate back and forth through the instructions using the buttons below 
                        or using the arrow keys on your keyboard.
                    </p>
                </div>`
            ], 
            [
                `<div style="width:500px; height: 60vh;">
                <div class="rectangle"></div>
                
                <div>
                    <img style="position: absolute; top: 50%; left: calc( 50% + ${button_x}px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                    <img style="position: absolute; top: 50%; left: calc( 50% - ${button_x}px);" src="stimuli/instructions/dist4.jpg" class="image-object"/>
                </div>
                
                <p class="instruction-paragraph-left">
                    <strong>1/3 Have you seen this image previously?</strong>
                    <br><br>
                    In this task you will see a series of images pairs. 
                    <br><br>
                    <strong>One image was shown in the task before, the other image is new</strong>. 
                    <br><br>
                    Please, try to remember which image you have seen in the previous task and select it.
                    <br><br><br>
                    <strong>Note</strong>: Before selecting any image you have to move your mouse 
                    to enable the buttons.
                    </p>
                </div>`
            ], 
            [
                `<div style="width:500px; height: 60vh;">
                <div class="rectangle"></div>
                
                <div>
                    <img style="position: absolute; top: 50%; left: calc( 50% + ${button_x}px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                    <img style="position: absolute; top: 50%; left: calc( 50% - ${button_x}px);" src="stimuli/instructions/dist4.jpg" class="image-object"/>
                </div>
                
                <p class="instruction-paragraph-left">
                    <strong>2/3 What if you don't recognize any of the images?</strong><br><br>
                    It's okay, if you don't recognize either image.
                    This task was designed to be challenging!
                    <br><br>
                    When unsure, choose whichever one feels more familiar.
                    <br><br>
                    You will get feedback during this task. 
                </p>

                </div>`
            ], 
            [
                `<div style="width:500px; height: 60vh;">
                <div class="rectangle"></div>
                
                <div>
                    <img style="position: absolute; top: 50%; left: calc( 50% + ${button_x}px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                    <img style="position: absolute; top: 50%; left: calc( 50% - ${button_x}px);" src="stimuli/instructions/dist4.jpg" class="image-object"/>
                </div>
                
                <p class="instruction-paragraph-left">
                    <strong>3/3 What about breaks?</strong><br><br>
                    This is the final task of the experiment, which will take only <strong>~10 minutes</strong>. 
                    <br><br>
                    Therefore, there will be no breaks in this task. 
                </p>
                </div>`
            ], 
            ],
        }
    )
    return lm_instruction_timeline
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
function createLM(timeline_variables, jsPsych) {
    var lm_timeline = [];  
    const { lm_trials } = experimentSettings.memory_experiment;
    const total_trials = lm_trials;
    const button_x = experimentSettings.spatial.button_x
    
    // hide cursor
    lm_timeline.push(hide_cursor())

    // preload
    lm_timeline.push(
    {
        type: jsPsychPreload,
        record_data: true,
        show_progress_bar: false,
        show_detailed_errors: true,
        message: function() {
            html = `<div style="width:500px; height: 60vh;"></div>
            <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>`
            // progress bar
            var trial_id = jsPsych.evaluateTimelineVariable('trial_id')
            var progress_percent = (trial_id / total_trials) * 100
            var progress_bar =
                `<div class="progress-bar">
                    <div class="progress-bar-track">
                        <div class="progress-bar-fill" style="width: ${progress_percent}%;"></div>
                    </div>
                </div>`
            html += progress_bar
            return html

        },
        images: function() {
            var files = []
            files.push(jsPsych.evaluateTimelineVariable(`recognition_foil_file`));
            files.push(jsPsych.evaluateTimelineVariable(`recognition_target_file`));
            return files;
        }, 
        on_finish: function(data) { 
            var preload_duration = jsPsych.data.get().last(1).values()[0].time_elapsed - jsPsych.data.get().last(2).values()[0].time_elapsed
            if (data.subject_id == 999) {
                    console.log("Preloading duration: ", preload_duration)
            }
            data.stimulus = null;
            data.trial_type = "preload";
            data.preload_duration = preload_duration;
            data.trial_id = jsPsych.evaluateTimelineVariable('trial_id');
        }
    })

    // inter trial delay
    lm_timeline.push(
    {
        type: jsPsychHtmlKeyboardResponse,
        choices: "NO_KEYS",
        trial_duration: function() {
            var preload_time = jsPsych.data.get().last(1).values()[0].time_elapsed
            var recognition_time = jsPsych.data.get().last(2).values()[0].time_elapsed
            var preload_delay = (preload_time-recognition_time)
            var delay = Math.max(experimentSettings.timing.lm_inter_trial_delay-preload_delay,0)
            return delay
        }, 

        record_data: true,
        stimulus: function(){
            var html = 
            `<div style="width:250px; height:80vh;"></div>
            <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
            `
            // progress bar
            var trial_id = jsPsych.evaluateTimelineVariable('trial_id')
            var progress_percent = (trial_id / total_trials) * 100
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
            data.stimulus = null;
            data.trial_type = "inter-trial-delay";
            data.trial_id = jsPsych.evaluateTimelineVariable('trial_id')
        }
    })
    
    // Show cursor
    lm_timeline.push(show_cursor())
    
    // Mouse Movement Check (same as the recognition slide, but with disabled buttons)
    lm_timeline.push(
        {
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: null,

            stimulus: function() {
                var foil_file = jsPsych.evaluateTimelineVariable(`recognition_foil_file`)
                var target_file = jsPsych.evaluateTimelineVariable(`recognition_target_file`)
                var left_target = jsPsych.evaluateTimelineVariable(`left_target`) 

                if (left_target === 1) {
                    var left_image = target_file
                    var right_image = foil_file
                } else {
                    var left_image = foil_file
                    var right_image = target_file 
                }

                var html =
                    `<div style="width:500px; height: 60vh;">
                    <p style="font-family: 'Courier New', monospace; font-size: x-large; 
                        position: absolute; top: 20%; left: 50%; max-width: 400px;
                        transform: translateX(-50%); color:#4682B4; text-align: center;">
                        <strong>Which image do you remember from the previous task?</strong>
                    </p>
                    <div class="rectangle"></div>
                    </div>

                    <!-- Disabled buttons that look like the real ones -->
                    <div style="width: 126px; height: 126px; 
                                position: absolute; top: 50%; left: calc( 50% - ${button_x}px); transform: translate(-50%, -50%);">
                        <img src="${left_image}" class="image-button" style="pointer-events: none;"/>
                    </div>
                    <div style="width: 126px; height: 126px; 
                                position: absolute; top: 50%; left: calc( 50% + ${button_x}px); transform: translate(-50%, -50%);">
                        <img src="${right_image}" class="image-button" style="pointer-events: none;"/>
                    </div>`
                
                // progress bar
                var trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                var progress_percent = (trial_id / total_trials) * 100      

                var progress_bar = 
                    `<div class="progress-bar">
                        <div class="progress-bar-track">
                            <div class="progress-bar-fill" style="width: ${progress_percent}%;"></div>
                        </div>
                    </div>`
                html += progress_bar
                return html;
            },

            on_load: function() {
                const mouseHandler = createMouseHandler(jsPsych, 50, downsample_mouse_history);
                document.addEventListener('mousemove', mouseHandler);
            },

            on_finish: function(data) {
                data.trial_type = "mouse-movement-check"
                data.trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                data.timestamp = new Date().toLocaleTimeString()
            }
        }
    )

    // Recognition Slide
    lm_timeline.push(
        {
            type: jsPsychHtmlButtonResponse,
            choices: ["left", "right"],
            button_layout: 'grid',
            trial_duration: 31000,

            button_html: (choice) => {
                var foil_file = jsPsych.evaluateTimelineVariable(`recognition_foil_file`)
                var target_file = jsPsych.evaluateTimelineVariable(`recognition_target_file`)
                var left_target = jsPsych.evaluateTimelineVariable(`left_target`) 

                if (left_target === 1) {
                    var left_image = target_file
                    var right_image = foil_file
                } else {
                    var left_image = foil_file
                    var right_image = target_file 
                }
            
                left_button = 
                    `<div style="cursor: pointer; width: 126px; height: 126px; 
                                position: absolute; top: 50%; left: calc( 50% - ${button_x}px); transform: translate(-50%, -50%);">
                    <img src="${left_image}" class="image-button" />
                    </div>`

                right_button = 
                    `<div style="cursor: pointer; width: 126px; height: 126px; 
                                position: absolute; top: 50%; left: calc( 50% + ${button_x}px); transform: translate(-50%, -50%);">
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
                    <p style="font-family: 'Courier New', monospace; font-size: x-large; 
                        position: absolute; top: 20%; left: 50%; max-width: 400px;
                        transform: translateX(-50%); color:#4682B4; text-align: center;">
                        <strong>Which image do you remember from the previous task?</strong>
                    </p>
                    <div class="rectangle"></div>
                    </div>`
                
                // progress bar
                var trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                var progress_percent = (trial_id / total_trials) * 100      

                var progress_bar = 
                    `<div class="progress-bar">
                        <div class="progress-bar-track">
                            <div class="progress-bar-fill" style="width: ${progress_percent}%;"></div>
                        </div>
                    </div>`
                html += progress_bar
                
                return html;
            },

            on_load: function() {
                startTrialTimer(
                    radius=4,
                    delay=25000,
                    duration=5000, 
                    top=50, 
                    color="#f57c00"
                );
            },

            on_finish: function(data) {  
                // reset timer
                resetTrialTimer();             

                // stimulus
                var foil_file = jsPsych.evaluateTimelineVariable(`recognition_foil_file`)
                var target_file = jsPsych.evaluateTimelineVariable(`recognition_target_file`)
                var left_target = jsPsych.evaluateTimelineVariable(`left_target`)

                data.stimulus = [target_file, foil_file]
                if (left_target === 1) {
                    data.stimulus_left = target_file
                    data.stimulus_right = foil_file
                } else {
                    data.stimulus_left = foil_file
                    data.stimulus_right = target_file
                }

                data.phase = 'recognition'
                data.trial_type = jsPsych.evaluateTimelineVariable('trial_type') 
                data.trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                data.encoding_trial_id = jsPsych.evaluateTimelineVariable('encoding_trial_id')
                data.set_id = jsPsych.evaluateTimelineVariable('set_id')
                data.sample_position = jsPsych.evaluateTimelineVariable('sample_position')
                data.encoding_time = jsPsych.evaluateTimelineVariable('encoding_time')
                data.condition = jsPsych.evaluateTimelineVariable('condition')
                data.condition_name = jsPsych.evaluateTimelineVariable('condition_name')
                data.target_file = jsPsych.evaluateTimelineVariable('recognition_target_file')
                data.foil_file = jsPsych.evaluateTimelineVariable('recognition_foil_file')
                data.left_target = jsPsych.evaluateTimelineVariable('left_target') 
                data.correct_response = jsPsych.evaluateTimelineVariable('correct_response')
                data.timed_out = (data.response === null);
                data.timestamp = new Date().toLocaleTimeString()

                if (data.subject_id==999) {
                    console.log("Condition: ", data.condition_name)
                    console.log("Response: ", data.response)
                    console.log("Correct response: ", data.correct_response)
                }
            }
        })

    // Feedback 
    lm_timeline.push(
        {
            timeline: [{
                type: jsPsychHtmlKeyboardResponse,
                choices: "NO_KEYS",
                trial_duration: 1000,
                record_data: true,
                stimulus: function() {
                    var foil_file = jsPsych.evaluateTimelineVariable(`recognition_foil_file`)
                    var target_file = jsPsych.evaluateTimelineVariable(`recognition_target_file`)
                    var left_target = jsPsych.evaluateTimelineVariable(`left_target`)

                    // Determine images for left and right positions
                    if (left_target === 1) {
                        var left_image = target_file
                        var right_image = foil_file
                    } else {
                        var left_image = foil_file
                        var right_image = target_file
                    }

                    var html =
                        `<div style="width:500px; height: 60vh;">
                        <p style="font-family: 'Courier New', monospace; font-size: x-large; position: absolute; top: 20%; left: 50%;
                            transform: translateX(-50%); color:#4682B4; text-align: center;  max-width: 400px;">
                            <strong>Which image do you remember from the previous task?</strong>
                        </p>
                        `
                    
                    var last_trial = jsPsych.data.get().last(1).values()[0]
                    var last_response = last_trial.response

                    if (last_response === last_trial.correct_response) {
                        var clicked_left = (last_response === 0)
                        var correct_on_left = (left_target === 1)
                        
                        var left_class = (clicked_left && correct_on_left) ? 'image-object feedback-correct' : 'image-object'
                        var right_class = (!clicked_left && !correct_on_left) ? 'image-object feedback-correct' : 'image-object'
                        
                        html += 
                        `
                        <p style="font-family: 'Courier New', monospace; font-size: large; position: absolute; top: 65%; left: 50%;
                            transform: translateX(-50%); color:#2e7d32; text-align: center;">
                            <strong></strong>
                        </p>
                        <div class="rectangle"></div>
                            <img src="${left_image}" class="${left_class}" style="top: 50%; left: calc(50% - ${button_x}px);"/>
                            <img src="${right_image}" class="${right_class}" style="top: 50%; left: calc(50% + ${button_x}px);"/>
                        </div>
                        `
                    } else {
                        var clicked_left = (last_response === 0)

                        var left_class = clicked_left ? 'image-object feedback-incorrect' : 'image-object'
                        var right_class = !clicked_left ? 'image-object feedback-incorrect' : 'image-object'

                        html +=
                        `
                        <div class="rectangle"></div>
                            <img src="${left_image}" class="${left_class}" style="top: 50%; left: calc(50% - ${button_x}px);"/>
                            <img src="${right_image}" class="${right_class}" style="top: 50%; left: calc(50% + ${button_x}px);"/>
                        </div>
                        `
                    }

                    // progress bar
                    var trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                    var progress_percent = (trial_id / total_trials) * 100
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
                    data.stimulus = null;
                    data.trial_type = "lm-feedback";
                    data.trial_id = data.trial_id = jsPsych.evaluateTimelineVariable('trial_id');
                }
            }],
            conditional_function: function() {
                var last_trial = jsPsych.data.get().last(1).values()[0]
                return !last_trial.timed_out 
            }
        }
    )

    // Time-out
    lm_timeline.push(    
        {
            timeline: [{
                type: jsPsychHtmlKeyboardResponse, 
                stimulus: 
                    `<div>
                        <p class="instruction-header" style="color: #f57c00;">
                            <strong>⏸ Time Out</strong>
                        </p>
                        <p class="instruction-paragraph">
                            You did not respond in the last trial.<br><br>
                            <strong style="color: #e65100;">Please remember to respond within 30 seconds after the images appear.</strong><br><br>
                            You're doing well! Let's stay focused until the next break.
                        </p>
                        <p class="continue-prompt" style="color: #f57c00;">
                            Press <strong>Enter</strong> to continue
                        </p>
                    </div>`,
                choices: ['Enter'],
                on_finish: function(data) { 
                    data.stimulus = null;
                    data.trial_type = "timeout";
                    data.trial_id = jsPsych.evaluateTimelineVariable('trial_id');
                }
            }],
            conditional_function: function() {
                return jsPsych.data.get().last(1).values()[0].timed_out;
            }
        }
    ) 

    return {timeline:lm_timeline, timeline_variables:timeline_variables};
}