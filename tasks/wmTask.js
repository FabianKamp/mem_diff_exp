// SETTINGS
var experimentSettings = fetch(`experimentSettings.json`)
    .then(response => response.json())
    .then(data => {
        experimentSettings = data;
    });

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
                <strong>1. Memorize</strong><br><br> 
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
                    <strong>2. Delay</strong><br><br> 
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
                <strong>3. Which image matches the original image better?</strong><br><br> 
                After the delay you will see <strong>2 new images</strong>, i.e.
                you haven't seen either of the images before.<br><br>
                Your task is to <strong>choose the image that matches the original image better</strong>.<br><br>
                The square indicates the position of the original image.
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
                <strong>4. Pick an image by clicking on it.</strong><br><br> 
                You can choose the matching image by clicking on it.<br><br> 
                If you don't remember the original image make your best guess.
            </p>
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
                    We will start with <strong>12 practice runs</strong>.
                    <br><br>
                    During the practice runs the original image will 
                    appear again as soon as you have made your choice,  
                    so that you're able to compare the original image with the image you picked. 
                    <br><br>
                    Press <strong>enter</strong> to start.
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
                    Amazing! We will now start the experiment.
                    The next break will be in ~15 minutes.<br><br>
                    Attention, there will be <strong>no feedback</strong> in during the experiment.<br><br>
                    Press <strong>enter</strong> to start.
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

// WM TASK
function convert2cartesian(rx, ry, theta) {
    const x = rx * Math.cos(theta);
    const y = ry * Math.sin(theta);
    return {x:x,y:y};
}

