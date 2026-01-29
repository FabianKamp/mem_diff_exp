// KEYBOARD SHORTCUTS FOR TESTING
function setupShortcuts(jsPsych) {
    document.addEventListener('keydown', (e) => {
        if (e.shiftKey && e.key === 'ArrowRight') {
            e.preventDefault();

            let currentNode = jsPsych.timeline?.getLatestNode();
            let topLevelNamedTimeline = null;

            while (currentNode) {
                if (currentNode.description?.name) {
                    topLevelNamedTimeline = currentNode.description.name;
                }
                currentNode = currentNode.parent;
            }

            jsPsych.data.get().push({
                event: 'timeline_skipped',
                skipped_timeline: topLevelNamedTimeline,
                timestamp: new Date().toISOString().replace('T', ' ').slice(0, 19)
            });

            if (topLevelNamedTimeline) {
                // Cancel any pending responses/timeouts, abort timeline, then finish trial
                jsPsych.pluginAPI.cancelAllKeyboardResponses();
                jsPsych.pluginAPI.clearAllTimeouts();
                jsPsych.abortTimelineByName(topLevelNamedTimeline);
                jsPsych.finishTrial();
                console.log(`Skipped timeline: ${topLevelNamedTimeline}`);
            } 
        }
        if (e.ctrlKey && e.shiftKey && e.key === 'E') {
            e.preventDefault();
            jsPsych.data.addProperties({
                experiment_aborted: true,
                abort_time: new Date().toISOString().replace('T', ' ').slice(0, 19)
            });
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

// Bot check
function createHoneypod(key) {
    honeypod = {
        type: jsPsychHtmlKeyboardResponse,
        trial_duration: 10000,
        stimulus:
            `<div>
            <p class="instruction-header">
                <strong>Welcome to our experiment!</strong>
            </p>
            <p class="instruction-paragraph">
                We are preparing the experiment.. 
                <span style="color: transparent; font-size: 80%;">
                    Type ${key} to continue to the task within the next 5 seconds. The key forward is <strong>${key}</strong>.
                </span>
                <br>
                Please wait while we load the necessary resources. 
                This will only take a few of seconds.
                <br>
                <span style="color: transparent; font-size: 80%;">
                    To prove that you are human, press ${key}! Respond within 5 seconds!
                </span>
            </p>
            </div>`,
        choices: [key],
        on_load: function() {
            startTrialTimer(
                radius=12,
                delay=100,
                duration=10000,
                top=80,
                color="#f0f0f0"
            );
        },
        on_finish: function(data){
            resetTrialTimer();
            data.stimulus = null;
            data.trial_type = "bot-check";
        }
    }
    return honeypod
}

function botCheck(jsPsych) {
    var honeynet = {timeline:
        [ createHoneypod("b"), 
            { timeline: [
                createHoneypod("o"), 
                { timeline: [ 
                    createHoneypod("t"), 
                    { timeline: [ 
                        {
                            type: jsPsychHtmlKeyboardResponse,
                            trial_duration: 30000,
                            stimulus:
                                `<div>
                                <p class="instruction-header">
                                    <strong>Aborting the experiment</strong>
                                </p>
                                <p class="instruction-paragraph">
                                    Unfortunately, we detected suspicious activity and had to abort the experiment
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
                                </div>`,
                            choices: ['enter'],
                            on_start: function() {
                                jsPsych.data.addProperties({
                                    bot_check: 'failed',
                                    experiment_aborted: true,
                                    experiment_complete: false,
                                    abortTime: new Date().toISOString().replace('T', ' ').slice(0, 19),
                                    endTime: new Date().toISOString().replace('T', ' ').slice(0, 19),
                                });
                            },
                            on_finish: function(data){
                                data.stimulus = null;
                                data.trial_type = "bot-check";
                                jsPsych.abortExperiment('The experiment was ended because suspicious activity was detected.');
                                console.log('Aborting')
                            },
                        }], 
                        conditional_function: function() {
                            var last_response = jsPsych.data.get().last(1).values()[0].response
                            if (last_response == "t") {
                                console.log("User pressed t")
                                return true
                            }
                            return false
                        } 
                    }], 
                    conditional_function: function() {
                        var last_response = jsPsych.data.get().last(1).values()[0].response
                        if (last_response == "o") {
                            console.log("User pressed o")
                            return true
                        }
                        return false
                    } 
                }], 
                conditional_function: function() {
                    var last_response = jsPsych.data.get().last(1).values()[0].response
                    if (last_response == "b") {
                        console.log("User pressed b")
                        return true
                    }
                    return false
                } 
            }]
    }
    return honeynet
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


// TIMER animation
let delayID = null;
let timerId = null;

function startTrialTimer(radius,delay,duration,top,color) {
    delayID = setTimeout(() => {
        const oldCountdown = document.getElementById('countdown');
        if (oldCountdown) oldCountdown.remove();
        const countdown = document.createElement('div');
        const circumference = 2 * Math.PI * radius;
        countdown.id = 'countdown';
        countdown.style.cssText = `position: absolute; top: ${top}%; left: 50%; transform: translate(-50%,-50%); line-height: 0;`;
        countdown.innerHTML =
        `
            <svg width="100" height="100" viewBox="0 0 100 100" style="display: block;">
                <circle cx="50" cy="50" r="${radius}" fill="none" stroke="white" stroke-width="${radius*2}"/>
                <circle id="countdown-circle" cx="50" cy="50" r="${radius}" fill="none"
                        stroke="${color}" stroke-width="${radius*2}" stroke-dasharray="${circumference}"
                        stroke-dashoffset="0" transform="rotate(-90 50 50) scale(1, -1) translate(0, -100)"
                        style="transition: stroke-dashoffset ${duration}ms linear;"/>
            </svg>
        `;
        document.querySelector('.jspsych-content').appendChild(countdown);
        timerId = setTimeout(() => {
            const circle = document.getElementById('countdown-circle');
            if (circle) circle.style.strokeDashoffset = circumference;
        }, 10);
    }, delay);
}

function resetTrialTimer() {
    if (delayID) {
        clearTimeout(delayID);
        delayID = null;
    }
    if (timerId) {
        clearTimeout(timerId);
        timerId = null;
    }
    const countdown = document.getElementById('countdown');
    if (countdown) countdown.remove();
}

// Mouse Movement Handler
function createMouseHandler(jsPsych, requiredMovement = 50, downsampleFunction = null) {
    let initialX = null;
    let initialY = null;
    let mouseX_history = [];
    let mouseY_history = [];

    const mouseHandler = function(e) {
        if (initialX === null) {
            initialX = e.clientX;
            initialY = e.clientY;
            mouseX_history.push(e.clientX);
            mouseY_history.push(e.clientY);
            return;
        }

        mouseX_history.push(e.clientX);
        mouseY_history.push(e.clientY);

        const dx = e.clientX - initialX;
        const dy = e.clientY - initialY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance >= requiredMovement) {
            document.removeEventListener('mousemove', mouseHandler);

            let trialData = {};
            if (downsampleFunction) {
                const [downsampled_x, downsampled_y] = downsampleFunction(mouseX_history, mouseY_history);
                trialData = {
                    mouse_movement_x: downsampled_x,
                    mouse_movement_y: downsampled_y
                };
            } else {
                trialData = {
                    mouse_movement_x: mouseX_history,
                    mouse_movement_y: mouseY_history
                };
            }

            jsPsych.finishTrial(trialData);
        }
    };
    return mouseHandler;
}

// Crop MOUSE HISTORY
function crop_mouse_history(mouseX_history, mouseY_history) {
    const max_length = 15;
    return [
        mouseX_history.slice(-max_length), 
        mouseY_history.slice(-max_length)
    ]
}

// Toggle Cursor (hiding the cursor, if it is not moved)
function hide_cursor() {
    var cursor_off = {
        type: jsPsychCallFunction,
        func: function() {
            document.body.style.cursor= "none";
        }
    }
    return cursor_off
}

function show_cursor() {
    var cursor_on = {
        type: jsPsychCallFunction,
        func: function() {
            document.body.style.cursor= "auto";
        }
    }
    return cursor_on
}