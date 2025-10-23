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
function createBreak() {
    // break
    var break_trial = {
        type: jsPsychHtmlKeyboardResponse, 
        stimulus: 
            `<div>
                <p class="instruction-header"><strong>Break</strong></p>
                <p class="instruction-paragraph"> 
                    If you need a break, you can take one now.<br><br>
                    Please allow yourself a maximum of <strong>2 minutes</strong>.<br>
                    Press <strong>enter</strong> to continue.<br><br>
                    <strong>The task will continue automatically after 2 minutes.</strong>
                </p>
                <p class="continue-prompt">
                    To continue press <strong>Enter</strong>
                </p>
            </div>`,
        choices: ['Enter'],
        trial_duration: 120000, // 2 minutes
        response_ends_trial: true,
        on_finish: function(data) {
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

// KEYBOARD SHORTCUTS FOR TESTING
function setupShortcuts(jsPsych) {
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && e.key === 'S') {
            e.preventDefault();
            jsPsych.data.get().push({
                event: 'timeline_skipped',
                timestamp: new Date().toISOString().replace('T', ' ').slice(0, 19)
            });
            // First finish the current trial to clean up properly, then abort timeline
            jsPsych.finishTrial();
            // Use setTimeout to ensure finishTrial completes before aborting
            setTimeout(() => {
                jsPsych.abortCurrentTimeline();
            }, 0);
            console.log("Section skipped with keyboard shortcut")
        }

        if (e.ctrlKey && e.altKey && e.shiftKey && e.key === 'E') {
            e.preventDefault();
            jsPsych.data.addProperties({
                experiment_aborted: true,
                abort_time: new Date().toISOString().replace('T', ' ').slice(0, 19)
            });
            jsPsych.finishTrial();
            jsPsych.abortExperiment('Experiment ended by keyboard shortcut');
            console.log("Experiment ended by keyboard shortcut")

        }
    });
}

// FULLSCREEN Tracker
class fullscreenTracker {
    constructor(jsPsych) {
        this.jsPsych = jsPsych;
        this.fullscreenExits = 0;
        this.reenterScreen = this.createReenterScreen();
    }

    createReenterScreen() {
        return {
            type: jsPsychFullscreen,
            fullscreen_mode: true,
            message: `
                <p class="instruction-header"><strong>Reenter fullscreen mode</strong></p>
                <div style="height: 80vh; position: relative;">
                    <p class="instruction-paragraph">
                        We detected that you exited the fullscreen mode.<br><br>
                        To ensure the quality of the results, we'd kindly ask you to <strong>remain in fullscreen mode</strong> for the duration of the experiment.<br><br>
                        Once the experiment is over, you will automatically be redirected to Prolific, so please don\'t close the experiment until this happens.</br><br><br>
                        To reenter fullscreen mode and <span>continue</span>, please click <span style="font-style: italic;">Continue</span>.
                    </p>
                </div>
            `,
            delay_after: 1000
        };
    }

    check() {
        return {
            timeline: [this.reenterScreen],
            conditional_function: () => {
                const interactionData = this.jsPsych.data.getInteractionData();
                const currentExitCount = interactionData.filter({event: 'fullscreenexit'}).count();
                if (this.fullscreenExits < currentExitCount) {
                    this.fullscreenExits = currentExitCount;
                    // Log the fullscreen exit event
                    this.jsPsych.data.get().push({
                        fullscreen_exit_detected: true,
                        exit_count: this.fullscreenExits,
                        timestamp: new Date().toLocaleTimeString()
                    });
                    return true;
                } else {
                    return false;
                }
            }
        };
    }
}