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
        type: jsPsychSurveyText,
        questions: [
            {
                prompt: 'Please give us feedback!', 
                placeholder: "e.g. did you experience any issues (technical problems, distractions etc.) during the experiment? Did you have any strategy while working on the tasks?",
                rows: 15,
            }
        ]
    }
    return feedback;
}