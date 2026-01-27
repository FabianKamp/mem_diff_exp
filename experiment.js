async function createTimeline(jsPsych){
    // load session/subject/wave id
    const session_id = jsPsych.data.getURLVariable('sid') ||  "M-PD-999-A"
    var [version_id, wave_id, subject_id, backup] = session_id.split('-');  
    subject_id = parseInt(subject_id, 10);

    // SETTINGS - Load and make globally accessible
    window.experimentSettings = await fetch(`input_data/${version_id}-${wave_id}/_settings.json`)
        .then(response => response.json())
        .catch(error => console.error(error));

    // Setup shortcuts for testing
    if (subject_id === 999) setupShortcuts(jsPsych);

    // add meta data
    jsPsych.data.addProperties({
        session_id : session_id,
        version_id : version_id,
        wave_id : wave_id,
        subject_id : subject_id,
        backup: backup,
        startTime : new Date().toISOString().replace('T', ' ').slice(0, 19),
        OS : window.navigator.platform,
        fullscreen_mode: true,
        experiment_complete: false
    });

    // initialize the fullscreen tracker
    fullscreen_tracker = new fullscreenTracker(jsPsych);
    
    // load data
    var input_data = await fetch(`input_data/${version_id}-${wave_id}/input_${session_id.slice(0,-2)}.json`) // excluding the trialing ABC
        .then(response => response.json())
        .catch(error => console.error(error));

    if (version_id == 'M') {
        console.log("starting memory task")

        // split data into practice, wm and lm task
        var practice_input_data = input_data.filter((trial) => trial.trial_type === "practice");
        var wm_input_data = input_data.filter((trial) => trial.trial_type === "wm" || trial.trial_type === "catch");
        var lm_input_data = input_data.filter((trial) => trial.trial_type === "lm");

        // split into blocks
        var wm_input_data_block1 = wm_input_data.filter((trial) => trial.wm_block_id === 1);
        var wm_input_data_block2 = wm_input_data.filter((trial) => trial.wm_block_id === 2);
        var wm_input_data_block3 = wm_input_data.filter((trial) => trial.wm_block_id === 3);

        // overall timeline
        var experiment_timeline = [];

        // starting
        experiment_timeline.push({
            timeline: [
                checkConsent(jsPsych, version_id),
                startingExperiment(jsPsych),
                createDemographics(),
            ],
            name: 'exp_start'
        })

        // WM instructions
        experiment_timeline.push({
            timeline: [
                checkTime(jsPsych, 15),
                botCheck(jsPsych),
                createWMInstructions()
            ],
            name: 'wm_instructions'
        })

        // WM practice
        experiment_timeline.push({
            timeline: [
                startingWMPractice(),
                fullscreen_tracker.check(),
                countdown(3),
                createWM(practice_input_data, jsPsych)
            ],
            name: 'wm_practice'
        })

        // WM block 1
        experiment_timeline.push({
            timeline: [
                startingWM(),
                fullscreen_tracker.check(),
                countdown(3),
                createWM(wm_input_data_block1, jsPsych)
            ],
            name: "wm_block_1"
        })

        // WM block 2
        experiment_timeline.push({
            timeline: [
                checkTime(jsPsych, 45),
                createBreak(label=1),
                fullscreen_tracker.check(),
                countdown(3),
                createWM(wm_input_data_block2, jsPsych),
            ],
            name: "wm_block_2"
        })

        // WM block 3
        experiment_timeline.push({
            timeline: [
                checkTime(jsPsych, 45),
                createBreak(label=2),
                fullscreen_tracker.check(),
                countdown(3),
                createWM(wm_input_data_block3, jsPsych),
            ],
            name: "wm_block_3"
        })

        // LM is not run during the piloting phase
        if ( wave_id[0] !== "P" || subject_id === 999 ) { 
            
            // LM Instructions
            experiment_timeline.push({
                timeline: [
                    checkTime(jsPsych, 45),
                    createLMInstructions()
                ],
                name: "lm_instructions"
            })

            // LM task
            experiment_timeline.push({
                timeline: [
                    startingLM(),
                    fullscreen_tracker.check(),
                    countdown(3),
                    createLM(lm_input_data, jsPsych),
                ],
                name: "lm_task"
            })
        }

        // Ending experiment
        experiment_timeline.push({
            timeline: [
                endingExperiment(jsPsych),
            ],
            name: "exp_end"
        })
    } 
    return experiment_timeline;
}

// run
async function runExperiment(jsPsych) {
    const experiment_timeline = await createTimeline(jsPsych);
    jsPsych.run(experiment_timeline)
}

