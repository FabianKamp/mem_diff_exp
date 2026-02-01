// Circle with correction for square rotation perception
function convert2cartesian(theta) {
    const rx = experimentSettings.spatial.radius_x;
    const ry = experimentSettings.spatial.radius_y;

    const angleOffset = (theta % (Math.PI / 2));
    const correctionFactor = 1 / Math.cos(Math.min(angleOffset, Math.PI / 2 - angleOffset));

    const x = rx * correctionFactor * Math.cos(theta);
    const y = ry * correctionFactor * Math.sin(theta);

    return {x:x, y:y};
}

// INSTRUCTIONS
function generate_instruction_angles(load) {
    var result = [1,3,6];
    for (let i = 0; i < load; i++) {
        result[i] *= Math.PI/4;
    }
    return result;
}

function createWMInstructions() {   
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
    var instruction_angles = generate_instruction_angles(experimentSettings.memory_experiment.load)
    var sample_pos = convert2cartesian(instruction_angles[1])
    var instruction_files = ["dist1.jpg", "sample1.jpg", "dist2.jpg"] // "dist3.jpg", "dist4.jpg", "dist5.jpg", "dist6.jpg"
    var encoding_positions = [] 
    for (let i = 0; i < instruction_angles.length; i++) {
        encoding_positions.push(convert2cartesian(instruction_angles[i]))
    }
    
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
            // 1/5
            [
            `<div>
                <div class="image-container"> 
                        <img src="stimuli/instructions/${instruction_files[0]}" class="image-object" 
                        style="left: calc(50% - ${encoding_positions[0].x}px); top: calc(50% + ${encoding_positions[0].y}px);"/>
                </div>
                <div class="image-container"> 
                        <img src="stimuli/instructions/${instruction_files[1]}" class="image-object" 
                        style="left: calc(50% - ${encoding_positions[1].x}px); top: calc(50% + ${encoding_positions[1].y}px);"/>
                </div>
                <div class="image-container"> 
                        <img src="stimuli/instructions/${instruction_files[2]}" class="image-object" 
                        style="left: calc(50% - ${encoding_positions[2].x}px); top: calc(50% + ${encoding_positions[2].y}px);"/>
                </div>
                
                <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
                
                <p class="instruction-paragraph-left">
                    <strong>1/5 Memorize</strong><br><br>
                    In each trial we will ask you to memorize <strong>3 images</strong>.
                    <br><br>
                    The images will be shown for about <strong>0.5 to 2 seconds</strong>. 
                    The time varies from trial to trial — some trials are fast, others are slower.
                    <br><br>
                    <strong>Important:</strong> Keep your eyes focused on the cross in the center of the screen while memorizing the images.
                    <br><br><br>
                    Note: The images shown in this experiment are computer-generated, not real photographs.
                </p>
            </div>`
            ],
            // 2/5
            [
            `<div>
                <div class="cross">
                    <div class="cross-vertical"></div>
                    <div class="cross-horizontal"></div>
                </div>       
                <p class="instruction-paragraph-left">
                    <strong>2/5 Delay</strong><br><br> 
                    Afterwards there will be a short delay. <br>
                    The delay will take a couple of seconds. <br><br>
                    Please focus on the cross on the screen.
                </p>
            </div>`
            ],
            // 3/5
            [
            `
            <div class="square plain" style="left: calc(50% - ${encoding_positions[0].x}px); top: calc(50% + ${encoding_positions[0].y}px);"></div>
            <div class="square" style="left: calc(50% - ${sample_pos.x}px); top: calc(50% + ${sample_pos.y}px);">
                ?
            </div>
            <div class="square plain" style="left: calc(50% - ${encoding_positions[2].x}px); top: calc(50% + ${encoding_positions[2].y}px);"></div>

            <div>
                <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% + ${button_x}px);" src="stimuli/instructions/sample3.jpg" class="image-object"/>
                <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% - ${button_x}px);" src="stimuli/instructions/dist4.jpg" class="image-object"/>
            </div>
            
            <div class="cross">
                <div class="cross-vertical"></div>
                <div class="cross-horizontal"></div>
            </div>

            <div class="rectangle"
                style="top: calc(50% + ${button_y}px);">
            </div>
            
            <p class="instruction-paragraph-left">
                <strong>3/5 Which image matches the original image better?</strong>
                <br><br> 
                After the delay you will see <strong>2 new images</strong> at the bottom of the screen.
                You haven't seen either of the images before.
                <br><br>
                Your task is to <strong>select the image that matches the original image better</strong> 
                by clicking on it.
                <br><br>
                The <strong>? mark</strong> indicates the location of the original image.
                <br>                
            </p>
            `
            ],
            // 4/5
            [
            `
            <div class="square plain" style="left: calc(50% - ${encoding_positions[0].x}px); top: calc(50% + ${encoding_positions[0].y}px);"></div>
            <div class="square" style="left: calc(50% - ${sample_pos.x}px); top: calc(50% + ${sample_pos.y}px);">
                ?
            </div>
            <div class="square plain" style="left: calc(50% - ${encoding_positions[2].x}px); top: calc(50% + ${encoding_positions[2].y}px);"></div>
                
            <div>
                <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% + ${button_x}px);" src="stimuli/instructions/sample3.jpg" class="image-object"/>
                <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% - ${button_x}px);" src="stimuli/instructions/dist4.jpg" class="image-object"/>
            </div>

            <div class="cross">
                <div class="cross-vertical"></div>
                <div class="cross-horizontal"></div>
            </div>

            <div class="rectangle"
                style="top: calc(50% + ${button_y}px);">
            </div>

            <p class="instruction-paragraph-left">
                <strong>4/5 What if you're uncertain?</strong>
                <br><br>
                The images can match the original image in various ways. 
                <br><br>
                If you're uncertain which image matches the original better, 
                that's okay - just make your best guess.
                <br><br><br>
                Note: Before selecting any image you have to move your mouse 
                to enable the buttons.
            </p>
            `
            ],
            // 5/5
            [
            `
            <div class="square plain" style="left: calc(50% - ${encoding_positions[0].x}px); top: calc(50% + ${encoding_positions[0].y}px);"></div>
            <div class="square" style="left: calc(50% - ${sample_pos.x}px); top: calc(50% + ${sample_pos.y}px);">
                ?
            </div>
            <div class="square plain" style="left: calc(50% - ${encoding_positions[2].x}px); top: calc(50% + ${encoding_positions[2].y}px);"></div>
                
            <div>
                <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% + ${button_x}px);" src="stimuli/instructions/sample3.jpg" class="image-object"/>
                <img style="position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% - ${button_x}px);" src="stimuli/instructions/dist4.jpg" class="image-object"/>
             </div>

            <div class="cross">
                <div class="cross-vertical"></div>
                <div class="cross-horizontal"></div>
            </div>

            <div class="rectangle"
                style="top: calc(50% + ${button_y}px);">
            </div>
            
            <p class="instruction-paragraph-left">
                <strong>5/5 What about breaks?</strong>
                <br><br> 
                The task has 3 blocks, each taking 10-12 minutes. 
                <br><br>
                You will have <strong>2 breaks</strong> (up to two minutes each) between blocks.
                <br><br>
                Your progress will be shown in a bar at the bottom of the screen.
                <br>
            </p>
            `
            ],
        ], 
        on_finish: function(data) { 
            data.stimulus = null;
            data.trial_type = "instructions";
        }
    })
    return instruction_timeline
}

