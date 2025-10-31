// SETTINGS
var experimentSettings = fetch(`experimentSettings.json`)
    .then(response => response.json())
    .then(data => {
        experimentSettings = data;
    });

// superellipse version with n=3 for rounder edges
function convert2cartesian(rx, ry, theta, n=3) {
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
    var instruction_angles = generate_instruction_angles(experimentSettings.memory_experiment.load)
    var sample_pos = convert2cartesian(experimentSettings.spatial.radius_x, experimentSettings.spatial.radius_y, instruction_angles[1])
    var instruction_files = ["dist1.jpg", "sample1.jpg", "dist2.jpg", "dist3.jpg", "dist4.jpg", "dist5.jpg", "dist6.jpg"]
    var encoding_slide = `<div>`
    for (let i = 0; i < instruction_angles.length; i++) {
        var pos = convert2cartesian(experimentSettings.spatial.radius_x, experimentSettings.spatial.radius_y, instruction_angles[i])
        encoding_slide += 
            `<div class="image-container"> 
                <img src="stimuli/instructions/${instruction_files[i]}" class="image-object" 
                style="left: calc(50% - ${pos.x}px); top: calc(50% + ${pos.y}px);"/>
            </div>`
    }
    encoding_slide += 
        `<div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
            <p class="instruction-paragraph-left">
                <strong>1/6 Memorize</strong><br><br> 
                We will ask you to memorize <strong>${experimentSettings.memory_experiment.load} images</strong>.<br><br>
                You have <strong>1-3 seconds</strong> to memorize all images.<br><br>
                The time to memorize the images will vary from trial to trial.<br><br>
            </p>
            </div>`
    
    var wm_instruction = {
        type: jsPsychInstructions,
        key_forward: 'ArrowRight',
        key_backward: 'ArrowLeft',
        show_clickable_nav: true,
        record_data: false,
        pages: [
            [
            `<div>
                <p class="instruction-header"><strong>Instructions</strong></p>
                <p class="instruction-paragraph">
                    During this experiment, we will ask you to memorize images that appear on your the screen.
                    <br><br>
                    The following instructions will explain in detail how the task works.
                    <br><br><br>
                    <strong>The instructions are self-paced</strong>. 
                    You can navigate back and forth through the instructions using the buttons below 
                    or using the arrow keys on your keyboard.
                </p>
                
            </div>`
            ],
            encoding_slide,
            [
            `<div>
                <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>       
                <p class="instruction-paragraph-left">
                    <strong>2/6 Delay</strong><br><br> 
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
                <img style="position: absolute; top: 50%; left: calc( 50% + 80px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                <img style="position: absolute; top: 50%; left: calc( 50% - 80px);" src="stimuli/instructions/sample4.jpg" class="image-object"/>
            </div>

            <p class="instruction-paragraph-left">
                <strong>3/6 Which image matches the original image better?</strong>
                <br><br> 
                After the delay you will see <strong>2 new images</strong>.
                You haven't seen either of the images before.
                <br><br>
                Your task is to <strong>choose the image that matches the original image better</strong>
                by clicking on it.
                <br><br>
                The square indicates the position of the original image.
                <div class="cross">
                    <div class="cross-vertical" style="opacity: .1;"></div>
                    <div class="cross-horizontal" style="opacity: .1;"></div>
                </div>
            </p>
            `
            ],
            [
            `<div class="square" 
                style="left: calc(50% - ${sample_pos.x}px); top: calc(50% + ${sample_pos.y}px);">
            </div>
                
            <div>
                <img style="position: absolute; top: 50%; left: calc( 50% + 80px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                <img style="position: absolute; top: 50%; left: calc( 50% - 80px);" src="stimuli/instructions/sample4.jpg" class="image-object"/>
            </div>

            <p class="instruction-paragraph-left">
                <strong>4/6 What if you're uncertain?</strong>
                <br><br>
                The images can match in many ways.
                <br><br> 
                If you're uncertain which image matches the original better, 
                that's okay - just make your best guess.
            </p>

            <div class="cross">
                <div class="cross-vertical" style="opacity: .1;"></div>
                <div class="cross-horizontal" style="opacity: .1;"></div>
            </div>
            `
            ],
            [
            `<div class="square" 
                style="left: calc(50% - ${sample_pos.x}px); top: calc(50% + ${sample_pos.y}px);">
            </div>
                
            <div>
                <img style="position: absolute; top: 50%; left: calc( 50% + 80px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                <img style="position: absolute; top: 50%; left: calc( 50% - 80px);" src="stimuli/instructions/sample4.jpg" class="image-object"/>
             </div>
            
            <p class="instruction-paragraph-left">
                <strong>5/6 Response timing</strong><br><br> 
                You will have <strong>30 seconds</strong> to select an image on each trial. 
                <br><br>
                Please try to respond within this time window.
            </p>

            <div class="cross">
                <div class="cross-vertical" style="opacity: .1;"></div>
                <div class="cross-horizontal" style="opacity: .1;"></div>
            </div>
            `
            ],
            [
            `<div class="square" 
                style="left: calc(50% - ${sample_pos.x}px); top: calc(50% + ${sample_pos.y}px);">
            </div>
                
            <div>
                <img style="position: absolute; top: 50%; left: calc( 50% + 80px);" src="stimuli/instructions/sample2.jpg" class="image-object"/>
                <img style="position: absolute; top: 50%; left: calc( 50% - 80px);" src="stimuli/instructions/sample4.jpg" class="image-object"/>
             </div>
            
             <div class="progress-bar" style="bottom: 140px;">
                <div class="progress-bar-track">
                    <div class="progress-bar-fill" style="width: 10%;"></div>
                    <div class="progress-marker" style="left: 33%"></div>
                    <div class="progress-marker" style="left: 66%"></div>
                </div>
            </div>
            
            <p class="instruction-paragraph-left">
                <strong>6/6 What about breaks?</strong><br><br> 
                At the bottom of your screen, you'll see a progress bar to help you track your progress through the task. 
                <br><br>
                You will have <strong>2 breaks</strong> during this task, each lasting up to 2 minutes. 
                Each block between breaks takes approximately 8 minutes to complete.
                <br>
            </p>

            <div class="cross">
                <div class="cross-vertical" style="opacity: .1;"></div>
                <div class="cross-horizontal" style="opacity: .1;"></div>
            </div>
            `
            ],
        ]
    }
    return wm_instruction
}

