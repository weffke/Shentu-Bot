import discord
import os
import requests
import json
from discord.ext import tasks, commands
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()
token = os.environ.get('TOKEN')
warning_channel_production="940694796274663445"
warning_channel_test="933479922402484224"

#Fetch Data from CoinGecko
def get_CGdata(cur):
  #Fetch Euro data
  if cur=="eur" or cur=="€" or cur=="euro":
    response = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&ids=certik")
  #Fetch USD data
  elif cur=="" or cur=="usd" or cur=="$":
    response = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=certik")
  #Load data and return
  json_data = json.loads(response.text)
  return(json_data)

#Fetch chain Data from Shentu Chain
def get_Chaindata(info):
  #Fetch Staking data
  if info=="staked":
    response = requests.get("http://35.172.164.222:1317/staking/pool")
  #Fetch Total supply data
  elif info=="total_supply":
    response = requests.get("http://35.172.164.222:1317/cosmos/bank/v1beta1/supply")
  #Fetch Inflation data
  elif info=="inflation":
    response = requests.get("http://35.172.164.222:1317/minting/inflation")
  #Fetch unbonding validators
  elif info=="unbonding":
    response = requests.get("http://35.172.164.222:1317/staking/validators?status=BOND_STATUS_UNBONDING")
  #Load data and return
  json_data = json.loads(response.text)
  return(json_data)

#Fetch validator Data from Shentu Chain
def get_validatordata(validator_address):
  #Fetch Validator data for the given address
  response = requests.get("http://35.172.164.222:1317/staking/validators/" + validator_address)
  json_data = json.loads(response.text)
  return(json_data)


#Discord Login
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  #Start the Jailed check
  jailed.start()
  


@tasks.loop(seconds=30.0)
async def jailed():
  #Initialize variable
  known_jailed=0
  new_list = ""
  #Define channel to post in
  channel = await client.fetch_channel(warning_channel_production)
  #Read the known jailed validators
  f = open("jail.dat", "r")
  old_list=f.read()
  f.close()
  #Make a list of known jailed addresses by splitting the jail.dat file content
  known_jailed_addresses=old_list.split('-')
  #Fetch full list of jailed validators
  unbonding_data=get_Chaindata("unbonding")
  for i in unbonding_data['result']:
    #Store address of unbinding validator for this loop
    unbinding_validator_address= i['operator_address']
    #loop through the known addresses to verify if it is a new one
    for jailed_address in known_jailed_addresses:
      if unbinding_validator_address == jailed_address:
        known_jailed=1
    #If jailed validator isn't known yet post in channel (skip if already known)
    if known_jailed==0:
      #Fetch Validator data
      unbinding_validator_data= get_validatordata(unbinding_validator_address)
      #Fetch Validator moniker (name)
      unbinding_validator_result_data=unbinding_validator_data['result']
      unbinding_validator_description_data=unbinding_validator_result_data['description']
      unbinding_validator_moniker=unbinding_validator_description_data['moniker']
      #Send message
      await channel.send(":warning::warning:**Validator jailed**:warning::warning:\n""**" + unbinding_validator_moniker + "** - " + unbinding_validator_address)
    #Append new jailed validator list 
    new_list+=unbinding_validator_address + "-"
  #Overwrite known jailed validators
  f = open("jail.dat", "w")
  f.write(new_list)
  f.close

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
  
  #Request shentu site link
  if msg.lower().startswith('-site'):
    #Send message
    await message.channel.send("**You can find the official website at: <https://www.shentu.technology>** \n*for more useful links visit* #resources")
  
  #Request Whitepaper link
  if msg.lower().startswith('-whitepaper'):
    #Send message
    await message.channel.send("**You can find the whitepaper at: <https://www.shentu.technology/whitepaper>** \n*for more useful links visit* #resources")
  
  #Request official wallet link
  if msg.lower().startswith('-wallet') or msg.lower().startswith('-deepwallet'):
    #Send message
    await message.channel.send("**You can find Shentu's official wallet, DeepWallet at: <https://wallet.shentu.technology>** \n*for more useful links visit* #resources")
  
  #Request official chain explorer
  if msg.lower().startswith('-chain') or msg.lower().startswith('-explorer'):
    #Send message
    await message.channel.send("**You can find the shentu chain explorer at: <https://explorer.shentu.technology>** \n*for more useful links visit* #resources")
  
  #Request Shield link
  if msg.lower().startswith('-shieldinfo') or msg.lower().startswith('-shieldweb'):
    #Send message
    await message.channel.send("**You can find the whitepaper at <https://shield.shentu.technology>** \n*for more useful links visit* #resources")
  
  #Request Resources link
  if msg.lower().startswith('-useful') or msg.lower().startswith('-resources') or msg.lower().startswith('-links'):
    #Send message
    f = open("resources.msg", "r")
    resources_text=f.read()
    f.close()
    await message.channel.send(resources_text)
  
  #Request Resources link
  if msg.lower().startswith('-setuseful'):
    new_resources_text = msg.partition(' ')[2]
    f = open("resources.msg", "w")
    f.write(new_resources_text)
    f.close
    

  
    
client.run(token)

