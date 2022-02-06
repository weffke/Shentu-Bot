import discord
import os
import requests
import json
from Keep_alive import Keep_alive

client = discord.Client()
token = os.environ['TOKEN']

#Fetch Data
def get_data(cur):
  if cur=="eur" or cur=="€" or cur=="euro":
    response = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&ids=certik")
  elif cur=="" or cur=="usd" or cur=="$":
    response = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=certik")
  json_data = json.loads(response.text)
  return(json_data)

#Discord Login
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
#Read Messages
async def on_message(message):
  if message.author == client.user:
    return
  msg = message.content

#Reply with correct answer
  if msg.lower().startswith('-price'):
    try:
      currency = msg.lower().split(' ')[1]
    except:
      currency = "$"
    full_data=get_data(currency)
    price = full_data[0]['current_price']
    high =full_data[0]['high_24h']
    low = full_data[0]['low_24h']
    price_change = full_data[0]['price_change_24h']
    if currency=="eur" or currency=="€" or currency=="euro":
      currency = "€"
    elif currency=="" or currency=="usd" or currency=="$":
      currency = "$"

    await message.channel.send( "**Current price: "+ currency + str(price)+ "**\n24H high: "+ currency + str(high) + "\n24H low: "+ currency +str(low) + "\n24H price change: "+ currency + str(price_change))




Keep_alive()
client.run(token)

