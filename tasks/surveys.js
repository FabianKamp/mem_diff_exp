function createDemographics() {
    var demographics = {
        type: jsPsychSurvey,
        survey_json: {
            pages: [{
                name: 'page-1',
                elements: [
                {
                    type: "html",
                    name: "Title",
                    html: 
                        `<p style="font-size: x-large; color:#4682B4;">
                            <strong>Please fill in the questions below before we start</strong>
                        </p>`
                },
                {
                    type: 'text',
                    title: 'How old are you?', 
                    name: 'age', 
                    isRequired: true,
                    inputType: 'number',
                    min: 0,
                    max: 100,
                },
                {
                    type: 'radiogroup',
                    title: 'Which gender do you identify with?',
                    choices: ['Diverse', 'Female','Male','I prefer not to say'],
                    name: 'Gender',
                    isRequired: true
                },
                {
                    type: "panel",
                    name: "captcha",
                    elements: [
                        {
                            type: "html",
                            name: "captcha-image",
                            html: '<img src="captcha.jpg" style="width: 180px; display: block; margin: 0 0 8px 0;">'
                        },
                        {
                            type: 'text',
                            name: 'Type the word you see in the image above', 
                            isRequired: true,
                            inputType: 'text',
                        }
                    ]
                }]
            }]
        },
    };
    return demographics;
}

function createFeedbackSurvey() {
    var feedback = {
        type: jsPsychSurvey,
        survey_json: {
            completeText: "Continue",
            showQuestionNumbers: "off",
            pages: [{
                name: 'feedback-page',
                elements: [
                    {
                        type: "html",
                        name: "Title",
                        html: 
                            `<p style="font-size: x-large; color:#4682B4; text-align: center;">
                                <strong>Ending the experiment</strong>
                            </p>`
                    },
                    {
                        type: "html",
                        name: "intro",
                        html: 
                            `<p>
                                <strong>Congratulations!</strong> You have successfully completed the experiment.
                                Thank you for your time and effort in participating in our study!
                                <br>
                                Your feedback helps us to improve our research, so please feel free to share any comments or suggestions.
                            </p>`
                    },
                    {
                        type: "comment",
                        name: "feedback",
                        title: "Feel free to leave any feedback below",
                        placeholder: "e.g. did you experience any issues (technical problems, distractions etc.) during the experiment? Did you have any strategy while doing experiment?",
                        rows: 8,
                        isRequired: false
                    },
                    {
                        type: "html",
                        name: "outro",
                        html: 
                            `<p>
                                <br><br>
                                Press <strong>Continue</strong> to go to the last slide.
                                From there you will be automatically redirected to Prolific.<br>
                                <strong>Please don't close this browser tab until you're redirected to Prolific.</strong>
                                <br><br>
                            </p>`
                    },
                ]
            }]
        },
        on_finish: function(data){
            jsPsych.data.addProperties({ 
                experiment_complete: true,
                endTime: new Date().toISOString().replace('T', ' ').slice(0, 19),
            });
            data.stimulus = null
            data.trial_type = "feedback-slide"
        }
    };
    return feedback;
}