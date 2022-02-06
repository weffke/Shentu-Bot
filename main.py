import discord
import os
import requests
import json
from Keep_alive import Keep_alive

client = discord.Client()
token = os.environ['TOKEN']

#Fetch Data from CoinGecko
def get_CGdata(cur):
  if cur=="eur" or cur=="€" or cur=="euro":
    response = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&ids=certik")
  elif cur=="" or cur=="usd" or cur=="$":
    response = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=certik")
  json_data = json.loads(response.text)
  return(json_data)

def get_Chaindata(info):
  if info=="staked":
    response = requests.get("http://35.172.164.222:1317/staking/pool")
  elif info=="total_supply":
    response = requests.get("http://35.172.164.222:1317/cosmos/bank/v1beta1/supply")
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
    try:
      currency = msg.lower().split(' ')[1]
    except:
      currency = "$"
    full_data=get_CGdata(currency)
    price = full_data[0]['current_price']
    high =full_data[0]['high_24h']
    low = full_data[0]['low_24h']
    price_change = full_data[0]['price_change_24h']
    if currency=="eur" or currency=="€" or currency=="euro":
      currency = "€"
    elif currency=="" or currency=="usd" or currency=="$":
      currency = "$"

    await message.channel.send( "**Current price: "+ currency + str(price)+ "**\n24H high: "+ currency + str(high) + "\n24H low: "+ currency +str(low) + "\n24H price change: "+ currency + str(price_change))
  
  #Request Staking info
  if msg.lower().startswith('-staked'):
    staking_data=get_Chaindata("staked")
    result_data=staking_data['result']
    uctk_not_bonded=result_data['not_bonded_tokens']
    uctk_bonded=result_data['bonded_tokens']
    bonded=int(uctk_bonded)/1000000
    not_bonded=int(uctk_not_bonded)/1000000
    supply_data=get_Chaindata("total_supply")
    supply_dataset=supply_data['supply']
    uctk_total_supply=supply_dataset[2]['amount']
    total_supply=int(uctk_total_supply)/1000000
    staked_percentage=(int(bonded)/int(total_supply))*100
    await message.channel.send("Total supply: " + str(total_supply) + "\nBonded (staked): " + str(bonded)+ "CTK \nUnbonded: " + str(not_bonded) + "CTK\nStaked Percentage:"+ str(staked_percentage) +"%")



Keep_alive()
client.run(token)

