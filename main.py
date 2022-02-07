import discord
import os

from Keep_alive import Keep_alive
from jailed_alerter import startParallelLoop
from functions import get_CGdata,get_Chaindata,get_validatordata


client = discord.Client()
token = os.environ['TOKEN']
stop_keep_alive=0


#Discord Login
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

#Read Messages
@client.event
async def on_message(message):
  if message.author == client.user:
    return
  msg = message.content




#Reply with correct answer
  
  #Request prices from CoinGecko
  if msg.lower().startswith('-price'):
    #Check for given Currency
    try:
      currency = msg.lower().split(' ')[1]
    #Use USD if no currency is given
    except:
      currency = "$"
    #Get price data
    full_data=get_CGdata(currency)
    price = full_data[0]['current_price']
    high =full_data[0]['high_24h']
    low = full_data[0]['low_24h']
    price_change = full_data[0]['price_change_24h']
    #Convert to correct currency sign
    if currency=="eur" or currency=="€" or currency=="euro":
      currency = "€"
    elif currency=="" or currency=="usd" or currency=="$":
      currency = "$"
    #Send message
    await message.channel.send( "**Current price: "+ currency + str(price)+ "**\n24H high: "+ currency + str(high) + "\n24H low: "+ currency +str(low) + "\n24H price change: "+ currency + str(price_change))
  
  #Request Staking info
  if msg.lower().startswith('-staked'):
    #Get staking data
    staking_data=get_Chaindata("staked")
    result_data=staking_data['result']
    uctk_not_bonded=result_data['not_bonded_tokens']
    uctk_bonded=result_data['bonded_tokens']
    #Get full supply data
    supply_data=get_Chaindata("total_supply")
    supply_dataset=supply_data['supply']
    uctk_total_supply=supply_dataset[2]['amount']
    #Convert from uctk to CTK
    total_supply=int(uctk_total_supply)/1000000
    bonded=int(uctk_bonded)/1000000
    not_bonded=int(uctk_not_bonded)/1000000
    #Calculate staked %
    staked_percentage=(int(uctk_bonded)/int(uctk_total_supply))*100
    inflation_data=get_Chaindata("inflation")
    inflation=inflation_data['result']
    #calculate yield
    yield_percentage=float(uctk_total_supply)/float(uctk_bonded)*float(inflation)*100
    #Send message
    await message.channel.send("Total supply: " + str('{:,}'.format(round(float(total_supply),2))) + "CTK\nBonded (staked): " + str('{:,}'.format(round(float(bonded),2)))+ "CTK \nUnbonding: " + str('{:,}'.format(round(float(not_bonded),2))) + "CTK\nStaked Percentage: "+ str('{:,}'.format(round(float(staked_percentage),2))) +"%\nYield: "+str('{:,}'.format(round(float(yield_percentage),2)))+ "%")

  #Request Total supply
  if msg.lower().startswith('-total'):
    #Get full supply data
    supply_data=get_Chaindata("total_supply")
    supply_dataset=supply_data['supply']
    uctk_total_supply=supply_dataset[2]['amount']
    #Convert from uctk to CTK
    total_supply=int(uctk_total_supply)/1000000
    #Send message
    await message.channel.send("Total supply: " + str('{:,}'.format(round(float(total_supply),2)))+"CTK")

  #Request Inflation information
  if msg.lower().startswith('-inflation'):
    #Get inflation data
    inflation_data=get_Chaindata("inflation")
    inflation=inflation_data['result']
    #Convert to percentage
    inflation_percentage=float(inflation)*100
    #Send message
    await message.channel.send("Inflation: " + str('{:,}'.format(round(float(inflation_percentage),2)))+ "%")

  #Request staking yield
  if msg.lower().startswith('-apy') or msg.lower().startswith('-yield') or msg.lower().startswith('-apr'):
    #Get full supply data
    supply_data=get_Chaindata("total_supply")
    supply_dataset=supply_data['supply']
    uctk_total_supply=supply_dataset[2]['amount']
    #Get staking data
    staking_data=get_Chaindata("staked")
    result_data=staking_data['result']
    uctk_bonded=result_data['bonded_tokens']
    #Get inflation data
    inflation_data=get_Chaindata("inflation")
    inflation=inflation_data['result']
    #calculate yield %
    yield_percentage=float(uctk_total_supply)/float(uctk_bonded)*float(inflation)*100
    #Send message
    await message.channel.send("Inflation: " + str('{:,}'.format(round(float(yield_percentage),2)))+ "%")

  #Request unbonding Validators
  if msg.lower().startswith('-jailed') or msg.lower().startswith('-unbonding'):
    #Initialize string
    unbinding_validator_list=""
    #Get unbonding validator data
    unbonding_data=get_Chaindata("unbonding")
    #Loop through all unbinding validators
    for i in unbonding_data['result']:
     #Store address of unbinding validator
     unbinding_validator_address= i['operator_address']
     #Fetch Validator data
     unbinding_validator_data= get_validatordata(unbinding_validator_address)
     #Fetch Validator moniker (name)
     unbinding_validator_result_data=unbinding_validator_data['result']
     unbinding_validator_description_data=unbinding_validator_result_data['description']
     unbinding_validator_moniker=unbinding_validator_description_data['moniker']
     #Build string to use in the message
     unbinding_validator_list+="**" + unbinding_validator_moniker + "** - " + unbinding_validator_address + "\n"   
    #Send message
    await message.channel.send(unbinding_validator_list)


Keep_alive()
startParallelLoop()
client.run(token)




