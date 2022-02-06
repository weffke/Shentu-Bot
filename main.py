import discord
import os
import requests
import json
from Keep_alive import Keep_alive

client = discord.Client()
token = os.environ['TOKEN']

#Fetch Data
def get_data():
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
  if msg.startswith('-price'):
    full_data=get_data()
    price = full_data[0]['current_price']
    high =full_data[0]['high_24h']
    low = full_data[0]['low_24h']
    price_change = full_data[0]['price_change_24h']
    await message.channel.send( "**Current price: $" + str(price)+ "**\n24H high: $" + str(high) + "\n24H low: $" +str(low) + "\n24H price change: $" + str(price_change))




Keep_alive()
client.run(token)

