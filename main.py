import discord
import os
import requests
import json
from discord.ext import tasks, commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
client = discord.Client(intents=intents)
token = os.environ.get('TOKEN')

warning_channel_production = os.environ.get('warning_channel_production')
warning_channel_test = os.environ.get('warning_channel_test')
resources_channel_production = os.environ.get('resources_channel_production')
bot_help_channel_production = os.environ.get('bot_help_channel_production')
production_server_id = os.environ.get('production_server_id')
admin_role_id = os.environ.get('admin_role_id')
shentu_role_id = os.environ.get('shentu_role_id')
chain_role_id = os.environ.get('chain_role_id')
admin_warning_channel_production=os.environ.get('admin_warning_channel_production')

#Fetch Data from CoinGecko
def get_CGdata(cur):
  coingecko_link = "https://api.coingecko.com/api/v3/coins/markets?vs_currency="+cur+"&ids=certik"
  response = requests.get(coingecko_link)
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
  #Fetch bonded validators
  elif info=="bonded":
    response = requests.get("http://35.172.164.222:1317/staking/validators?status=BOND_STATUS_BONDED")
  #Fetch unbonded validators
  elif info=="unbonded":
    response = requests.get("http://35.172.164.222:1317/staking/validators?status=BOND_STATUS_UNBONDED")
  #Fetch Chain info
  elif info=="network":    
    response = requests.get("http://35.172.164.222:1317/cosmos/base/tendermint/v1beta1/node_info")
  #Fetch Shield Provider info
  elif info=="shieldproviders":
    response = requests.get("http://35.172.164.222:1317/shield/providers")
  elif info=="shieldpurchases":
    response = requests.get("http://35.172.164.222:1317/shield/purchases")
  #Load data and return
  json_data = json.loads(response.text)
  return(json_data)

def get_total_supply():
  uctk_total_supply=0
  supply_data=get_Chaindata("total_supply")
  supply_dataset=supply_data['supply']
  for supply_result in supply_data['supply'] :
    if supply_result['denom']=="uctk":
      uctk_total_supply=supply_result['amount']
  return (uctk_total_supply)
  
def get_yield():
  #Get full supply data
  uctk_total_supply=get_total_supply()
  #Get staking data
  staking_data=get_Chaindata("staked")
  result_data=staking_data['result']
  uctk_bonded=result_data['bonded_tokens']
  #Get inflation data
  inflation_data=get_Chaindata("inflation")
  inflation=inflation_data['result']
  #calculate yield %
  yield_percentage=float(uctk_total_supply)/float(uctk_bonded)*float(inflation)*100
  return(yield_percentage)

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
  #set status
  discord.CustomActivity(name="-shentuhelp for info", emoji='🖥️')
  #Start the Jailed check
  jailed.start()
  #Spammer alert
  spammer.start()

  


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
  #print ("jailed test")
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
      await channel.send(":warning::warning:**Validator jailed**:warning::warning:\n""**" + str(unbinding_validator_moniker) + "** - " + str(unbinding_validator_address))
    #Append new jailed validator list 
    new_list+=unbinding_validator_address + "-"
    #Reset known variable
    known_jailed=0
  #Overwrite known jailed validators
  f = open("jail.dat", "w")
  f.write(new_list)
  f.close