function createWM(timeline_variables, feedback, jsPsych) {
    // timeline: initial delay -> 3 encoding images (inter stimulus delay) -> memory delay -> recognition slide
    var wm_timeline = [];
    
    // preload
    wm_timeline.push(
    {
        type: jsPsychPreload,
        record_data: false,
        show_progress_bar: false,
        message:                 
            `<div style="width:250px; height:75vh;">
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
    })

    // inter trial delay
    wm_timeline.push(
    {
        type: jsPsychHtmlKeyboardResponse,
        choices: "NO_KEYS",
        trial_duration: experimentSettings.timing.wm_inter_trial_delay,
        record_data: false,
        stimulus: function(){
            var html = 
            `<div style="width:250px; height:75vh;">
                <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
            </div>`
            return html;
        }
    })

    // encoding
    if (experimentSettings.memory_experiment.serial == 0){
        wm_timeline.push(
            {
                type: jsPsychHtmlKeyboardResponse,
                choices: "NO_KEYS",
                trial_duration: function() {
                    var long_encoding = jsPsych.evaluateTimelineVariable(`long_encoding`)
                    if (long_encoding == 1) {
                        return experimentSettings.timing.encoding_time_long
                    } else {
                        return experimentSettings.timing.encoding_time_short
                    }
                },
                stimulus: function() {
                    var html = `<div style="width:500px; height:60vh;">`
                    var load = experimentSettings.memory_experiment.load
                    var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding')
                    
                    for (let i = 0; i < load; i++) {
                        if (i >= n_encoding) break; 
                        var file = jsPsych.evaluateTimelineVariable(`encoding_file_${i+1}`)
                        var theta = jsPsych.evaluateTimelineVariable(`encoding_theta_${i+1}`)
                        var pos = convert2cartesian(experimentSettings.spatial.radius_x, experimentSettings.spatial.radius_y, theta)
                        html +=                         
                        `<div style="width:500px; height:75vh;">
                            <div> 
                                <img src="${file}" class="image-object" 
                                style="top: calc(50% - ${pos.y}px); left: calc(50% + ${pos.x}px);"/>
                            </div>
                        </div>`
                    }

                    html += 
                    `<div class="cross">
                        <div class="cross-vertical"></div>
                        <div class="cross-horizontal"></div>
                    </div></div>`

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

                    var long_encoding = jsPsych.evaluateTimelineVariable(`long_encoding`)
                    if (long_encoding == 1) {
                        data.encoding_time = experimentSettings.timing.encoding_time_long
                    } else {
                        data.encoding_time = experimentSettings.timing.encoding_time_short
                    }

                    data.stimulus = file
                    data.theta = theta
                    data.trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                    data.trial_type = jsPsych.evaluateTimelineVariable('trial_type');
                    data.phase = 'encoding';
                    data.timestamp = new Date().toLocaleTimeString()
                }
            }
        )
    
    } else {
        // SERIAL ENCODING
        var load = experimentSettings.memory_experiment.load
        for (let i = 0; i < load; i++) {
            wm_timeline.push({
                timeline: [{
                    type: jsPsychHtmlKeyboardResponse,
                    choices: "NO_KEYS",
                    trial_duration: function() {
                        var long_encoding = jsPsych.evaluateTimelineVariable(`long_encoding`)
                        var n_encoding = jsPsych.evaluateTimelineVariable(`n_encoding`)
                        if (long_encoding == 1) {
                            return experimentSettings.timing.encoding_time_long/n_encoding
                        } else {
                            return experimentSettings.timing.encoding_time_short/n_encoding
                        }
                    },
                    stimulus: function() {
                        var html = `<div style="width:500px; height:60vh;">`
                        var file = jsPsych.evaluateTimelineVariable(`encoding_file_${i+1}`)
                        var theta = jsPsych.evaluateTimelineVariable(`encoding_theta_${i+1}`)
                        var pos = convert2cartesian(experimentSettings.spatial.radius_x, experimentSettings.spatial.radius_y, theta)
                        console.log(file)
                        html +=                         
                        `<div style="width:500px; height:75vh;">
                            <div> 
                                <img src="${file}" class="image-object" 
                                style="top: calc(50% - ${pos.y}px); left: calc(50% + ${pos.x}px);"/>
                            </div>
                        </div>`
                        html += 
                        `<div class="cross">
                            <div class="cross-vertical"></div>
                            <div class="cross-horizontal"></div>
                        </div></div>`
                        return html;
                    },
                    on_finish: function(data) { 
                        var file = jsPsych.evaluateTimelineVariable(`encoding_file_${i+1}`)
                        var theta = jsPsych.evaluateTimelineVariable(`encoding_theta_${i+1}`)
                        var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding')
                        var long_encoding = jsPsych.evaluateTimelineVariable(`long_encoding`)
                        if (long_encoding == 1) {
                            data.encoding_time = experimentSettings.timing.encoding_time_long/n_encoding
                        } else {
                            data.encoding_time = experimentSettings.timing.encoding_time_short/n_encoding
                        }
                        data.stimulus = file
                        data.theta = theta
                        data.n_encoding = n_encoding
                        data.trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                        data.trial_type = jsPsych.evaluateTimelineVariable('trial_type');
                        data.phase = 'encoding';
                        data.encoding_position = i+1;
                        data.timestamp = new Date().toLocaleTimeString()
                    }
                }],
                conditional_function: function() {
                    var n_encoding = jsPsych.evaluateTimelineVariable('n_encoding')
                    return i < n_encoding
                }
            })
            
            // ISI
            wm_timeline.push(
            {
                type: jsPsychHtmlKeyboardResponse,
                choices: "NO_KEYS",
                trial_duration: experimentSettings.timing.wm_isi,
                record_data: false,
                stimulus: function(){
                    var html = 
                    `<div style="width:250px; height:75vh;">
                        <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
                    </div>`
                    return html;
                }
            })
        }
    }

    // delay
    wm_timeline.push(
        {
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: experimentSettings.timing.memory_delay,
            record_data: false,
            stimulus: function(){
                var html = 
                    `<div style="width:250px; height:75vh;">
                        <div class="cross"><div class="cross-vertical"></div>
                        <div class="cross-horizontal"></div></div>
                    </div>`
                return html;
            }
        }
    )
    
    // recognition
    wm_timeline.push(
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
                var theta = jsPsych.evaluateTimelineVariable('recognition_theta')
                var pos = convert2cartesian(experimentSettings.spatial.radius_x, experimentSettings.spatial.radius_y, theta)
                var html = 
                    `<div style="width:500px; height: 60vh;">
                        <p style="font-size: x-large; position: absolute; top: 50px; left: 50%; 
                        transform: translateX(-50%); color:#4682B4; text-align: center;">
                            <strong></strong>
                        </p>

                        <div> 
                            <div class="square" 
                                style="top: calc(50% - ${pos.y}px); left: calc(50% + ${pos.x}px);">
                            </div>
                        </div>

                        <div style="width:250px; height:75vh;">
                            <div class="cross">
                                <div class="cross-vertical" style="background-color: rgba(0, 0, 0, 0.05);"></div>
                                <div class="cross-horizontal" style="background-color: rgba(0, 0, 0, 0.05);"></div>
                            </div>
                        </div>
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
                data.timestamp = new Date().toLocaleTimeString()
            }
        }
    )

    if (feedback == 1) {
        wm_timeline.push(
            {
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
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
                    `<div style="width:500px; height: 75vh;">
                        <p style="font-size: x-large; position: absolute; top: 50px; left: 50%; 
                        transform: translateX(-50%); color:#4682B4; text-align: center;">
                            <strong></strong>
                        </p>

                        <div> 
                            <div class="square" 
                                style="top: calc(50% - ${pos.y}px); left: calc(50% + ${pos.x}px);">
                            </div>
                        </div>

                        <div style="width:500px; height:75vh;">
                            <div> 
                                <img src="${wm_sample_file}" class="image-object feedback-blink" 
                                style="top: calc(50% - ${pos.y}px); left: calc(50% + ${pos.x}px);"/>
                            </div>
                        </div>

                        <div style="cursor: pointer; width: 130px; height: 130px;
                                position: absolute; top: 50%; left: calc( 50% + 80px); transform: translate(-50%, -50%);">
                                <img src="${right_image}" class="image-button"/>
                        </div>

                        <div style="cursor: pointer; width: 130px; height: 130px;
                                position: absolute; top: 50%; left: calc( 50% - 80px); transform: translate(-50%, -50%);">
                                <img src="${left_image}" class="image-button" />
                        </div>

                        <div style="width:250px; height:75vh;">
                            <div class="cross">
                                <div class="cross-vertical" style="background-color: rgba(0, 0, 0, 0.05);"></div>
                                <div class="cross-horizontal" style="background-color: rgba(0, 0, 0, 0.05);"></div>
                            </div>
                        </div>

                    </div>`
                return html;
            }
        }) 
    }   
    return {timeline:wm_timeline, timeline_variables:timeline_variables};
}

// slide after WM
function endingWM() {
    var end_wm = {
        type: jsPsychHtmlKeyboardResponse, 
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
        trial_duration: 120000
    }
    return end_wm
}