// STARTING PRACTICE
function startingWMPractice(){
    var start_practice = {
        type: jsPsychInstructions,
        show_clickable_nav: false,
        key_forward: 'Enter',
        record_data: true,
        post_trial_gap: 200,
        min_viewing_time: 3000,
        pages: [
            [
            `<div>
                <p class="instruction-header">
                    <strong>Starting practice runs</strong>
                </p>
                <p class="instruction-paragraph">
                    We will start with <strong>three practice runs</strong>.
                    <br><br>
                    <strong>Feedback</strong>: During the practice runs the original image will 
                    appear again for a couple of seconds,  
                    so that you're able to compare the original image 
                    with the image you picked. 
                    <br><br>
                </p>
                <p class="continue-prompt">
                    To start press <strong>Enter</strong>
                </p>
            </div>
            `
            ]
        ],
        on_finish: function(data) { 
            data.stimulus = null;
            data.trial_type = "starting-practice";
        }
    }
    return start_practice
}

// STARTING SCREEN
function startingWM() {
    // start wm experiment
    var start_wm = {
        type: jsPsychInstructions,
        show_clickable_nav: false,
        key_forward: 'Enter',
        record_data: true,
        post_trial_gap: 200,
        min_viewing_time: 3000,
        pages: [
            [
            `<div>
                <p class="instruction-header">
                    <strong>Starting the experiment</strong>
                </p>
                <p class="instruction-paragraph">
                    Great! We will now start the experiment.
                    <br><br>
                    <strong>Reminder</strong>: The images can match the original image in various ways.
                    If you're uncertain which image matches the original better, make your best guess. 
                    <br><br>
                    Note: The experiment includes attention checks. During these trials you'll have to  
                    memorize a single image and then recognize it.
                    <br><br><br>
                    There will be <strong>no feedback</strong> during the experiment. 
                    <br>
                </p>
                <p class="continue-prompt">
                    To continue press <strong>Enter</strong>
                </p>
            </div>
            `
            ]
        ],
        on_finish: function(data) {
            // check the durations for the prelaoding until now
            var preload_durations = jsPsych.data
                .get()
                .filter({trial_type: 'preload'})
                .select('preload_duration').values
            const max_preload = Math.max(...preload_durations)
            jsPsych.data.dataProperties.connection_quality = max_preload < 1000 ? "good" : "bad";                
            jsPsych.data.dataProperties.preloadBlock = max_preload < 1000 ? false : true;
            
            if (data.subject_id == 999) {
                    console.log("Max preload: ", max_preload)
                    jsPsych.data.dataProperties.preloadBlock = true;
            }

            data.stimulus = null;
            data.trial_type = "starting-wm";
        }
    }
    return start_wm
}

