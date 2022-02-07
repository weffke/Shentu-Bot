import requests
import json

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
  #Fetch Inflation data
  ##elif info=="apy":
    ##response = requests.get("http://35.172.164.222:1317/minting/inflation")
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