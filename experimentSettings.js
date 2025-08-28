// Experiment Settings - centralized configuration
const experimentSettings = {
    "memory_experiment": {
        "load": 4
    },

    "timing": {
        "inter_trial_delay": 750,
        "memory_delay": 3000,
        "catch_delay": 1000,
        "encoding_time_short": 1250,
        "encoding_time_long": 2500,
        "catch_encoding": 5000
    },

    "spatial": {
        "radius_x": 280,
        "radius_y": 240
    },

    "break": {
        "duration": 120000
    },

    "countdown": {
        "interval": 1000
    },
    
    "distractor": {
        "initial_number": 100,
        "random_min": 2,
        "random_max": 6,
        "delay_time": 1000,
        "stimulus_time": 3000,
        "feedback_timeout": 10000,
        "rounds": 3,
        "operations_per_round": 5
    }
};