// STARTING PRACTICE
function startingWMPractice(){
    var start_practice = {
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
                    <strong>Starting practice runs</strong>
                </p>
                <p class="instruction-paragraph">
                    We will start with <strong>6 practice runs</strong>.
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
    }
    return start_practice
}

// STARTING SCREEN
function startingWM () {
    // start wm experiment
    var start_wm = {
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
                    Great! We will now start the experiment.
                    The next break will be in ~8 minutes.<br><br>
                    <strong>Attention</strong>, there will be no feedback during the experiment and
                    the next trial will start automatically as soon as you responded.
                </p>
                <p class="continue-prompt">
                    To continue press <strong>Enter</strong>
                </p>
            </div>
            `
            ]
        ],
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
    
    // timeline 
    var wm_timeline = []
    
    // preload
    wm_timeline.push(
        {
            type: jsPsychPreload,
            record_data: false,
            show_progress_bar: false,
            message:                 
                `<div style="width:250px; height:80vh;">
                    <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
                </div>`,
            show_detailed_errors: true,
            images: function() {
                var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding')
                var files = [];
                for (let i = 0; i < n_encoding; i++) {
                    var file = jsPsych.evaluateTimelineVariable(`encoding_file_${i+1}`);
                    files.push(file)
                }
                files.push(jsPsych.evaluateTimelineVariable('recognition_target_file'))
                files.push(jsPsych.evaluateTimelineVariable('recognition_control_file'))
                return files;
            }
        }
    )
    
    // inter trial delay
    wm_timeline.push(    
        {
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: experimentSettings.timing.wm_inter_trial_delay,
            record_data: false,
            stimulus: function(){
                var html = 
                `<div style="width:250px; height:80vh;">
                    <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
                </div>`
                return html;
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
                    var pos = convert2cartesian(experimentSettings.spatial.radius_x, experimentSettings.spatial.radius_y, theta)
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
                
                return html;
                },

                on_finish: function(data) { 
                    var file = []
                    var theta = []
                    var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding')
                    var long_encoding = jsPsych.evaluateTimelineVariable('long_encoding')
                    var encoding_time = jsPsych.evaluateTimelineVariable('encoding_time')
                    
                    for (let i = 0; i < n_encoding; i++) { 
                        file.push(jsPsych.evaluateTimelineVariable(`encoding_file_${i+1}`))
                        theta.push(jsPsych.evaluateTimelineVariable(`encoding_theta_${i+1}`))
                    }
                    
                    data.long_encoding = long_encoding
                    data.encoding_time = encoding_time
                    data.stimulus = file
                    data.theta = theta
                    data.trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                    data.trial_type = jsPsych.evaluateTimelineVariable('trial_type');
                    data.phase = 'encoding';
                    data.serial  = 0;
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
                                var pos = convert2cartesian(experimentSettings.spatial.radius_x, experimentSettings.spatial.radius_y, theta)

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
                                return html;
                            },

                            on_finish: function(data) {
                                var file = jsPsych.evaluateTimelineVariable(`encoding_file_${encodingIndex}`)
                                var theta = jsPsych.evaluateTimelineVariable(`encoding_theta_${encodingIndex}`)
                                var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding')
                                var long_encoding = jsPsych.evaluateTimelineVariable('long_encoding')
                                var encoding_time = jsPsych.evaluateTimelineVariable('encoding_time')

                                data.long_encoding = long_encoding
                                data.encoding_time = encoding_time/n_encoding
                                data.stimulus = file
                                data.theta = theta
                                data.n_encoding = n_encoding
                                data.trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                                data.trial_type = jsPsych.evaluateTimelineVariable('trial_type');
                                data.phase = 'encoding';
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
                                    <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
                                </div>`
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
            record_data: false,
            stimulus: function(){
                var html = 
                    `<div style="width:250px; height:80vh;">
                        <div class="cross"><div class="cross-vertical"></div>
                        <div class="cross-horizontal"></div></div>
                    </div>`
                return html;
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
                var theta = jsPsych.evaluateTimelineVariable('recognition_theta')
                var pos = convert2cartesian(experimentSettings.spatial.radius_x, experimentSettings.spatial.radius_y, theta)

                var html =
                    `<div style="width:500px; height: 75vh;">
                        <div>
                            <div class="square"
                                style="top: calc(50% - ${pos.y}px); left: calc(50% + ${pos.x}px);">
                            </div>

                            <div class="cross">
                                <div class="cross-vertical" style="opacity: .1;"></div>
                                <div class="cross-horizontal" style="opacity: .1;"></div>
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
                data.image_id = jsPsych.evaluateTimelineVariable('wm_id')
                data.target = jsPsych.evaluateTimelineVariable('recognition_target_file')
                data.target_correct = jsPsych.evaluateTimelineVariable('target_correct')
                data.correct_response = jsPsych.evaluateTimelineVariable('correct_response')
                data.control = jsPsych.evaluateTimelineVariable('recognition_control_file')
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

    // Feedback
    wm_timeline.push(    
        {
            timeline: [{
                // type: jsPsychHtmlKeyboardResponse,
                type: jsPsychHtmlButtonResponse,
                // choices: "Enter",
                choices: ["Next Trial"],
                button_html: (choice) => '<button class="jspsych-btn next-trial-button">' + choice + '</button>',
                trial_duration: experimentSettings.feedback.duration,
                record_data: false,
                stimulus: function() {
                    var wm_sample_file = jsPsych.evaluateTimelineVariable('wm_sample_file')
                    var control_file = jsPsych.evaluateTimelineVariable('recognition_control_file')
                    var target_file = jsPsych.evaluateTimelineVariable(`recognition_target_file`)
                    var left_target = jsPsych.evaluateTimelineVariable(`left_target`) 

                    if (left_target === 1) {
                        var left_image = target_file
                        var right_image = control_file
                    } else {
                        var left_image = control_file
                        var right_image = target_file 
                    }

                    var theta = jsPsych.evaluateTimelineVariable('recognition_theta')
                    var pos = convert2cartesian(experimentSettings.spatial.radius_x, experimentSettings.spatial.radius_y, theta)
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
                                <img src="${wm_sample_file}" class="image-object feedback-blink" 
                                style="top: calc(50% - ${pos.y}px); left: calc(50% + ${pos.x}px);"/>
                            </div>

                            <div style="cursor: pointer; width: 130px; height: 130px;
                                    position: absolute; top: 50%; left: calc( 50% + 75px); transform: translate(-50%, -50%);">
                                    <img src="${right_image}" class="image-button"/>
                            </div>

                            <div style="cursor: pointer; width: 130px; height: 130px;
                                    position: absolute; top: 50%; left: calc( 50% - 75px); transform: translate(-50%, -50%);">
                                    <img src="${left_image}" class="image-button" />
                            </div>

                            <div class="cross">
                                <div class="cross-vertical" style="opacity: .1;"></div>
                                <div class="cross-horizontal" style="opacity: .1;"></div>
                            </div>

                        </div>`
                    return html;
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

