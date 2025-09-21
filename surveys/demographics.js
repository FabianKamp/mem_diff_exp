function createDemographics() {
    var demographics = {
        type: jsPsychSurvey,
        survey_json: {
            pages: [{
                name: 'page1',
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
                // {
                //     type: 'text',
                //     title: 'Paste your Prolific ID below', 
                //     name: 'prolificID', 
                //     isRequired: true,
                //     inputType: 'text',
                // },
                ]
            }] 
        }};
    return demographics;
}