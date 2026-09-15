function createRetroCueInstructions() {   
    var instruction_timeline = []
     // preload
    instruction_timeline.push(
        {
            type: jsPsychPreload,
            record_data: true,
            show_progress_bar: false,
            message:  
                `<div>
                    <p class="instruction-header">
                        <strong>Welcome to our experiment!</strong>
                    </p>
                    <p class="instruction-paragraph">
                        We are preparing the instructions.. 
                        <br><br>
                        Please wait while we load the necessary resources. 
                        This will only take a few of seconds.
                        <br>
                    </p>
                </div>`
            ,
            images: [
                "stimuli/instructions/dist1.jpg", 
                "stimuli/instructions/dist2.jpg", 
                "stimuli/instructions/dist3.jpg", 
                "stimuli/instructions/sample1.jpg", 
                "stimuli/instructions/sample2.jpg",
                "stimuli/instructions/sample4.jpg"
            ],
            on_finish: function(data) { 
                data.stimulus = null;
                data.trial_type = "preload";
            }
        }
    ) 

    // instruction angles
    const button_x = experimentSettings.spatial.button_x
    const button_y = experimentSettings.spatial.button_y
    var load = experimentSettings.memory_experiment.load
    var instruction_angles = generate_instruction_angles(load)
    var sample_pos = convert2cartesian(instruction_angles[1])
    var instruction_files = ["dist1.jpg", "sample1.jpg", "dist2.jpg"] // "dist3.jpg", "dist4.jpg", "dist5.jpg", "dist6.jpg"
    if (experimentSettings.memory_experiment.load == 4){
        instruction_files.push("dist3.jpg")
    }

    var encoding_positions = [] 
    for (let i = 0; i < instruction_angles.length; i++) {
        encoding_positions.push(convert2cartesian(instruction_angles[i]))
    }
    
    var image_containers = ``
    for (let i = 0; i < load; i++) {
        image_containers += `
            <div class="image-container"> 
                    <img src="stimuli/instructions/${instruction_files[i]}" class="image-object" 
                    style="left: calc(50% - ${encoding_positions[i].x}px); top: calc(50% + ${encoding_positions[i].y}px);"/>
            </div>
            `
    }

    var square_containers = `
        <div class="square plain" style="left: calc(50% - ${encoding_positions[0].x}px); top: calc(50% + ${encoding_positions[0].y}px);"></div>
        <div class="square" style="left: calc(50% - ${sample_pos.x}px); top: calc(50% + ${sample_pos.y}px);">
            ?
        </div>
        <div class="square plain" style="left: calc(50% - ${encoding_positions[2].x}px); top: calc(50% + ${encoding_positions[2].y}px);"></div>
        `
    if (load == 4){
        square_containers += `<div class="square plain" style="left: calc(50% - ${encoding_positions[3].x}px); top: calc(50% + ${encoding_positions[3].y}px);"></div>`
    }

    // Cue container for instruction page (showing X at sample position)
    var cue_container = `
        <div class="square" style="left: calc(50% - ${sample_pos.x}px); top: calc(50% + ${sample_pos.y}px);">
            X
        </div>
        `
    

    instruction_timeline.push({
        type: jsPsychInstructions,
        key_forward: 'ArrowRight',
        key_backward: 'ArrowLeft',
        show_clickable_nav: true,
        record_data: true,
        pages: [
            [
            `<div>
                <p class="instruction-header"><strong>Instructions</strong></p>
                <p class="instruction-paragraph">
                    <strong>The instructions are self-paced</strong>. 
                    You can navigate back and forth through the instructions using the buttons below 
                    or using the arrow keys on your keyboard.
                    <br>
                </p>
            </div>`
            ],
            // 1/6
            [
            `<div>
                <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
                <p class="instruction-paragraph-left">
                    <strong>1/6 Memorize</strong><br><br>
                    In each trial we will ask you to memorize <strong>${load} images</strong>.
                    <br><br>
                    The images will be shown for about <strong>1 second</strong>.
                    <br><br>
                    <strong>Important:</strong> Keep your eyes focused on the cross in the center of the screen while memorizing the images.
                    <br><br>
                    All images shown in this experiment are computer-generated, not real photographs.
                </p>
            ` + image_containers + `</div>`
            ],
            // 2/6
            [
            `<div>
                <div class="cross">
                    <div class="cross-vertical"></div>
                    <div class="cross-horizontal"></div>
                </div>
                ` + cue_container + `
                <p class="instruction-paragraph-left">
                    <strong>2/6 Cue</strong><br><br>
                    After the images disappear, you will see a short delay followed by a <strong>cue</strong>.
                    <br><br>
                    The cue is a square with an <strong>X</strong> that appears briefly at one of the image positions.
                    <br><br>
                    The cue indicates which image you will be tested on. <strong>However, the cue is not always accurate</strong> — sometimes it points to a different position than the one you'll be tested on.
                    <br><br>
                    Try to focus on the cued position, but keep all images in mind.
                </p>
            </div>`
            ],
            // 3/6
            [
            `
            <div>
                <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% + ${button_x}px);" src="stimuli/instructions/sample3.jpg" class="image-object"/>
                <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% - ${button_x}px);" src="stimuli/instructions/dist4.jpg" class="image-object"/>
            </div>

            <div
                style="position: absolute; top: calc(50% + ${button_y}px + 80px); left: calc(50% - 24px);
                transform: translateX(-50%); font-size: 30px;">&larr;
            </div>
            <div
                style="position: absolute; top: calc(50% + ${button_y}px + 80px); left: calc(50% + 24px);
                transform: translateX(-50%); font-size: 30px;">&rarr;
            </div>

            <div class="cross">
                <div class="cross-vertical"></div>
                <div class="cross-horizontal"></div>
            </div>

            <div class="rectangle"
                style="top: calc(50% + ${button_y}px);">
            </div>

            <p class="instruction-paragraph-left">
                <strong>3/6 Which image matches the original image better?</strong>
                <br><br> 
                After the delay you will see <strong>2 new images</strong> on the screen.
                You haven't seen either of the images before. 
                <br><br>
                Your task: <strong>Select the image that matches the original image better</strong>.
                <br><br>
                The <strong>? mark</strong> indicates the location of the original image.
                <br><br>
                Press the left arrow key ⬅️ to select the left image, or the right arrow key ➡️ to select the right image.
                <br>
            </p>
            ` + square_containers
            ],
            // 4/6
            [
            `
            <div>
                <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% + ${button_x}px);" src="stimuli/instructions/sample3.jpg" class="image-object"/>
                <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% - ${button_x}px);" src="stimuli/instructions/dist4.jpg" class="image-object"/>
            </div>
            <div
                style="position: absolute; top: calc(50% + ${button_y}px + 80px); left: calc(50% - 24px); transform: translateX(-50%); font-size: 30px;">&larr;
            </div>
            <div
                style="position: absolute; top: calc(50% + ${button_y}px + 80px); left: calc(50% + 24px); transform: translateX(-50%); font-size: 30px;">&rarr;
            </div>

            <div class="cross">
                <div class="cross-vertical"></div>
                <div class="cross-horizontal"></div>
            </div>

            <div class="rectangle"
                style="top: calc(50% + ${button_y}px);">
            </div>

            <p class="instruction-paragraph-left">
                <strong>4/6 What if you're uncertain?</strong>
                <br><br>
                The images can match the original image in various ways. 
                <br><br>
                If you're uncertain which image matches the original better, 
                that's okay - just make your best guess.
                <br><br>
                You'll have <strong>10 seconds to respond</strong>. If you don't respond in time, the trial will be timed out.
                We will abort the experiment if too many trails are timed out.
                <br>
            </p>
            ` + square_containers
            ],
            // 5/6
            [
            `
            <div>
                <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% + ${button_x}px);" src="stimuli/instructions/sample3.jpg" class="image-object"/>
                <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% - ${button_x}px);" src="stimuli/instructions/dist4.jpg" class="image-object"/>
            </div>
            <div
                style="position: absolute; top: calc(50% + ${button_y}px + 80px); left: calc(50% - 24px); transform: translateX(-50%); font-size: 30px;">&larr;
            </div>
            <div
                style="position: absolute; top: calc(50% + ${button_y}px + 80px); left: calc(50% + 24px); transform: translateX(-50%); font-size: 30px;">&rarr;
            </div>

            <div class="cross">
                <div class="cross-vertical"></div>
                <div class="cross-horizontal"></div>
            </div>

            <div class="rectangle"
                style="top: calc(50% + ${button_y}px);">
            </div>

            <p class="instruction-paragraph-left">
                <strong>5/6 What about breaks?</strong>
                <br><br>
                The task has 3 blocks, each taking 10-12 minutes.
                <br><br>
                You will have <strong>2 breaks</strong> (up to two minutes each) between blocks.
                <br><br>
                Your progress will be shown in a bar at the bottom of the screen.
                <br>
            </p>
            ` + square_containers
            ],
            // 6/6
            [
            `<div>
                <div class="cross">
                    <div class="cross-vertical"></div>
                    <div class="cross-horizontal"></div>
                </div>
                <p class="instruction-paragraph">
                    <strong>6/6 Summary</strong><br><br>
                    Each trial follows this sequence:
                    <br><br>
                    1. <strong>Memorize</strong> — ${load} images appear briefly<br>
                    2. <strong>Cue</strong> — An X marks a position (not always accurate)<br>
                    3. <strong>Test</strong> — Choose which image matches the original better
                    <br><br>
                    You will start with a few practice trials.
                    <br><br>
                    <strong>Good luck!</strong>
                </p>
            </div>`
            ],
        ], 
        on_finish: function(data) { 
            data.stimulus = null;
            data.trial_type = "instructions";
        }
    })
    return instruction_timeline
}

