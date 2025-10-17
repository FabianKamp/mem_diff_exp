// LM INSTRUCTIONS
function createLMInstructions() {
    const lm_base_layout = () => `
        <div style="width:900px; height:40vh; position: relative; margin: 0 auto;">
            <p style="font-family: 'Courier New', monospace; font-size: x-large; position: absolute; top: -140px; left: 50%;
                    transform: translate(-50%, -50%); color:#4682B4; text-align: center;">
                <strong>Have you seen this image before?</strong>
            </p>
            <img src="stimuli/instructions/sample1.jpg" style="position: absolute; border-radius:10px;
                                    height:200px; width:200px; top: 30%; left: 50%;
                                    transform: translate(-50%, -50%);"/>
            `;

    const lm_scale_labels = () => `
            <div style="position: absolute; bottom: .6em; left: 50%; transform: translateX(-50%);
                        width: 100px; height: 10px; display: flex; align-items: center;">
                <div style="width: 0; height: 0; border-right: 8px solid rgba(51, 51, 51, 0.2); border-top: 5px solid transparent; border-bottom: 5px solid transparent;"></div>
                <div style="flex: 1; height: 2px; background: linear-gradient(to right, rgba(51, 51, 51, 0.2) 0%, rgba(51, 51, 51, 0.15) 10%, rgba(51, 51, 51, 0.05) 40%, rgba(51, 51, 51, 0.01) 50%, rgba(51, 51, 51, 0.05) 60%, rgba(51, 51, 51, 0.15) 90%, rgba(51, 51, 51, 0.2) 100%);"></div>
                <div style="width: 0; height: 0; border-left: 8px solid rgba(51, 51, 51, 0.2); border-top: 5px solid transparent; border-bottom: 5px solid transparent;"></div>
            </div>
            <p style="font-family: 'Courier New', monospace; font-size: large; position: absolute; bottom: 0px; left: 40%; transform: translate(-45%, 50%);">No</p>
            <p style="font-family: 'Courier New', monospace; font-size: large; position: absolute; bottom: 0px; left: 60%; transform: translate(-50%, 50%);">Yes</p>`;

    const lm_slider = () => `
        <div> 
        <div style="position: absolute; left: 50%; transform: translateX(-50%); width: 320px;">
                <input type="range" class="jspsych-slider" value="50" min="5" max="95" step="15" disabled/>
                <div>
                    ${['certain', 'probably', 'guess', ' ', 'guess', 'probably', 'certain'].map((label, i) => 
                        `<div style="border: 1px solid transparent; display: inline-block; position: absolute; left:calc(${i * 16.67}% - (16.67% / 2) - ${i === 1 ? '-1.25px' : i === 2 ? '-2.5px' : i === 4 ? '2.5px' : i === 5 ? '1.25px' : '0px'}); text-align: center; width: 16.67%;"><span style="text-align: center; font-size: 80%; font-family: 'Courier New', monospace; transform: rotate(-30deg); display: inline-block;">${label}</span></div>`
                    ).join('')}
                </div>
            </div>
        </div>`;

    // LM recognition slides
    lm_recognition_slide_1 = lm_base_layout() + `
        </div>
            <p class="instruction-paragraph-left">
                <strong>Have you seen this image?</strong><br><br>
                Now we would like to know if you can still remember the images from the task before. <br><br>
                You will see images which were shown in the task before as well as some new images. <br><br>
                Please, try to remember if you have seen the image before or not.
            </p>
        </div>`;
    
    lm_recognition_slide_2 = lm_base_layout() + lm_scale_labels() + `
        </div>` + lm_slider() + `
            <p class="instruction-paragraph-left">
                <strong>Use the slider to respond</strong><br><br>
                The <strong>right side</strong> of the slider indicates that the image has been shown before (i.e. it is <strong>old</strong>).<br><br>
                The <strong>left side</strong>  means that has not been shown (i.e. it is <strong>new</strong>).
            </p>
        </div>`;

    lm_recognition_slide_3 = lm_base_layout() + lm_scale_labels() + `
        </div>` + lm_slider() + `
            <p class="instruction-paragraph-left">
                <strong>Use the slider to respond to indicate your confidence</strong><br><br>
                You have three options: <strong>guess - probably - certain</strong>.<br><br>
                Please, move the slider to the position that indicates your confidence level.
            </p>
        </div>`;

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
                        <br><br>
                        For each image we will ask if you have seen it before (i.e. during the first/second block of the experiment)
                        <br><br><br><br>
                        The following instructions will explain the task in detail.
                    </p>
                </div>`
            ], 
            lm_recognition_slide_1, 
            lm_recognition_slide_2, 
            lm_recognition_slide_3, 
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
            `<div">
                <p class="instruction-header"><strong>Starting the last task</strong></p>
                <p class="instruction-paragraph">
                    We will now start the last task of this experiment.<br><br>
                    There will be <strong>no practice</strong>, you will directly start the real task.<br><br>
                    This task will take approx. <strong>10 minutes</strong>.
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
    slider_labels = 
        [
            `<span style="font-family: 'Courier New', monospace; font-size: x-small; transform: rotate(-30deg); display: inline-block;">certain</span>`,
            `<span style="font-family: 'Courier New', monospace; font-size: x-small; transform: rotate(-30deg); display: inline-block;">probably</span>`,
            `<span style="font-family: 'Courier New', monospace; font-size: x-small; transform: rotate(-30deg); display: inline-block;">guess</span>`,
            `<span style="font-family: 'Courier New', monospace; font-size: x-small; transform: rotate(-30deg); display: inline-block;"> </span>`,
            `<span style="font-family: 'Courier New', monospace; font-size: x-small; transform: rotate(-30deg); display: inline-block;">guess</span>`,
            `<span style="font-family: 'Courier New', monospace; font-size: x-small; transform: rotate(-30deg); display: inline-block;">probably</span>`,
            `<span style="font-family: 'Courier New', monospace; font-size: x-small; transform: rotate(-30deg); display: inline-block;">certain</span>`
        ];
    var lm_timeline = [];       
    // image presentation
    lm_timeline.push(
        {
            type: jsPsychHtmlSliderResponse,
            require_movement: false, // defined later in on load
            slider_start: 50,
            slider_width: 280,
            min: 5,
            max: 95,
            step: 15,
            labels: slider_labels,
            css_classes : ["next-trial-btn"],
            stimulus: function() {
                var file = jsPsych.evaluateTimelineVariable('recognition_file')
                var html =
                    `<div style="width:900px; height:45vh; position: relative; margin: 0 auto;">
                        <p style="font-family: 'Courier New', monospace; font-size: x-large; position: absolute; top: -30px; left: 50%;
                                transform: translate(-50%, -50%); color:#4682B4; text-align: center;">
                            <strong>Have you seen this image before?</strong>
                        </p>

                        <div style="position: absolute; bottom: .6em; left: 50%; transform: translateX(-50%);
                                    width: 100px; height: 10px; display: flex; align-items: center;">
                            <div style="width: 0; height: 0; 
                                    border-right: 8px solid rgba(51, 51, 51, 0.2); 
                                    border-top: 5px solid transparent; 
                                    border-bottom: 5px solid transparent;
                                    "></div>
                            <div style="flex: 1; height: 2px; 
                                    background: linear-gradient(to right, 
                                        rgba(51, 51, 51, 0.2) 0%, 
                                        rgba(51, 51, 51, 0.15) 10%, 
                                        rgba(51, 51, 51, 0.05) 40%, 
                                        rgba(51, 51, 51, 0.01) 50%, 
                                        rgba(51, 51, 51, 0.05) 60%, 
                                        rgba(51, 51, 51, 0.15) 90%, 
                                        rgba(51, 51, 51, 0.2) 100%);"></div>
                            <div style="width: 0; height: 0; 
                                    border-left: 8px solid rgba(51, 51, 51, 0.2); 
                                    border-top: 5px solid transparent; 
                                    border-bottom: 5px solid transparent;
                                    "></div>
                        </div>

                        <p style="font-family: 'Courier New', monospace; font-size: large; position: absolute; bottom: 0px; left: 40%; 
                            transform: translate(-45%, 50%);">
                            No
                        </p>
                        <p style="font-family: 'Courier New', monospace; font-size: large; position: absolute; bottom: 0px; left: 60%;
                            transform: translate(-50%, 50%);">
                            Yes
                        </p>

                        <img src="${file}" style="position: absolute; border-radius:10px;
                                                height:200px; width:200px; top: 50%; left: 50%;
                                                transform: translate(-50%, -50%);"/>
                    </div>`

                return html;
                },
            on_load: () => {
                let moved = false;
                const slider = document.querySelector('input[type="range"]');
                const nextBtn = document.querySelector('#jspsych-html-slider-response-next');
                nextBtn.disabled = true;
                slider.addEventListener('input', () => {
                    if (parseInt(slider.value) !== 50) {
                    moved = true;
                    nextBtn.disabled = false;
                    } else {
                    moved = false;
                    nextBtn.disabled = true;
                    }
                });
            },
            on_finish: function(data) { 
                // encoding time 
                var long_encoding = jsPsych.evaluateTimelineVariable(`long_encoding`)
                if (long_encoding == 1) {
                    data.encoding_time = experimentSettings.timing.encoding_time_long
                } else if (long_encoding == 0){
                    data.encoding_time = experimentSettings.timing.encoding_time_short
                } else {
                    data.encoding_time = 9999
                }
                
                // meta data
                data.stimulus = jsPsych.evaluateTimelineVariable('recognition_file')
                data.image_id = jsPsych.evaluateTimelineVariable('recognition_id')
                data.image_old = jsPsych.evaluateTimelineVariable('old')
                data.lm_trial_id = jsPsych.evaluateTimelineVariable('trial_id')
                data.encoding_trial_id = jsPsych.evaluateTimelineVariable('encoding_trial')
                data.trial_type = "lm"
                data.phase = "recognition"
                data.timestamp = new Date().toLocaleTimeString()
            }
        }
    )
    return {timeline:lm_timeline, timeline_variables:timeline_variables};
}