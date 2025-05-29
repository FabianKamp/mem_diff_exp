function assignValues(config){
    data = config[0]
    maxPay = data.maxPay
    maxLoss = data.maxLoss
    houseMoney = data.houseMoney
    nTrials = data.nTrials
    // }

}

config = JSON.parse(config)
assignValues(config)

language = 'DE'

url_parameters = window.location.search
url_parameters = url_parameters.split('&')
url_parameters = url_parameters.map(param => parseInt(param[param.length-1]))
url_parameters.splice(1,1)

play_DD = url_parameters[0]
play_PDG = url_parameters[1]
play_PDL = url_parameters[2]
play_MG = url_parameters[3]

instructions_dd = false       // initialized to true since tasks starts with isntructions for Delayed Discounting
instructions_pdg = false      // true when instructions for PDG currently running   
instructions_pdl = false      // true when instructions for PDL currently running
instructions_mg = false       // true when instructions for MG currently running

all_tasks = ['DD', 'PDG','PDL','MG']
tasks_to_play = [play_DD, play_PDG, play_PDL, play_MG]
tasks_to_play = all_tasks.filter((val, ind) => tasks_to_play[ind] == true)
tasks_already_played = []
lastTask = tasks_to_play[tasks_to_play.length-1]