// WM TASK
function createRetroCueWM(timeline_variables, jsPsych) {
    // preload block 
    const preloadBlock = jsPsych.data.dataProperties.preloadBlock
    
    // set up progress bar
    const { wm_trials, ncatch, practice_trials, wm_block1_trials, wm_block2_trials} = experimentSettings.memory_experiment;
    const total_trials = wm_trials + ncatch + practice_trials;
    const first_break = 100/total_trials * (practice_trials + wm_block1_trials + ncatch*wm_block1_trials/total_trials);
    const second_break = 100/total_trials * (practice_trials + wm_block1_trials + wm_block2_trials + 
        ncatch*(wm_block1_trials+wm_block2_trials)/total_trials);
    const button_x = experimentSettings.spatial.button_x
    const button_y = experimentSettings.spatial.button_y

    // Helper function to generate progress bar HTML
    const getProgressBarHTML = () => {
        var running_trial_id = jsPsych.evaluateTimelineVariable('trial_id');
        var progress_percent = (running_trial_id / total_trials) * 100;
        return `<div class="progress-bar">
                    <div class="progress-bar-track">
                        <div class="progress-bar-fill" style="width: ${progress_percent}%;"></div>
                        <div class="progress-marker" style="left: ${first_break}%"></div>
                        <div class="progress-marker" style="left: ${second_break}%"></div>
                    </div>
                </div>`;
    };

    // timeline
    var wm_timeline = []

    // hide cursor
    wm_timeline.push(hide_cursor())
    
    // preload trialwise
    wm_timeline.push({timeline: [
        {
            type: jsPsychPreload,
            record_data: true,
            show_progress_bar: false,
            message:  function() {               
                html = 
                `<div style="width:250px; height:80vh;">
                    <div class="cross">
                    <div class="cross-vertical" style="opacity: 0.4;"></div>
                    <div class="cross-horizontal" style="opacity: 0.4;"></div>
                    </div>
                </div>`
                html += getProgressBarHTML()
                return html 
            },
            show_detailed_errors: true,
            images: function() {
                var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding')
                var files = [];
                for (let i = 0; i < n_encoding; i++) {
                    var file = jsPsych.evaluateTimelineVariable(`encoding_file_${i+1}`);
                    files.push(file)
                }
                files.push(jsPsych.evaluateTimelineVariable('recognition_target_file'))
                files.push(jsPsych.evaluateTimelineVariable('recognition_foil_file'))
                return files;
            },
            on_finish: function(data) { 
                var preload_duration = jsPsych.data.get().last(1).values()[0].time_elapsed - jsPsych.data.get().last(2).values()[0].time_elapsed
                if (data.subject_id == 999) {
                    console.log("Trial preloading duration: ", preload_duration)
                }
                data.stimulus = null;
                data.trial_type = "preload";
                data.preload_duration = preload_duration;
                data.wm_block_id = jsPsych.evaluateTimelineVariable('wm_block_id');
                data.running_trial_id = jsPsych.evaluateTimelineVariable('trial_id');
            }
        }],
        conditional_function: function() {
            return !jsPsych.data.dataProperties.preloadBlock
        }
    })
    
    // inter trial delay
    wm_timeline.push({timeline: [
        {
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: function() {
                if (preloadBlock) {
                    var preload_delay = 0;
                } else { 
                    var preload_time = jsPsych.data.get().last(1).values()[0].time_elapsed
                    var recognition_time = jsPsych.data.get().last(2).values()[0].time_elapsed
                    var preload_delay = (preload_time-recognition_time) 
                }
                var delay = Math.max(experimentSettings.timing.wm_inter_trial_delay-preload_delay-500,0)
                
                if (jsPsych.data.subject_id == 999) {
                        console.log("Inter trial delay: ", delay)
                        console.log("Recognition time previous: ", recognition_time)
                    }
                return delay  
            },

            record_data: true,
            stimulus: function(){
                var html =
                `<div style="width:250px; height:80vh;">
                    <div class="cross">
                        <div class="cross-vertical" style="opacity: 0.4;"></div>
                        <div class="cross-horizontal" style="opacity: 0.4;"></div>
                    </div>
                </div>`
                html += getProgressBarHTML();
                return html;
            }, 
            on_finish: function(data) { 
                data.stimulus = null;
                data.trial_type = "inter-trial-delay";
                data.wm_block_id = jsPsych.evaluateTimelineVariable('wm_block_id');
                data.running_trial_id = jsPsych.evaluateTimelineVariable('trial_id');
            }
        },

        // cross switches color 500ms before next trial
        {
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: 500,
            record_data: false,
            stimulus: function(){
                var html =
                `<div style="width:250px; height:80vh;">
                    <div class="cross">
                        <div class="cross-vertical"></div>
                        <div class="cross-horizontal"></div>
                    </div>
                </div>`
                html += getProgressBarHTML();
                return html;
            },
        }, 
    ]})

    // Encoding slide
    wm_timeline.push(
        {
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: function() {
                var encoding_time = jsPsych.evaluateTimelineVariable(`encoding_time`)
                return encoding_time
            },
            stimulus: function() {
                var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding')
                html = `<div style="width:500px; height:75vh;">`
                for (let i = 0; i < n_encoding; i++) {
                    if (i >= n_encoding) break;
                    var file = jsPsych.evaluateTimelineVariable(`encoding_file_${i+1}`)
                    var theta = jsPsych.evaluateTimelineVariable(`encoding_theta_${i+1}`)
                    var pos = convert2cartesian(theta)
                    html +=
                    `<div>
                        <img src="${file}" class="image-object"
                        style="top: calc(50% - ${pos.y}px); left: calc(50% + ${pos.x}px);"/>
                    </div>`
                }
                html +=
                `<div class="cross">
                    <div class="cross-vertical"></div>
                    <div class="cross-horizontal"></div>
                </div>
                </div>`

                html += getProgressBarHTML();
                return html;
                },

            on_finish: function(data) { 
                var file = []
                var theta = []
                var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding')
                
                for (let i = 0; i < n_encoding; i++) { 
                    file.push(jsPsych.evaluateTimelineVariable(`encoding_file_${i+1}`))
                    theta.push(jsPsych.evaluateTimelineVariable(`encoding_theta_${i+1}`))
                }
                data.phase = 'encoding'
                data.running_trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                data.wm_block_id = jsPsych.evaluateTimelineVariable('wm_block_id')
                data.encoding_trial_id = jsPsych.evaluateTimelineVariable('encoding_trial_id')
                data.trial_type = jsPsych.evaluateTimelineVariable('trial_type')
                data.encoding_time = jsPsych.evaluateTimelineVariable('encoding_time')
                data.stimulus = file
                data.theta = theta
                data.serial = 0;
                data.timestamp = new Date().toLocaleTimeString()
            }, 
        }
    )

    // delay for catch trials (no cue)
    wm_timeline.push({
        timeline: [{
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: experimentSettings.timing.catch_delay,
            record_data: true,
            stimulus: function(){
                var html =
                    `<div style="width:250px; height:80vh;">
                        <div class="cross"><div class="cross-vertical"></div>
                        <div class="cross-horizontal"></div></div>
                    </div>`
                html += getProgressBarHTML();
                return html;
            },
            on_finish: function(data) {
                data.stimulus = null;
                data.trial_type = "memory-delay";
                data.wm_block_id = jsPsych.evaluateTimelineVariable('wm_block_id');
                data.running_trial_id = jsPsych.evaluateTimelineVariable('trial_id');
            }
        }],
        conditional_function: function() {
            return jsPsych.evaluateTimelineVariable('trial_type') === "catch";
        }
    })

    // pre-cue delay for non-catch trials
    wm_timeline.push({
        timeline: [{
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: experimentSettings.timing.pre_cue_delay,
            record_data: true,
            stimulus: function(){
                var html =
                    `<div style="width:250px; height:80vh;">
                        <div class="cross"><div class="cross-vertical"></div>
                        <div class="cross-horizontal"></div></div>
                    </div>`
                html += getProgressBarHTML();
                return html;
            },
            on_finish: function(data) {
                data.stimulus = null;
                data.trial_type = "pre-cue-delay";
                data.wm_block_id = jsPsych.evaluateTimelineVariable('wm_block_id');
                data.running_trial_id = jsPsych.evaluateTimelineVariable('trial_id');
            }
        }],
        conditional_function: function() {
            return jsPsych.evaluateTimelineVariable('trial_type') !== "catch";
        }
    })

    // cue slide for non-catch trials
    wm_timeline.push({
        timeline: [{
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: experimentSettings.timing.cue_duration,
            record_data: true,
            stimulus: function(){
                var cue_theta = jsPsych.evaluateTimelineVariable('cue_theta')
                var cue_pos = convert2cartesian(cue_theta)

                var html =
                    `<div style="width:500px; height:75vh;">
                        <div class="cross"><div class="cross-vertical"></div>
                        <div class="cross-horizontal"></div></div>
                        <div class="square" style="top: calc(50% - ${cue_pos.y}px); left: calc(50% + ${cue_pos.x}px);">
                            X
                        </div>
                    </div>`
                html += getProgressBarHTML();
                return html;
            },
            on_finish: function(data) {
                data.stimulus = null;
                data.trial_type = "cue";
                data.cue_condition = jsPsych.evaluateTimelineVariable('cue_condition');
                data.cue_position = jsPsych.evaluateTimelineVariable('cue_position');
                data.cue_theta = jsPsych.evaluateTimelineVariable('cue_theta');
                data.wm_block_id = jsPsych.evaluateTimelineVariable('wm_block_id');
                data.running_trial_id = jsPsych.evaluateTimelineVariable('trial_id');
            }
        }],
        conditional_function: function() {
            return jsPsych.evaluateTimelineVariable('trial_type') !== "catch";
        }
    })

    // post-cue delay for non-catch trials
    wm_timeline.push({
        timeline: [{
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: experimentSettings.timing.post_cue_delay,
            record_data: true,
            stimulus: function(){
                var html =
                    `<div style="width:250px; height:80vh;">
                        <div class="cross"><div class="cross-vertical"></div>
                        <div class="cross-horizontal"></div></div>
                    </div>`
                html += getProgressBarHTML();
                return html;
            },
            on_finish: function(data) {
                data.stimulus = null;
                data.trial_type = "post-cue-delay";
                data.wm_block_id = jsPsych.evaluateTimelineVariable('wm_block_id');
                data.running_trial_id = jsPsych.evaluateTimelineVariable('trial_id');
            }
        }],
        conditional_function: function() {
            return jsPsych.evaluateTimelineVariable('trial_type') !== "catch";
        }
    })

    // Recognition Slide 
    wm_timeline.push(
        {
            type: jsPsychHtmlKeyboardResponse,
            choices: ["ArrowLeft", "ArrowRight"],
            trial_duration: 10000,

            on_load: function() {
                startTrialTimer(
                    radius=15,
                    delay=7000,
                    duration=3000,
                    top=50,
                    color="#ff0000"
                );
            },

            stimulus: function() {
                var recog_theta = jsPsych.evaluateTimelineVariable('recognition_theta')
                var recog_pos = convert2cartesian(recog_theta)

                var html =
                    `
                    <div style="width:500px; height:75vh;">
                        <div>
                            <div class="square" style="top: calc(50% - ${recog_pos.y}px); left: calc(50% + ${recog_pos.x}px);">
                                ?
                            </div>
                            <div class="cross"><div class="cross-vertical"></div>
                            <div class="cross-horizontal"></div></div>

                            <div class="rectangle"
                                style="top: calc(50% + ${button_y}px);">
                            </div>
                        </div>
                    </div>
                    `
                
                // empty squares
                var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding')
                for (let i = 0; i < n_encoding; i++) {
                    if (i >= n_encoding) break;
                    
                    var theta = jsPsych.evaluateTimelineVariable(`encoding_theta_${i+1}`)
                    if (theta == recog_theta) continue;
                    
                    var pos = convert2cartesian(theta)
                    html += `<div class="square plain" style="top: calc(50% - ${pos.y}px); left: calc(50% + ${pos.x}px);"></div>`
                }  

                // response options
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

                console.log(left_image)
                console.log(right_image)

                var left_arrow_emoji = 
                    `
                    <div style="position: absolute; top: calc(50% + ${button_y}px + 80px); left: calc(50% - 24px); 
                    transform: translateX(-50%); font-size: 30px;">&larr;
                    </div>
                    `
                 
                var right_arrow_emoji = 
                    `
                    <div style="position: absolute; top: calc(50% + ${button_y}px + 80px); left: calc(50% + 24px); 
                    transform: translateX(-50%); font-size: 30px;">&rarr;
                    </div>
                    `

                var left_button =
                    `
                    <div>
                        <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% - ${button_x}px);"
                                    src="${left_image}" class="image-object"/>
                    </div>
                    
                    `

                var right_button =
                    `
                    <div>
                        <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% + ${button_x}px);"
                                    src="${right_image}" class="image-object"/>
                    </div>
                    `
                
                html += left_button + left_arrow_emoji
                html += right_button + right_arrow_emoji

                // progress bar
                var running_trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                var progress_percent = (running_trial_id / total_trials) * 100
                var progress_bar = 
                    `
                    <div class="progress-bar">
                        <div class="progress-bar-track">
                            <div class="progress-bar-fill" style="width: ${progress_percent}%;"></div>
                            <div class="progress-marker" style="left: ${first_break}%"></div>
                            <div class="progress-marker" style="left: ${second_break}%"></div>
                        </div>
                    </div>
                    `
                
                html += progress_bar
                return html;
            },

            on_finish: function(data) {
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

                // recode response
                if (data.response === 'ArrowLeft') {
                    data.response = 0
                } else if (data.response === 'ArrowRight') {
                    data.response = 1
                } 
                
                // saving data
                data.encoding_time = jsPsych.evaluateTimelineVariable(`encoding_time`)
                data.phase = 'recognition'
                data.wm_block_id = jsPsych.evaluateTimelineVariable('wm_block_id')
                data.running_trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                data.encoding_trial_id = jsPsych.evaluateTimelineVariable('encoding_trial_id')
                data.set_id = jsPsych.evaluateTimelineVariable('set_id')
                data.target_file = jsPsych.evaluateTimelineVariable('recognition_target_file')
                data.target_correct = jsPsych.evaluateTimelineVariable('target_correct')
                data.correct_response = jsPsych.evaluateTimelineVariable('correct_response')
                data.control = jsPsych.evaluateTimelineVariable('recognition_foil_file')
                data.theta = jsPsych.evaluateTimelineVariable('recognition_theta')
                data.condition = jsPsych.evaluateTimelineVariable('condition')
                data.condition_name = jsPsych.evaluateTimelineVariable('condition_name')
                data.sample_position = jsPsych.evaluateTimelineVariable('sample_position')
                data.left_target = jsPsych.evaluateTimelineVariable('left_target')
                data.trial_type = jsPsych.evaluateTimelineVariable('trial_type')
                data.cue_condition = jsPsych.evaluateTimelineVariable('cue_condition')
                data.cue_position = jsPsych.evaluateTimelineVariable('cue_position')
                data.cue_theta = jsPsych.evaluateTimelineVariable('cue_theta')
                data.timed_out = (data.response === null);
                data.timestamp = new Date().toLocaleTimeString()

                if (data.subject_id==999) {
                    console.log("Condition: ", data.condition_name, "\tCue: ", data.cue_condition)
                    console.log("Response: ", data.response, "\tCorrect response: ", data.correct_response)
                }
            }
        }
    )
    
    // Time-out
    wm_timeline.push(
        {
            timeline: [{
                type: jsPsychHtmlKeyboardResponse,
                choices: ['Enter'],
                stimulus: function() {
                    var timeout_count = jsPsych.data.get().filter({timed_out: true}).count();
                    if (timeout_count > 15) {
                        html = 
                            `<div>
                                <p class="instruction-header">
                                    <strong>Aborting the experiment</strong>
                                </p>
                                <p class="instruction-paragraph">
                                    Unfortunately, too many trials have timed out.
                                    To ensure data quality, we need to end the experiment here.
                                    Thank you for your time and effort.
                                    <br><br>
                                    Press <strong>Enter</strong> to continue to the last slide.
                                    From there you will be automatically redirected to Prolific.
                                    <br><br>
                                    We will contact you as soon as possible.
                                    <br><br>
                                    <strong>Please don\'t close the experiment until your redirected to Prolific.</strong>
                                </p>
                                <p class="continue-prompt">
                                    To end the experiment press <strong>Enter</strong>
                                </p>
                            </div>`;
                        return html
                    }

                    html = 
                        `<div>
                            <p class="instruction-header" style="color: #ff0000;">
                                <strong>⏸ Time Out</strong>
                            </p>
                            <p class="instruction-paragraph">
                                You did not respond in the last trial.<br><br>
                                <strong style="color: #ff0000;">Please remember to respond within 30 seconds after the images appear.</strong>
                                <br><br>
                                You're doing well! Let's stay focused until the next break.
                            </p>
                            <p class="continue-prompt" style="color: #000000;">
                                Press <strong>Enter</strong> to continue
                            </p>
                        </div>`;
                    
                    return html
                },
                on_finish: function(data) {
                    data.stimulus = null;
                    data.trial_type = "timeout";
                    data.wm_block_id = jsPsych.evaluateTimelineVariable('wm_block_id');
                    data.running_trial_id = jsPsych.evaluateTimelineVariable('trial_id');
                    
                    timeout_count = jsPsych.data.get().filter({timed_out: true}).count();
                    data.timeout_count = timeout_count
                    if (timeout_count > 15){
                        jsPsych.abortExperiment('The experiment was ended due to too many timed-out trials.');
                        console.log('Aborting')
                    }
                }
            }],
            conditional_function: function() {
                return jsPsych.data.get().last(1).values()[0].timed_out;
            }
        }
    ) 

    // Feedback
    wm_timeline.push(    
        {
            timeline: [{
                type: jsPsychHtmlKeyboardResponse,
                choices: ['Enter'],
                trial_duration: experimentSettings.feedback.duration,
                record_data: true,
                stimulus: function() {
                    var sample_file = jsPsych.evaluateTimelineVariable('sample_file')
                    var foil_file = jsPsych.evaluateTimelineVariable('recognition_foil_file')
                    var target_file = jsPsych.evaluateTimelineVariable(`recognition_target_file`)
                    var left_target = jsPsych.evaluateTimelineVariable(`left_target`) 

                    if (left_target === 1) {
                        var left_image = target_file
                        var right_image = foil_file
                    } else {
                        var left_image = foil_file
                        var right_image = target_file 
                    }

                    var recog_theta = jsPsych.evaluateTimelineVariable('recognition_theta')
                    var recog_pos = convert2cartesian(recog_theta)
                    
                    var html =
                        `<div style="width:500px; height: 75vh;">
                            <p style="font-size: x-large; position: absolute; top: 50px; left: 50%;
                            transform: translateX(-50%); color:#4682B4; text-align: center;">
                                <strong></strong>
                            </p>

                            <div>
                                <div class="square"
                                    style="top: calc(50% - ${recog_pos.y}px); left: calc(50% + ${recog_pos.x}px);">
                                </div>
                            </div>

                            <div class="cross"><div class="cross-vertical"></div>
                            <div class="cross-horizontal"></div></div>

                            <div class="rectangle"
                                style="top: calc(50% + ${button_y}px);">
                            </div>
                            
                            <div>
                                <img src="${sample_file}" class="image-object feedback-blink"
                                style="width: 126px; height: 126px; top: calc(50% - ${recog_pos.y}px); left: calc(50% + ${recog_pos.x}px);"/>
                            </div>

                                                        
                            <div>
                                <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% - ${button_x}px);" 
                                            src="${left_image}" class="image-object"/>
                            </div>
                    
                            <div>
                                <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% + ${button_x}px);"  
                                    src="${right_image}" class="image-object"/>
                            </div>
                            
                            <p class="continue-prompt" style="color: #000000;">
                                Press <strong>Enter</strong> to continue
                            </p>

                        </div>`

                        // empty squares
                        var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding')
                        for (let i = 0; i < n_encoding; i++) {
                            if (i >= n_encoding) break;
                            
                            var theta = jsPsych.evaluateTimelineVariable(`encoding_theta_${i+1}`)
                            if (theta == recog_theta) continue;
                            
                            var pos = convert2cartesian(theta)
                            html += `<div class="square plain" style="top: calc(50% - ${pos.y}px); left: calc(50% + ${pos.x}px);"></div>`
                        }

                    return html;
                },
                on_finish: function(data) { 
                    data.stimulus = null;
                    data.trial_type = "practice-feedback";
                    data.running_trial_id = jsPsych.evaluateTimelineVariable('trial_id');
                }
            }], 
            conditional_function: function() {
                return jsPsych.evaluateTimelineVariable("trial_type")==="practice" && !jsPsych.data.get().last(2).values()[0].timed_out;
            }
        }
    )

    return {timeline:wm_timeline, 
            timeline_variables:timeline_variables};
}
