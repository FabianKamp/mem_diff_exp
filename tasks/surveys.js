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
                }]
            }]
        }
    };
    return demographics;
}

function createCaptcha() {
    const captchas = [
        { image: 'captcha/captcha1.jpg', answer: 'u4f3e' },
        { image: 'captcha/captcha2.jpg', answer: '5rm2m' },
        { image: 'captcha/captcha3.jpg', answer: '3nd9i' },
        { image: 'captcha/captcha4.jpg', answer: '65idi' },
        { image: 'captcha/captcha5.jpg', answer: 'm7f2f' }
    ];
    
    let currentIndex = 0;
    let showError = false;
    let failedAttempts = 0;

    const captchaTrial = {
        type: jsPsychSurvey,
        survey_json: function() {
            return {
                pages: [{
                    name: 'captcha-page',
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
                            type: "html",
                            name: "captcha-image",
                            html: `<img src="${captchas[currentIndex].image}" style="width: 180px; display: block; margin: 0 0 8px 0;">`
                        },
                        {
                            type: 'text',
                            title: 'Type the code you see in the image above',
                            name: 'captcha_input',
                            isRequired: true,
                            inputType: 'text',
                        },
                        {
                            type: "html",
                            name: "captcha-error",
                            html: showError
                                ? `<p style="color: red;">Incorrect. Try again.</p>`
                                : ''
                        }
                    ]
                }]
            };
        }, 
        on_finish: function(data){
            data.trial_type = "captcha-check";
        }
    };

    const captchaProcedure = {
        timeline: [captchaTrial],
        loop_function: function(data) {
            const response = data.values()[0].response;
            const userAnswer = response.captcha_input?.toLowerCase().trim();
            const correctAnswer = captchas[currentIndex].answer.toLowerCase();

            if (userAnswer !== correctAnswer) {
                failedAttempts++;
                if (failedAttempts >= 5) {
                    return false; 
                }
                currentIndex = (currentIndex + 1) % captchas.length;
                showError = true;
                return true;
            }
            return false;
        }
    };

    const captchaFailure = {
        timeline: [{
            type: jsPsychHtmlKeyboardResponse,
            trial_duration: 30000,
            stimulus:
                `<div>
                <p class="instruction-header">
                    <strong>Aborting the experiment</strong>
                </p>
                <p class="instruction-paragraph">
                    The captcha was entered incorrectly too many times, so the experiment has been aborted.
                    <br><br>
                    Press <strong>Enter</strong> to continue to the last slide.
                    From there you will be automatically redirected to Prolific.
                    <br><br>
                    <strong>Please do not close this page until you are redirected.</strong>
                </p>
                <p class="continue-prompt">
                    To end the experiment press <strong>Enter</strong>
                </p>
                </div>`,
            choices: ['enter'],
            on_start: function() {
                jsPsych.data.addProperties({
                    captcha_check: 'failed',
                    experiment_aborted: true,
                    experiment_complete: false,
                    abortTime: new Date().toISOString().replace('T', ' ').slice(0, 19),
                    endTime: new Date().toISOString().replace('T', ' ').slice(0, 19),
                });
            },
            on_finish: function(data){
                data.stimulus = null;
                data.trial_type = "captcha-check";
                jsPsych.abortExperiment('The experiment was aborted because captcha was entered incorrectly.');
                console.log('Aborting')
            },
        }],
        conditional_function: function() {
            return failedAttempts >= 5;
        }
    };

    return { timeline: [captchaProcedure, captchaFailure] };
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