@tasks.loop(seconds=900.0)
async def spammer():
  #Initialize variables
  known_spammer_name=0
  known_spammer_display_name=0
  new_name_list = ""
  new_display_name_list = ""
  #Define channel to post in
  channel = await client.fetch_channel(admin_warning_channel_production)
  #Get the template list
  f = open("spammer_templates.dat", "r")
  template_list=f.read()
  f.close()
  #Get the name list
  f = open("known_spammer_name.dat", "r")
  spammer_name_list=f.read()
  f.close()
  #Get the display name list
  f = open("known_spammer_display_name.dat", "r")
  spammer_display_name_list=f.read()
  f.close()
  #transform lists into arrays
  templates=template_list.split('-')
  spammer_names=spammer_name_list.split('_-_')
  spammer_display_names=spammer_display_name_list.split('_-_')
  #Define server
  server = client.get_guild(int(production_server_id))
  #Get all members
  member_list = server.members
  #Loop through members
  for member in member_list:
    #Check all templates
    for template in templates:
      #Check if name contains current template
      if template in member.display_name.lower():
        #Add to new list
        new_display_name_list += member.display_name + "_-_"
        #Verify if already flagged before
        for display_name in spammer_display_names:
          if  display_name == member.display_name:
            known_spammer_display_name=1
        #If not known post in channel
        if known_spammer_display_name == 0:
          await channel.send(member.display_name + " display name found")
      #Check if name contains current template
      if template in member.name.lower():
        new_name_list += member.name + "_-_"
        #Verify if already flagged before
        for name in spammer_names:
          if name == member.name:
            known_spammer_name=1
        #If not known post in channe
        if known_spammer_name == 0:
          await channel.send(member.name + " name found")
    #Reset known variables
    known_spammer_display_name=0
    known_spammer_name=0
  #write new list
  f = open("known_spammer_name.dat", "w")
  f.write(new_name_list)
  f.close      	 
  f = open("known_spammer_display_name.dat", "w")
  f.write(new_display_name_list)
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
    #Request data and convert to correct currency sign
    if currency=="eur" or currency=="€" or currency=="euro":
      currency = "eur"
      full_data=get_CGdata(currency)
      currency_sign = "€"
    elif currency=="" or currency=="usd" or currency=="$" or currency=="dollar":
      currency = "usd"
      full_data=get_CGdata(currency)
      currency_sign = "$"
    elif currency=="pound" or currency=="gbp" or currency=="£":
      currency = "gbp"
      full_data=get_CGdata(currency)
      currency_sign = "£"
    elif currency=="yen" or currency=="jpy" or currency=="¥":
      currency = "jpy"
      full_data=get_CGdata(currency)
      currency_sign = "¥"
    elif currency=="yuan" or currency=="cny" or currency=="¥":
      currency = "cny"
      full_data=get_CGdata(currency)
      currency_sign = "¥"
    elif currency=="rubles" or currency=="rub" or currency=="₽":
      currency = "rub"
      full_data=get_CGdata(currency)
      currency_sign = "₽"
    elif currency=="twd" or currency=="ntdollar" or currency=="NT$":
      currency = "twd"
      full_data=get_CGdata(currency)
      currency_sign = "NT$"
    elif currency=="idr" or currency=="rupiah" or currency=="Rp":
      currency = "idr"
      full_data=get_CGdata(currency)
      currency_sign = "Rp"
    elif currency=="won" or currency=="krw" or currency=="₩":
      currency = "krw"
      full_data=get_CGdata(currency)
      currency_sign = "₩"
    #Get price data
    price = full_data[0]['current_price']
    high =full_data[0]['high_24h']
    low = full_data[0]['low_24h']
    price_change = full_data[0]['price_change_24h']
    #Send message
    await message.channel.send( "**Current price: "+ currency_sign + str('{:,}'.format(round(float(price),2)))+ "**\n24H high: "+ currency_sign + str('{:,}'.format(round(float(high),2))) + "\n24H low: "+ currency_sign +str('{:,}'.format(round(float(low),2))) + "\n24H price change: "+ currency_sign + str('{:,}'.format(round(float(price_change),4))))
  
  #Request Staking info
  if msg.lower().startswith('-staked'):
    #Get staking data
    staking_data=get_Chaindata("staked")
    result_data=staking_data['result']
    uctk_not_bonded=result_data['not_bonded_tokens']
    uctk_bonded=result_data['bonded_tokens']
    #Get full supply data
    uctk_total_supply=get_total_supply()
    #Convert from uctk to CTK
    total_supply=int(uctk_total_supply)/1000000
    bonded=int(uctk_bonded)/1000000
    not_bonded=int(uctk_not_bonded)/1000000
    #Calculate staked %
    staked_percentage=(int(uctk_bonded)/int(uctk_total_supply))*100
    inflation_data=get_Chaindata("inflation")
    inflation=inflation_data['result']
    #Fetch yield
    yield_percentage=get_yield()
    #Send message
    await message.channel.send("Total supply: " + str('{:,}'.format(round(float(total_supply),2))) + "CTK\nBonded (staked): " + str('{:,}'.format(round(float(bonded),2)))+ "CTK \nUnbonding: " + str('{:,}'.format(round(float(not_bonded),2))) + "CTK\nStaked Percentage: "+ str('{:,}'.format(round(float(staked_percentage),2))) +"%\nYield: "+str('{:,}'.format(round(float(yield_percentage),2)))+ "%")

  #Request Total supply
  if msg.lower().startswith('-total'):
    #Get full supply data
    uctk_total_supply=get_total_supply()
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
    #Fetch yield
    yield_percentage=get_yield()
    #Send message
    await message.channel.send("Yield: " + str('{:,}'.format(round(float(yield_percentage),2)))+ "%")

  #Request staking rewards
  if msg.lower().startswith('-stakingrewards') or msg.lower().startswith('-srewards') or msg.lower().startswith('-scalc') or msg.lower().startswith('-stakingcalculator'):
    staking_rewards_error = 0
    validator_commission = 0
    try:
      validator_commission = msg.lower().split(' ')[1]
    #Use 0 commission if none is given
    except:
      staked_quantity = 0
    try:
      staked_quantity = msg.lower().split(' ')[2]
    #Use 1000CTK if none is given
    except:
      staked_quantity = 1000
    
    if int(validator_commission) > 100 or int(validator_commission) < 0 or int(staked_quantity) < 0:
      staking_rewards_error=1
    

    if staking_rewards_error == 0:
      #Fetch yield
      yield_percentage=get_yield()
      #Calculate staking rewards
      year_reward=float(staked_quantity)*(float(yield_percentage)/100)*(1-(float(validator_commission)/100))
      day_reward=year_reward/365
      month_reward=day_reward*30
      week_reward=day_reward*7
      hour_reward=day_reward/24
      #Send message
      await message.channel.send("Given data used to calculate is "+ str('{:,}'.format(round(float(staked_quantity),4))) +"CTK with a validator commission of " + str(validator_commission) + "%\nCurrent yield: " + str(round(float(yield_percentage),2)) + "%\n1 Year     : " + str('{:,}'.format(round(float(year_reward),4))) + "CTK\n30 Days : " + str('{:,}'.format(round(float(month_reward),4))) + "CTK\n7 Days    : " + str('{:,}'.format(round(float(week_reward),4))) + "CTK\n1 Day       : " + str('{:,}'.format(round(float(day_reward),4))) + "CTK\n1 Hour     : " + str('{:,}'.format(round(float(hour_reward),4))) + "CTK\n*Please note that the staking yield is variable and this is only an estimation*")
    else: 
      await message.channel.send("Bad parameters given. Please use \'command validator commission staked quantity\'.\n Example: \'-stakingcalculator 5 2500\' ")

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
    await message.channel.send("**You can find the official website at: <https://www.shentu.technology>** \n*for more useful links visit* <#"+resources_channel_production+">")
  
  #Request Whitepaper link
  if msg.lower().startswith('-whitepaper'):
    #Send message
    await message.channel.send("**You can find the whitepaper at: <https://www.shentu.technology/whitepaper>** \n*for more useful links visit* <#"+resources_channel_production+">")
  
  #Request official wallet link
  if msg.lower().startswith('-wallet') or msg.lower().startswith('-deepwallet'):
    #Send message
    await message.channel.send("**You can find Shentu's official wallet, DeepWallet at: <https://wallet.shentu.technology>** \n*for more useful links visit* <#"+resources_channel_production+">")
  
  #Request official chain explorer
  if msg.lower().startswith('-chain') or msg.lower().startswith('-explorer'):
    #Send message
    await message.channel.send("**You can find the shentu chain explorer at: <https://explorer.shentu.technology>** \n*for more useful links visit* <#"+resources_channel_production+">")
  
  #Request Shield link
  if msg.lower().startswith('-shieldinfo') or msg.lower().startswith('-shieldweb'):
    #Send message
    await message.channel.send("**You can find the whitepaper at <https://shield.shentu.technology>** \n*for more useful links visit* <#" + resources_channel_production + ">")
  
  #Request Resources links
  if msg.lower().startswith('-useful') or msg.lower().startswith('-resources') or msg.lower().startswith('-links'):
    #fetch last message info in the resources channel
    resources_last_message=(await client.get_channel(int(resources_channel_production)).history(limit=1).flatten())[0]
    #Send message
    await message.channel.send(resources_last_message.content + "\n\n You can also visit <#"+resources_channel_production+"> to see all links")
  
  #Request Github link 
  if msg.lower().startswith('-git') or msg.lower().startswith('-github'):
    #Send message
    await message.channel.send("**You can find the Shentu Github at <https://github.com/ShentuChain/>** \n*for more useful links visit* <#"+resources_channel_production+">")
  
  #Post Shentu Bot help 
  if msg.lower().startswith('-shentuhelp'):
    #fetch last 2 messages info in the Shentu-bot channel
    bot_help_second_last_message =(await client.get_channel(int(bot_help_channel_production)).history(limit=2).flatten())[1]
    bot_help_last_message =(await client.get_channel(int(bot_help_channel_production)).history(limit=2).flatten())[0]
    #Send message
    await message.channel.send(bot_help_second_last_message.content)
    await message.channel.send(bot_help_last_message.content + "\n\n You can also visit <#"+bot_help_channel_production+"> to see all commands")
  
  #Shentu bot to repeat message
  if msg.lower().startswith('-shentusay'):
    #Pick up the text
    say_text = msg.partition(' ')[2]
    #Fetch messenger
    message_author_id = message.author.id
    #Fetch server
    server = client.get_guild(int(production_server_id))
    #fetch user
    user = server.get_member(message_author_id) 
    #Fetch authorized roles
    admin_role = server.get_role(int(admin_role_id))
    shentu_role = server.get_role(int(shentu_role_id))
    chain_role = server.get_role(int(chain_role_id))
    #Init accepted
    accepted=0
    #Loop through the roles (range is a bad workaround)
    for r in range(15):
      try:
        role=user.roles[r]
        if shentu_role == role or admin_role == role or chain_role_id == role:
          accepted=1
      except:
        break
    #If the user is allowed and message isn't empty the message will be posted
    if accepted==1:
      if say_text != "":
        await message.channel.send(say_text)
 
  #Add Shentu Bot feature request
  if msg.lower().startswith('-request'):
    #Read message and get the requested feature
    try:
      requested_feature = str(msg.split(',')[1])
    except:
      await message.channel.send("Couldn't read the request please make sure to use -request ,requested feature")
    #Use USD if no currency is given
    stripped_request = requested_feature
    new_feature_request= str(stripped_request) + "-_-" 
    #Add to list 
    f = open("features.dat", "a")
    f.write(new_feature_request)
    f.close
    #Send message
    await message.channel.send("\'" + requested_feature + "\' added to the list of requested features")
    
    
  #Show Shentu Bot feature requests
  if msg.lower().startswith('-showrequests'):
    #read existing list
    f = open("features.dat", "r")
    old_list=f.read()
    f.close()
    features_message = "List of requested features: \n\n"
    requested_features=old_list.split('-_-')
    #loop through list and add to message
    for feature_request in requested_features:
      if feature_request != "":
        features_message = features_message + "-" + feature_request + "\n"
    #Send message
    await message.channel.send(features_message)
    
   
  #Show Shentu versions
  if msg.lower().startswith('-version'):
    #Get full network data
    network_data=get_Chaindata("network")
    protocol_data=network_data['default_node_info']
    application_data=network_data['application_version']
    #Send message
    protocol_version=protocol_data['network']
    application_version=application_data['app_name'] + " " + application_data['version']
    await message.channel.send("Network version: " + protocol_version + "\nValidator binary version: " + application_version )    
    
  #Show Social media links
  if msg.lower().startswith('-social'):
    
    #fetch last message info in the resources channel
    resources_last_message=(await client.get_channel(int(resources_channel_production)).history(limit=1).flatten())[0]
    #Trim to only get social media
    resources_last_message_string=resources_last_message.content
    social_media=resources_last_message_string.split("***Social Media***",1)[1] 
    #Send message
    await message.channel.send("***Social Media***" + social_media) 
    
  #Show Validator info
  if msg.lower().startswith('-validatorinfo') or msg.lower().startswith('-validators'):
    #Initialize variables
    unbonding_amount=0
    bonded_amount=0
    unbonded_amount=0
    top_voting_power=0
    #Get all data
    staking_data=get_Chaindata("staked")
    result_data=staking_data['result']
    uctk_bonded=result_data['bonded_tokens']
    uctk_not_bonded=result_data['not_bonded_tokens']
    unbonding_data=get_Chaindata("unbonding")
    bonded_data=get_Chaindata("bonded")
    unbonded_data=get_Chaindata("unbonded")
    for unbonding_validator in unbonding_data['result']:
      #Count number of unbonding validators
      unbonding_amount+=1
    for unbonded_validator in unbonded_data['result']:
      #Count number of unbonding validators
      unbonded_amount+=1   
    for bonded_validator in bonded_data['result']:
      #Count number of unbonding validators
      bonded_amount+=1
      validator_voting_power=bonded_validator['tokens'] 
      if int(top_voting_power)<int(validator_voting_power):
        top_voting_power=validator_voting_power
        top_validator=bonded_validator['operator_address']
      
    top_voting_power_percentage=float(top_voting_power)/float(uctk_bonded)*100
    #Fetch Validator data
    top_validator_data= get_validatordata(top_validator)
    #Fetch Validator moniker (name)
    top_validator_result_data=top_validator_data['result']
    top_validator_description_data=top_validator_result_data['description']
    top_validator_moniker=top_validator_description_data['moniker']
    await message.channel.send("Running validators: " + str(bonded_amount) + "\nJailed validators: " + str(unbonding_amount) + "\nUnbonded validators: " + str(unbonded_amount)+"\n\nTop validator: " + top_validator_moniker + "\nTop validator power: "+ str('{:,}'.format(round(float(top_voting_power_percentage),2))) + "%")
 
  #Show supported valuta
  if msg.lower().startswith('-valuta'):
    await message.channel.send("US Dollar : usd | Euro : eur | Great Britain Pound : gbp | Korean Won : krw | Japanese Yen : jpy | Chinese Yuan : cny | Russian Rubles : rub | Indonesian Rupiah : idr | New Taiwan Dollar : twd")    
  
  
  #Show shield info
  if msg.lower().startswith('-shield'):
    #init variables
    total_collateral=0
    total_bonded=0
    total_purchased=0
    #Get Shield data
    shield_provider_data=get_Chaindata("shieldproviders")
    shield_provider_result_data=shield_provider_data['result']
    shield_purchases_data=get_Chaindata("shieldpurchases")
    shield_purchases_result_data=shield_purchases_data['result']
    for provider in shield_provider_result_data:
      total_collateral += int(provider['collateral'])
      total_bonded += int(provider['delegation_bonded'])
    for purchase in shield_purchases_result_data:
      shield_purchases_servicefees_data=purchase['service_fees']
      print(shield_purchases_servicefees_data)
      shield_purchases_native_data=shield_purchases_servicefees_data['native']
      print(shield_purchases_native_data)
      for native in shield_purchases_native_data:
        print(native)
        print(native['amount'])
        total_purchased += float(native['amount'])
    #Convert uCTK to CTK
    total_collateral_ctk=total_collateral/1000000
    total_bonded_ctk=total_bonded/1000000
    total_purchased_ctk=total_purchased/1000000
    #Send message
    await message.channel.send("Total Collateral: " + str('{:,}'.format(round(float(total_collateral_ctk),4))) + "\nTotal bonded: " + str('{:,}'.format(round(float(total_bonded_ctk),4))) + "\nTotal Shields purchased: " + str('{:,}'.format(round(float(total_purchased_ctk),4))))    
         
 
client.run(token)

