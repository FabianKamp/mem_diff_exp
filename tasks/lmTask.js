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
                        <strong>Follow-up task</strong>
                    </p>
                    <p class="instruction-paragraph"> 
                        <strong>Great, you are almost done!</strong>
                        <br><br>
                        In our second task we want to know 
                        if you can still recognize the images from the first task.
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
                
                <p class="instruction-paragraph-left">
                    <strong>1/3 Have you seen this image previously?</strong>
                    <br><br>
                    In this task you will see a series of images pairs. 
                    <br><br>
                    <strong>One image was shown in the task before, the other image is new</strong>. 
                    <br><br>
                    Please, try to remember which image you have seen in the previous task and select it.
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
                    <strong>2/3 What if you don't recognize any of the images?</strong><br><br>
                    It's okay, if you don't recognize either image.
                    This task was designed to be challenging!
                    <br><br>
                    When unsure, choose whichever one feels more familiar.
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
                    <strong>3/3 What about breaks?</strong><br><br>
                    This is the final task of the experiment, which will take only <strong>~10 minutes</strong>. 
                    <br><br>
                    Therefore, there will be no breaks in this task. 
                    <br><br>
                    But you can track your progress on the progress bar at the bottom of the screen.
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
function createLM(timeline_variables, jsPsych) {
    var lm_timeline = [];  
    const { lm_trials } = experimentSettings.memory_experiment;
    const total_trials = lm_trials;
    
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
            data.stimulus = null;
            data.trial_type = "preload";
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
                                position: absolute; top: 50%; left: calc( 50% - 75px); transform: translate(-50%, -50%);">
                    <img src="${left_image}" class="image-button" />
                    </div>`

                right_button = 
                    `<div style="cursor: pointer; width: 126px; height: 126px; 
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

            on_finish: function(data) {  
                // reset timer
                resetTimer();             

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
                data.long_encoding = jsPsych.evaluateTimelineVariable('long_encoding')
                data.encoding_time = jsPsych.evaluateTimelineVariable('encoding_time')
                data.condition = jsPsych.evaluateTimelineVariable('condition')
                data.condition_name = jsPsych.evaluateTimelineVariable('condition_name')
                data.target_file = jsPsych.evaluateTimelineVariable('recognition_target_file')
                data.foil_file = jsPsych.evaluateTimelineVariable('recognition_foil_file')
                data.left_target = jsPsych.evaluateTimelineVariable('left_target') 
                data.correct_response = jsPsych.evaluateTimelineVariable('correct_response')
                data.timed_out = (data.response === null);
                data.timestamp = new Date().toLocaleTimeString()
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
                        <img src="${left_image}" class="${left_class}" style="top: 50%; left: calc(50% - 75px);"/>
                        <img src="${right_image}" class="${right_class}" style="top: 50%; left: calc(50% + 75px);"/>
                        </div>
                        `
                    } else {
                        var clicked_left = (last_response === 0)

                        var left_class = clicked_left ? 'image-object feedback-incorrect' : 'image-object'
                        var right_class = !clicked_left ? 'image-object feedback-incorrect' : 'image-object'

                        html +=
                        `
                        <div class="rectangle"></div>
                        <img src="${left_image}" class="${left_class}" style="top: 50%; left: calc(50% - 75px);"/>
                        <img src="${right_image}" class="${right_class}" style="top: 50%; left: calc(50% + 75px);"/>
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