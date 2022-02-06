import discord
import os
import requests
import json
from Keep_alive import Keep_alive

client = discord.Client()
token = os.environ['TOKEN']

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

#Fetch Data from Shentu Chain
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
  #Load data and return
  json_data = json.loads(response.text)
  return(json_data)

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
    #Send message
    await message.channel.send("Total supply: " + str('{:,}'.format(round(float(total_supply),2))) + "\nBonded (staked): " + str('{:,}'.format(round(float(bonded),2)))+ "CTK \nUnbonded: " + str('{:,}'.format(round(float(not_bonded),2))) + "CTK\nStaked Percentage: "+ str('{:,}'.format(round(float(staked_percentage),2))) +"%")

  #Request Total supply
  if msg.lower().startswith('-total'):
    #Get full supply data
    supply_data=get_Chaindata("total_supply")
    supply_dataset=supply_data['supply']
    uctk_total_supply=supply_dataset[2]['amount']
    #Convert from uctk to CTK
    total_supply=int(uctk_total_supply)/1000000
    #Send message
    await message.channel.send("Total supply: " + str('{:,}'.format(round(float(total_supply),2))))

  #Request Inflation information
  if msg.lower().startswith('-inflation'):
    #Get full supply data
    inflation_data=get_Chaindata("inflation")
    inflation=inflation_data['result']
    #Convert to percentage
    inflation_percentage=float(inflation)*100
      #Send message
    await message.channel.send("Inflation: " + str('{:,}'.format(round(float(inflation_percentage),2)))+ "%")
Keep_alive()
client.run(token)

