// consent

function checkConsent(jsPsych, version_id) {
    var participantConsentStatus = null;
    
    var check_consent_html = function(elem) {
        if (!document.getElementById('consent_checkbox').checked && !document.getElementById('no_consent_checkbox').checked) {
            alert("Please indicate whether you consent to participate or not.");
            return false;
        }
        if (document.getElementById('no_consent_checkbox').checked) {
            participantConsentStatus = "Participant does not consent and is redirected";
            
            // Redirect to Prolific or any other action for non-consenting participants
            window.location.href = "https://app.prolific.com/";
            return false;
        }
        participantConsentStatus = "Participant has read consent form and consents to study participation.";
        return true;
    };

    var consent = {
    type: jsPsychExternalHtml,
    url: version_id === 'M' ? 'consent/consent_page_memory.html' : 'consent/consent_page_vision.html',
    cont_btn: 'continue_button',
    check_fn: check_consent_html,
    on_finish: function() {
        // Log consent status
        jsPsych.data.get().last(1).addToAll({
            consent_status: participantConsentStatus
        })}
    }
    return consent;
}
