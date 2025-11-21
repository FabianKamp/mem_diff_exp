// superellipse version with n=3 for rounder edges
function convert2cartesian(theta) {
    
    const rx = experimentSettings.spatial.radius_x;
    const ry = experimentSettings.spatial.radius_y;
    const n = experimentSettings.spatial.n;

    console.log(theta)
    // console.log(rx)
    // console.log(ry)

    const cos_t = Math.cos(theta);
    const sin_t = Math.sin(theta);

    const x = rx * Math.sign(cos_t) * Math.pow(Math.abs(cos_t), 2/n);
    const y = ry * Math.sign(sin_t) * Math.pow(Math.abs(sin_t), 2/n);

    return {x:x, y:y};
}

// INSTRUCTIONS
function generate_instruction_angles(load) {
    var result = [];
    var step = (2 * Math.PI) / load;
    var offset = Math.PI / 6; // 30 degree offset
    for (let i = 0; i < load; i++) {
        result.push(i * step + offset);
    }
    return result;
}

function createWMInstructions() {   
    // instruction angles
    const button_pos = experimentSettings.spatial.button_pos
    var instruction_angles = generate_instruction_angles(experimentSettings.memory_experiment.load)
    var sample_pos = convert2cartesian(instruction_angles[1])
    var instruction_files = ["dist1.jpg", "sample1.jpg", "dist2.jpg", "dist3.jpg", "dist4.jpg", "dist5.jpg", "dist6.jpg"]
    var encoding_slide = `<div>`
    for (let i = 0; i < instruction_angles.length; i++) {
        var pos = convert2cartesian(instruction_angles[i])
        encoding_slide += 
            `<div class="image-container"> 
                <img src="stimuli/instructions/${instruction_files[i]}" class="image-object" 
                style="left: calc(50% - ${pos.x}px); top: calc(50% + ${pos.y}px);"/>
            </div>`
    }
    encoding_slide += 
        `<div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
            <p class="instruction-paragraph-left">
                <strong>1/5 Memorize</strong><br><br>
                We will ask you to memorize <strong>${experimentSettings.memory_experiment.load} images</strong>.<br><br>
                ${experimentSettings.memory_experiment.serial === 1 ? 'The images will appear <strong>sequentially</strong> on the screen.<br><br>' : ''}
                You'll have <strong>1-3 seconds</strong> to memorize all images.
            </p>
            </div>`
    
    var wm_instruction = {
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
                    During this experiment, we will ask you to memorize images that appear on your the screen.
                    <br><br>
                    <strong>The instructions are self-paced</strong>. 
                    You can navigate back and forth through the instructions using the buttons below 
                    or using the arrow keys on your keyboard.
                    <br><br>
                </p>
                
            </div>`
            ],
            encoding_slide,
            [
            `<div>
                <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>       
                <p class="instruction-paragraph-left">
                    <strong>2/5 Delay</strong><br><br> 
                    Afterwards there will be a short delay. <br><br>
                    The delay will take a couple of seconds. <br><br>
                    Please focus on the cross on the screen.
                </p>
            </div>`
            ],
            [
            `<div class="square" 
                style="left: calc(50% - ${sample_pos.x}px); top: calc(50% + ${sample_pos.y}px);">
            </div>
                
            <div>
                <img style="position: absolute; top: 50%; left: calc( 50% + ${button_pos}px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                <img style="position: absolute; top: 50%; left: calc( 50% - ${button_pos}px);" src="stimuli/instructions/sample4.jpg" class="image-object"/>
            </div>
            <p class="instruction-paragraph-left">
                <strong>3/5 Which image matches the original image better?</strong>
                <br><br> 
                After the delay you will see <strong>2 new images</strong>.
                You haven't seen either of the images before.
                <br><br>
                Your task is to <strong>select the image that matches the original image better</strong> 
                by clicking on it.
                <br><br>
                The square indicates the position of the original image.
            </p>
            `
            ],
            [
            `<div class="square" 
                style="left: calc(50% - ${sample_pos.x}px); top: calc(50% + ${sample_pos.y}px);">
            </div>
                
            <div>
                <img style="position: absolute; top: 50%; left: calc( 50% + ${button_pos}px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                <img style="position: absolute; top: 50%; left: calc( 50% - ${button_pos}px);" src="stimuli/instructions/sample4.jpg" class="image-object"/>
            </div>

            <p class="instruction-paragraph-left">
                <strong>4/5 What if you're uncertain?</strong>
                <br><br>
                The images can match the original image in various ways.
                <br><br> 
                If you're uncertain which image matches the original better, 
                that's okay - just make your best guess.
            </p>
            `
            ],
            [
            `<div class="square" 
                style="left: calc(50% - ${sample_pos.x}px); top: calc(50% + ${sample_pos.y}px);">
            </div>
                
            <div>
                <img style="position: absolute; top: 50%; left: calc( 50% + ${button_pos}px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                <img style="position: absolute; top: 50%; left: calc( 50% - ${button_pos}px);" src="stimuli/instructions/sample4.jpg" class="image-object"/>
             </div>
            
             <div class="progress-bar" style="bottom: 140px;">
                <div class="progress-bar-track">
                    <div class="progress-bar-fill" style="width: 10%;"></div>
                    <div class="progress-marker" style="left: 33%"></div>
                    <div class="progress-marker" style="left: 66%"></div>
                </div>
            </div>
            
            <p class="instruction-paragraph-left">
                <strong>5/5 What about breaks?</strong><br><br> 
                You will have <strong>2 breaks</strong>, each lasting up to two minutes. 
                Each block between breaks takes ~8 minutes to complete.
                <br><br>
                At the bottom of your screen, 
                you'll see a progress bar to help you track your progress during the task. 
                <br>
            </p>
            `
            ],
        ], 
        on_finish: function(data) { 
            data.stimulus = null;
            data.trial_type = "instructions";
        }
    }
    return wm_instruction
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
                    During the practice runs the original image will 
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
                    If you're uncertain which image matches the original better, 
                    make your best guess. 
                    <br><br>
                    There will be <strong>no feedback</strong> during the experiment and
                    the next trial will start automatically as soon as you responded.
                    <br><br>
                    The next break will be in ~8 minutes.
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
            data.stimulus = null;
            data.trial_type = "starting-wm";
        }
    }
    return start_wm
}

// Ending WM
function endingWM() {
    var end_wm = {
        type: jsPsychHtmlKeyboardResponse, 
        trial_duration: 120000,
        stimulus: 
            `<div>
                <p class="instruction-paragraph"> 
                    <strong>Great, you have successfully completed the first task!</strong><br><br>

                    You are free to take a short break now before 
                    beginning the next task (max. 2 minutes)<br><br>
                    
                    The following task will be much shorter.
                    The next slide will have the detailed instructions.
                </p>
                <p class="continue-prompt">
                    To continue press <strong>Enter</strong>
                </p>
            </div>`,
        choices: ['Enter'],
        on_finish: function(data) { 
            data.stimulus = null;
            data.trial_type = "ending-wm";
        }
    }
    return end_wm
}

// WM TASK
function createWM(timeline_variables, jsPsych) {
    // set up progress bar
    const { wm_trials, ncatch, practice_trials } = experimentSettings.memory_experiment;
    const total_trials = wm_trials + ncatch + practice_trials;
    const block_size = (wm_trials + ncatch) / 3;
    const first_break = 100 * (practice_trials + block_size) / total_trials;
    const second_break = 100 * (practice_trials + 2 * block_size) / total_trials;
    const button_pos = experimentSettings.spatial.button_pos

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
    
    // preload
    wm_timeline.push(
        {
            type: jsPsychPreload,
            record_data: true,
            show_progress_bar: false,
            message:  function() {               
                html = 
                `<div style="width:250px; height:80vh;">
                    <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
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
                data.stimulus = null;
                data.trial_type = "preload";
                data.wm_block_id = jsPsych.evaluateTimelineVariable('wm_block_id');
                data.trial_id = jsPsych.evaluateTimelineVariable('trial_id');
            }
        }
    )
    
    // inter trial delay
    wm_timeline.push(
        {
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: function() {
                var preload_time = jsPsych.data.get().last(1).values()[0].time_elapsed
                var recognition_time = jsPsych.data.get().last(2).values()[0].time_elapsed
                var preload_delay = (preload_time-recognition_time)
                var delay = Math.max(experimentSettings.timing.wm_inter_trial_delay-preload_delay,0)
                return delay  
            },
            record_data: true,
            stimulus: function(){
                var html =
                `<div style="width:250px; height:80vh;">
                    <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
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
        }
    )

    // Parallel encoding
    wm_timeline.push(
        {timeline: [{
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: function() {
                var encoding_time = jsPsych.evaluateTimelineVariable(`encoding_time`)
                return encoding_time
            },
            stimulus: function() {
                var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding')
                html = `<div style="width:500px; height:80vh;">`
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
                    data.long_encoding = jsPsych.evaluateTimelineVariable('long_encoding')
                    data.encoding_time = jsPsych.evaluateTimelineVariable('encoding_time')
                    data.stimulus = file
                    data.theta = theta
                    data.serial = 0;
                    data.timestamp = new Date().toLocaleTimeString()
                }, 
            }],
            conditional_function: function() {
                return experimentSettings.memory_experiment.serial == 0;
            }
        }
    )

    // Serial encoding
    wm_timeline.push(    
        {
            timeline: (() => {
                var encoding_slides = [];
                var load = experimentSettings.memory_experiment.load
                
                for (let i = 0; i < load; i++) {
                    const encodingIndex = i + 1;

                    // Encoding trial
                    encoding_slides.push({
                        timeline: [
                        {
                            type: jsPsychHtmlKeyboardResponse,
                            choices: "NO_KEYS",
                            trial_duration: function() {
                                var encoding_time = jsPsych.evaluateTimelineVariable(`encoding_time`)
                                var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding')
                                return encoding_time/n_encoding
                            },
                            stimulus: function() {
                                var file = jsPsych.evaluateTimelineVariable(`encoding_file_${encodingIndex}`)
                                var theta = jsPsych.evaluateTimelineVariable(`encoding_theta_${encodingIndex}`)
                                var pos = convert2cartesian(theta)

                                html =
                                `<div style="width:500px; height:80vh;">
                                    <div>
                                        <img src="${file}" class="image-object"
                                        style="top: calc(50% - ${pos.y}px); left: calc(50% + ${pos.x}px);"/>
                                    </div>
                                `
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
                                var file = jsPsych.evaluateTimelineVariable(`encoding_file_${encodingIndex}`)
                                var theta = jsPsych.evaluateTimelineVariable(`encoding_theta_${encodingIndex}`)
                                var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding')
                                var long_encoding = jsPsych.evaluateTimelineVariable('long_encoding')
                                var encoding_time = jsPsych.evaluateTimelineVariable('encoding_time')

                                data.phase = 'encoding';
                                data.trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                                data.encoding_trial_id = jsPsych.evaluateTimelineVariable('encoding_trial_id')
                                data.wm_block_id = jsPsych.evaluateTimelineVariable('wm_block_id')
                                data.long_encoding = long_encoding
                                data.encoding_time = encoding_time/n_encoding
                                data.stimulus = file
                                data.theta = theta
                                data.n_encoding = n_encoding
                                data.trial_type = jsPsych.evaluateTimelineVariable('trial_type')
                                data.encoding_position = encodingIndex;
                                data.serial  = 1;
                                data.timestamp = new Date().toLocaleTimeString()
                            }
                        },

                        // ISI
                        {
                            type: jsPsychHtmlKeyboardResponse,
                            choices: "NO_KEYS",
                            trial_duration: experimentSettings.timing.wm_isi,
                            record_data: false,
                            stimulus: function(){
                                var html =
                                `<div style="width:250px; height:80vh;">
                                    <div class="cross"><div class="cross-vertical"></div><div 
                                    class="cross-horizontal"></div></div>
                                </div>`
                                html += getProgressBarHTML();
                                return html;
                                }
                        }],
                        conditional_function: function() {
                            var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding');
                            return encodingIndex <= n_encoding;
                        }
                    });
                }
                return encoding_slides;
            })(),

            conditional_function: function() {
                return experimentSettings.memory_experiment.serial == 1;
            }
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

    // Recognition
    wm_timeline.push(
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
                                position: absolute; top: 50%; left: calc( 50% - ${button_pos}px); transform: translate(-50%, -50%);">
                    <img src="${left_image}" class="image-button" />
                    </div>`

                right_button = 
                    `<div style="cursor: pointer; width: 126px; height: 126px; 
                                position: absolute; top: 50%; left: calc( 50% + ${button_pos}px); transform: translate(-50%, -50%);">
                    <img src="${right_image}" class="image-button"/>
                    </div>`
            
                if (choice == "left") {
                    return left_button;
                } else {
                    return right_button;
                }
            },

            stimulus: function() {
                var theta = jsPsych.evaluateTimelineVariable('recognition_theta')
                var pos = convert2cartesian(theta)

                var html =
                    `<div style="width:500px; height: 75vh;">
                        <div>
                            <div class="square"
                                style="top: calc(50% - ${pos.y}px); left: calc(50% + ${pos.x}px);">
                            </div>
                        </div>
                    </div>
                    `

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

            on_finish: function(data) {
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

                // encoding time
                var long_encoding = jsPsych.evaluateTimelineVariable(`long_encoding`)
                if (long_encoding == 1) {
                    data.encoding_time = experimentSettings.timing.encoding_time_long
                } else {
                    data.encoding_time = experimentSettings.timing.encoding_time_short
                }

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

                    var theta = jsPsych.evaluateTimelineVariable('recognition_theta')
                    var pos = convert2cartesian(theta)
                    var html =
                        `<div style="width:500px; height: 80vh;">
                            <p style="font-size: x-large; position: absolute; top: 50px; left: 50%;
                            transform: translateX(-50%); color:#4682B4; text-align: center;">
                                <strong></strong>
                            </p>

                            <div>
                                <div class="square"
                                    style="top: calc(50% - ${pos.y}px); left: calc(50% + ${pos.x}px);">
                                </div>
                            </div>

                            <div>
                                <img src="${sample_file}" class="image-object feedback-blink"
                                style="width: 100px; height: 100px; top: calc(50% - ${pos.y}px); left: calc(50% + ${pos.x}px);"/>
                            </div>

                            <div style="cursor: pointer; width: 126px; height: 126px;
                                    position: absolute; top: 50%; left: calc( 50% + ${button_pos}px); transform: translate(-50%, -50%);">
                                    <img src="${right_image}" class="image-button"/>
                            </div>

                            <div style="cursor: pointer; width: 126px; height: 126px;
                                    position: absolute; top: 50%; left: calc( 50% - ${button_pos}px); transform: translate(-50%, -50%);">
                                    <img src="${left_image}" class="image-button" />
                            </div>
                        </div>`
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
            startTimer(
                radius=12,
                delay=100,
                duration=120000,
                top=80,
                color="#f0f0f0  "
            );
        },
        
        on_finish: function(data) {
            resetTimer();

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