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

// TIMER animation
let delayID = null;
let timerId = null;
function startTimer(radius,delay,duration,top,color) {
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

function resetTimer() {
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