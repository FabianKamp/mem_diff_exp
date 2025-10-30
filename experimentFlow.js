// STARTING EXPERIMENT
function startingExperiment(jsPsych) {
    var start_experiment = {timeline:[
        {
            type: jsPsychFullscreen,
            fullscreen_mode: true,
            choices: ['Continue'],
            message:         
            `
            <p class="instruction-header"><strong>Welcome to the experiment!</strong></p>
            <div style="height: 80vh; position: relative;">
                <p class="instruction-paragraph">
                    We will now enter <strong>fullscreen mode</strong>.
                    <br><br>
                    To ensure the quality of the results, we'd ask you to 
                    <br>
                    <strong>remain in fullscreen mode during the entire experiment</strong>.
                    <br><br>
                    Once the experiment is over, you will be redirected to Prolific automatically. 
                    Please, don\'t close the experiment until this happens.
                    </br><br><br>
                    To enter fullscreen mode, please click <strong>Continue</strong>.
                </p>
            </div>
            `,
            on_start: async function() {
                jsPsych.data.addProperties({ 
                    startTime: new Date().toISOString().replace('T', ' ').slice(0, 19),
                });
            },
            on_finish: function(data){
                data.stimulus = null
                data.trial_type = "fullscreen-slide"
            }
        },
        {
            type: jsPsychBrowserCheck
        }
    ]}
    return start_experiment
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
                color="#4682B4"//"#00000021"
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

// ENDING EXPERIMENT
function endingExperiment(jsPsych) {
    // end experiment
    var end_experiment = {
        type: jsPsychHtmlKeyboardResponse,
        trial_duration: 10000,
        stimulus:
            `<p><strong>End Of Experiment</strong></p><br>
            <p>Thank you for participating!</p>
            <p>Press <strong>Enter</strong> to continue to the last slide. 
            From there you will be automatically redirected to Prolific.</p>`, 
        key_forward: 'Enter',
        on_start: async function() {
            jsPsych.data.addProperties({ 
                experiment_complete: true,
                endTime: new Date().toISOString().replace('T', ' ').slice(0, 19),
            });
        },
        on_finish: function(data){
            data.stimulus = null
            data.trial_type = "end-slide"
        }
    };
    return end_experiment;
}

// COUNTDOWN
function countdown(seconds) {
    var counter = []; 
    for (let i = 0; i < seconds; i++) {
        counter.push(
        {
            type: jsPsychHtmlKeyboardResponse,
            choices: "NO_KEYS",
            trial_duration: 1000,
            record_data: false,
            stimulus: function(){
                var html = 
                    `<div style="width:250px; height:75vh;">
                        <p style="font-family: 'Courier New', monospace; font-size: 3rem; 
                                position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                                text-align: center; color: #4682B4; margin: 0; line-height: 1;">
                            <strong>${seconds-i}</strong>
                        </p>
                    </div>`
                return html;
            }
        })
    }
    return {timeline:counter}; 
}
