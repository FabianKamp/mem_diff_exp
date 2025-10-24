// DISTRACTOR INSTRUCTIONS
function createDistractorInstructions() {
    // distractor instructions 
    var distractor_instructions = {
        type: jsPsychInstructions,
        show_clickable_nav: false,
        key_forward: 'Enter',
        record_data: false,
        post_trial_gap: 200,
        trial_duration: 120000,
        min_viewing_time: 3000, 
        pages:[[
            `<div>
                <p class="instruction-header">
                    <strong>Instructions</strong>
                </p>
                <p class="instruction-paragraph"> 
                    We will now ask you to do some <strong>basic mental math</strong> for ~2 minutes.<br><br>
                    We'd ask you to sequentially <strong>substract numbers from 100</strong><br>
                    <em>(e.g. 100-3=97 <span style="font-size:x-large;">&#8594;</span> 97-5=92 
                        <span style="font-size:x-large;">&#8594;</span> 92-3=89 ... )</em>.
                    <br><br>
                    You will see each number for <strong>3 seconds</strong> and then the 
                    task will automatically move forward to the next number.

                </p>
                <p class="continue-prompt">
                    To start press <strong>Enter</strong>
                </p>
            </div>`
        ]],
    }
    return distractor_instructions
}

// DISTRACTOR TASK
function createDistractorTask() {  
    var initial_number = 100; 
    var dt_timeline = [];    
    dt_timeline.push(
        {
        type: jsPsychHtmlKeyboardResponse, 
        choices: "NO_KEYS",
        record_data: false,
        stimulus: 
            `<div>
                <p class="instruction-paragraph" style="top:48%; text-align: center;"> 
                    The initial number is <strong>${initial_number}</strong>.
                </p>
            </div>`,
        choices: ['Enter'],
        trial_duration: 3000,
        response_ends_trial: true,
        }
    );
    var total = initial_number;
    for (let j = 0; j < 4; j++) {
        var rounds = j == 0 ? 3 : 5;
        for (let i = 0; i < rounds; i++) {
            // delay            
            dt_timeline.push(
            {
                type: jsPsychHtmlKeyboardResponse,
                choices: "NO_KEYS",
                trial_duration: 1000, //ms
                record_data: false,
                stimulus: function(){
                    var html = 
                    `<div style="width:250px; height:75vh;">
                        <div class="cross"><div class="cross-vertical"></div><div class="cross-horizontal"></div></div>
                    </div>`
                return html;
                }
            }); 
            
            let randomInteger = Math.floor(Math.random() * 5) + 2;
            // substract number
            dt_timeline.push(
            {
                type: jsPsychHtmlKeyboardResponse,
                choices: "NO_KEYS",
                record_data: false,
                trial_duration: 3000, //ms
                stimulus: function(){
                    total -= randomInteger;
                    var html = 
                    `<div>
                        <p class="instruction-paragraph" style="top:48%; text-align: center"> 
                            <strong>Substract ${randomInteger}</strong> from the previous number.</p>
                    </div>`
                    return html}
            })           
        };
        // which is the current number?
        dt_timeline.push(
        {
            type: jsPsychSurveyText,
            trial_duration: 20000, 
            questions: [{prompt: `
                <p style="font-family: 'Courier New', monospace; font-size: x-large; color:#4682B4; ">
                    What is the current number?
                </p>
                `, 
                required: true
            }],
            on_finish: function(data) {
                data.trial_type = "distractor-task";
                data.correct_response = total;
                data.stimulus = null
                data.timestamp = new Date().toLocaleTimeString();
            }
        })
        
        if (j == 2) {
            continue;
        }
        // continue substracting
        dt_timeline.push(
            {
                type: jsPsychHtmlKeyboardResponse,
                choices: ['Enter'],
                record_data:false,
                trial_duration: 10000,
                stimulus: function(){
                    if (parseInt(jsPsych.data.get().last(1).values()[0].response["Q0"], 10) === total) {
                        var feedback = `Awesome, that was the correct number!`
                    } else {
                        var feedback = `Almost, the correct number was <strong>${total}</strong>.`
                    }

                    var html = 
                    `<div>
                        <p class="instruction-paragraph"> 
                            ${feedback}<br><br>
                            <strong>Please continue from ${total}</strong>.
                        </p>
                        <p class="continue-prompt">
                            To continue press <strong>Enter</strong>
                        </p>
                    </div>`
                    return html;
                }
            })
    };
    return {timeline:dt_timeline};
}
