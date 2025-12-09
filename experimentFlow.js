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
                    We'd ask you to <strong>remain in fullscreen mode during the entire experiment</strong>.
                    <br><br>
                    This experiment is time sensitive. To ensure data quality, 
                    the session will be automatically terminated if you take significantly 
                    longer than expected.
                    <br><br>
                    Once the experiment is over, you will be redirected to Prolific automatically. 
                    </br><br>
                    To enter fullscreen mode, please click <strong>Continue</strong>.
                </p>
            </div>
            `,
            on_finish: function(data){
                data.stimulus = null
                data.trial_type = "fullscreen-slide", 
                jsPsych.data.addProperties({ 
                    experimentStart: jsPsych.data.get().last(1).values()[0].time_elapsed
                });
            }
        },
        {
            type: jsPsychBrowserCheck
        }
    ]}
    return start_experiment
}

// ENDING EXPERIMENT
function endingExperiment(jsPsych) {
    // end experiment
    var end_experiment = {
        type: jsPsychHtmlKeyboardResponse,
        trial_duration: 15000,
        stimulus:
            `<div>
            <p class="instruction-header">
                <strong>Ending the experiment</strong>
            </p>
            <p class="instruction-paragraph">
                Great! You have successfully finished the experiment. 
                <br><br>
                Thank you for your time and effort in participating in our study!
                <br><br>
                Press <strong>Enter</strong> to continue to the last slide. 
                From there you will be automatically redirected to Prolific.
                <br><br>
                <strong>Please don\'t close the experiment until your redirected to Prolific.</strong>
            </p>
            <p class="continue-prompt">
                To end the experiment press <strong>Enter</strong>
            </p>
            </div>
            `, 
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

// Abort experiment if the max duration (in minutes) has been reached
function checkTime(jsPsych, max_duration) {
    var end_experiment = {
        timeline: [{
            type: jsPsychHtmlKeyboardResponse,
            trial_duration: 30000,
            stimulus:
                `<div>
                <p class="instruction-header">
                    <strong>Ending the experiment</strong>
                </p>
                <p class="instruction-paragraph">
                    Thank you for your time and effort in participating in our experiment.
                    <br><br>
                    Unfortunately, the time limit for the previous section has been exceeded,
                    so we are unable to continue with the remainder of the study.
                    <br><br>
                    Press <strong>Enter</strong> to continue to the last slide. 
                    From there you will be automatically redirected to Prolific.
                    <br><br>
                    <strong>Please don\'t close the experiment until your redirected to Prolific.</strong>
                </p>
                <p class="continue-prompt">
                    To end the experiment press <strong>Enter</strong>
                </p>
                </div>`, 
            key_forward: 'Enter',
            on_start: function() {
                jsPsych.data.addProperties({ 
                    time_limited_reached: true,
                    experiment_aborted: true,
                    experiment_complete: false,
                    abortTime: new Date().toISOString().replace('T', ' ').slice(0, 19),
                    endTime: new Date().toISOString().replace('T', ' ').slice(0, 19),
                });
            },
            on_finish: function(data){
                data.stimulus = null;
                data.trial_type = "time-check";
                jsPsych.abortExperiment('The experiment was ended because time limit was reached.');
                console.log("Time limit reached.")
            }
        }], 
        conditional_function: function() {
            var time_elapsed = jsPsych.data.get().last(1).values()[0].time_elapsed;
            time_elapsed = time_elapsed-jsPsych.data.dataProperties.experimentStart;
            
            var minutes_elapsed = time_elapsed/60e3
            console.log(
                `Time-check: Time elapsed ${Math.round(minutes_elapsed)} -- Max duration ${max_duration}`
            )
            return minutes_elapsed>max_duration
        }
    }
    return end_experiment
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
            record_data: true,
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
            }, 
            on_finish: function(data){
                data.stimulus = null;
                data.trial_type = `countdown-${i+1}`
            }
        })
    }
    return {timeline:counter}; 
}