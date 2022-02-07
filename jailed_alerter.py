from threading import Thread
import time
from functions import get_Chaindata ,get_validatordata
import discord
import os



running=1

def mainLoop():
  print("Started main loop on thread")
  unbinding_validator_alert_list=""
  f = open("jail.dat", "w")
  lines = f.readlines()
  newlist = ""
  while running==1:
  
    unbonding_data=get_Chaindata("unbonding")
    for i in unbonding_data['result']:
      #Store address of unbinding validator
      unbinding_validator_address= i['operator_address']
      newlist+=unbinding_validator_address
      for x in lines:
       jailed_address=f.readline(x)
      if unbinding_validator_address == jailed_address:
        break
      else:
        #Fetch Validator data
        unbinding_validator_data= get_validatordata(unbinding_validator_address)
        #Fetch Validator moniker (name)
        unbinding_validator_result_data=unbinding_validator_data['result']
        unbinding_validator_description_data=unbinding_validator_result_data['description']
        unbinding_validator_moniker=unbinding_validator_description_data['moniker']
        discord.Message.(":warning::warning:**Validator jailed**:warning::warning:\n""**" + unbinding_validator_moniker + "** - " + unbinding_validator_address + "\n @Validator")
     #Build string to use in the message
    f.close
    print(unbinding_validator_alert_list)
    time.sleep(5)
  else:
    print("Canceled the main Loop on thread ")

def startParallelLoop():
  
  t2 = Thread(target=mainLoop, daemon=True)
  t2.start()