// WM TASK
function createWM(timeline_variables, jsPsych) {
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
        var trial_id = jsPsych.evaluateTimelineVariable('trial_id');
        var progress_percent = (trial_id / total_trials) * 100;
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
                data.trial_id = jsPsych.evaluateTimelineVariable('trial_id');
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
                data.trial_id = jsPsych.evaluateTimelineVariable('trial_id');
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
                data.trial_id = jsPsych.evaluateTimelineVariable('trial_id')
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

    // delay
    wm_timeline.push(
        {
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: function() {
                var trial_type = jsPsych.evaluateTimelineVariable(`trial_type`)
                if (trial_type=="catch") {
                    return experimentSettings.timing.catch_delay
                } else {
                    return experimentSettings.timing.memory_delay
                }
            },
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
                data.trial_id = jsPsych.evaluateTimelineVariable('trial_id');
            }
        }
    )

    // Show cursor
    wm_timeline.push(show_cursor())

    // Mouse Movement Check (this is the same as the recognition slide, but with RESPONSE DISABLED)
    wm_timeline.push(
        {
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: 10000, // skip automatically after 10secs

            stimulus: function() {                                
                var recog_theta = jsPsych.evaluateTimelineVariable('recognition_theta')
                var recog_pos = convert2cartesian(recog_theta)
                
                var foil_file = jsPsych.evaluateTimelineVariable(`recognition_foil_file`)
                var target_file = jsPsych.evaluateTimelineVariable(`recognition_target_file`)
                var left_target = jsPsych.evaluateTimelineVariable(`left_target`)

                // Determine which image goes on which side
                if (left_target === 1) {
                    var left_image = target_file
                    var right_image = foil_file
                } else {
                    var left_image = foil_file
                    var right_image = target_file
                }

                var html =
                    `<div style="width:500px; height: 75vh;">
                        <div>
                            <div class="square"style="top: calc(50% - ${recog_pos.y}px); left: calc(50% + ${recog_pos.x}px);">
                                ?
                            </div>
                            <div class="cross"><div class="cross-vertical"></div>
                            <div class="cross-horizontal"></div></div>

                            <div class="rectangle"
                                style="top: calc(50% + ${button_y}px);">
                            </div>

                            <!-- Disabled buttons -->
                            <div style="width: 126px; height: 126px;
                                        position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% - ${button_x}px); transform: translate(-50%, -50%);">
                                <img src="${left_image}" class="image-button" style="pointer-events: none;" />
                            </div>

                            <div style="width: 126px; height: 126px;
                                        position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% + ${button_x}px); transform: translate(-50%, -50%);">
                                <img src="${right_image}" class="image-button" style="pointer-events: none;" />
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

                // progress bar
                var trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                var progress_percent = (trial_id / total_trials) * 100

                var progress_bar =
                    `<div class="progress-bar">
                        <div class="progress-bar-track">
                            <div class="progress-bar-fill" style="width: ${progress_percent}%;"></div>
                            <div class="progress-marker" style="left: ${first_break}%"></div>
                            <div class="progress-marker" style="left: ${second_break}%"></div>
                        </div>
                    </div>`

                html += progress_bar
                return html;
            },

            on_load: function() {
                const mouseHandler = createMouseHandler(jsPsych, 50, crop_mouse_history);
                document.addEventListener('mousemove', mouseHandler);
            },

            on_finish: function(data) {
                data.trial_type = "mouse-movement-check"
                data.wm_block_id = jsPsych.evaluateTimelineVariable('wm_block_id')
                data.trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                data.timestamp = new Date().toLocaleTimeString()
            }
        }
    )

    // Recognition Slide - RESPONSE ENABLED
    wm_timeline.push(
        {
            type: jsPsychHtmlButtonResponse,
            choices: ["left", "right"],
            button_layout: 'grid',
            trial_duration: 31000,

            on_load: function() {
                startTrialTimer(
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
                                position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% - ${button_x}px); transform: translate(-50%, -50%);">
                    <img src="${left_image}" class="image-button" />
                    </div>`

                right_button = 
                    `<div style="cursor: pointer; width: 126px; height: 126px; 
                                position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% + ${button_x}px); transform: translate(-50%, -50%);">
                    <img src="${right_image}" class="image-button"/>
                    </div>`
            
                if (choice == "left") {
                    return left_button;
                } else {
                    return right_button;
                }
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

                // progress bar
                var trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                var progress_percent = (trial_id / total_trials) * 100
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
                
                // saving data
                data.encoding_time = jsPsych.evaluateTimelineVariable(`encoding_time`)
                data.phase = 'recognition'
                data.wm_block_id = jsPsych.evaluateTimelineVariable('wm_block_id')
                data.trial_id = jsPsych.evaluateTimelineVariable('trial_id')
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
                data.timed_out = (data.response === null);
                data.timestamp = new Date().toLocaleTimeString()
                
                if (data.subject_id==999) {
                    console.log("Condition: ", data.condition_name)
                    console.log("Response: ", data.response)
                    console.log("Correct response: ", data.correct_response)
                }
            }
        }
    )
    
    // Time-out
    wm_timeline.push(    
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
                    data.wm_block_id = jsPsych.evaluateTimelineVariable('wm_block_id');
                    data.trial_id = jsPsych.evaluateTimelineVariable('trial_id');
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
                type: jsPsychHtmlButtonResponse,
                // choices: "Enter",
                choices: ["Next Trial"],
                button_html: (choice) => '<button class="jspsych-btn next-trial-button">' + choice + '</button>',
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

                            <div style="cursor: pointer; width: 126px; height: 126px;
                                    position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% + ${button_x}px); transform: translate(-50%, -50%);">
                                    <img src="${right_image}" class="image-button"/>
                            </div>

                            <div style="cursor: pointer; width: 126px; height: 126px;
                                    position: absolute; top: calc( 50% + ${button_y}px); left: calc( 50% - ${button_x}px); transform: translate(-50%, -50%);">
                                    <img src="${left_image}" class="image-button" />
                            </div>
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
                    data.trial_id = jsPsych.evaluateTimelineVariable('trial_id');
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

// BREAK TRIAL
function createBreak(label) {
    // break
    var break_trial = {
        type: jsPsychHtmlKeyboardResponse,
        trial_duration: 121000,
        choices: ['Enter'],
        post_trial_gap: 200,
        min_viewing_time: 10000,
        stimulus: function() {
            html = 
            `
            <div>
                <p class="instruction-header"><strong>Break #${label}</strong></p>
                <p class="instruction-paragraph"> 
                    If you need a break, you can take one now.<br><br>
                    Please allow yourself a maximum of <strong>2 minutes</strong>.<br>
                    Press <strong>enter</strong> to continue.<br><br>
                    <strong>The task will continue automatically after 2 minutes.</strong>
                </p>
                <p class="continue-prompt">
                    To continue press <strong>Enter</strong>
                </p>
            </div>
            `
            return html
        },
        
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
            data.trial_type = "break";
            data.timestamp = new Date().toLocaleTimeString()
        }
    }
    return break_trial;
}