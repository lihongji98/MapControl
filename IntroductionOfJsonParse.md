# Introduction of Demo json file

### Raw information
  variable data is the 
  <span style="color: cyan;">
  "raw data"
  </span>
  read from the json file.

    > data = json.load(file)

Here list the attributes in the json file:

>__important info__: \
> 'matchID' \
> 'mapName'  \
> 'matchPhases' \  
> 'playerConnections' \
>**_'gameRounds'_**  ============>  which contains the track data\
> \
> __some redundant info__: \
> 'clientName','tickRate','playbackTicks', 'playbackFramesCount','parsedToFrameIdx',
> 'parserParameters', 'serverVars','matchmakingRanks', 'chatMessages',

<br>



### __Round information__

data['gameRounds'] is a list where each element is a dictionary with the corresponding 
round information. 

    data['gameRounds'][i] ======> i_th round information  

Here list the attributes in the __*"gameRounds"*__ branch:

    > data['gameRounds'][i].keys()

> __Important info__ :\
> 'roundNum', 
> 'startTick','endTick', 'bombPlantTick',
> 'tScore', 'ctScore', 'winningTeam', 'losingTeam', 'roundEndReason',
> 'ctBuyType', 'tBuyType',\
> __'frames'__ ========> important 
> 
> __some redundant info__:\
> 'isWarmup',\
>  'freezeTimeEndTick',  'endOfficialTick',  \
>  'endTScore', 'endCTScore', \
> 'ctTeam', 'tTeam', 'winningSide', 
> 'ctFreezeTimeEndEqVal', 'ctRoundStartEqVal', 'ctRoundSpendMoney', 
> 'tFreezeTimeEndEqVal', 'tRoundStartEqVal', 'tRoundSpendMoney','ctSide', 'tSide',
> 'grenades', 'flashes', \
> 'bombEvents'， \
> 'kills', 'damages',  'weaponFires' =============> relatively long

### __Frag_info__
This is a collection which contains information of "kills".
```
data['gameRounds'][i][kills]
```


Here list the attributes in __*frag*__ branch:
>>__Important information__:\
> 'seconds', 'clockTime',  
> 'attackerName', 'attackerX', 'attackerY', 'attackerZ', 'attackerViewX', 'attackerViewY', 
> 'victimName', 'victimX', 'victimY', 'victimZ', 'victimViewX', 'victimViewY', 
> 'distance', 
> 'isFirstKill', 'isHeadshot',
> 'weapon', 'weaponClass'
> 
>__some Redundant information__:\
> 'tick', 
> 'attackerSteamID', 'attackerTeam', 'attackerSide',
> 'victimSteamID', 'victimTeam', 'victimSide',
> 'assisterSteamID', 'assisterName', 'assisterTeam', 'assisterSide', 
> 'isSuicide', 'isTeamkill', 'isWallbang', 'penetratedObjects', 
> 'victimBlinded', 'attackerBlinded', 
> 'flashThrowerSteamID', 'flashThrowerName', 'flashThrowerTeam', 'flashThrowerSide',
> 'noScope', 'thruSmoke', 
> 
> 'isTrade', 'playerTradedName', 'playerTradedTeam', 'playerTradedSteamID', 'playerTradedSide', 
> 

### __Frame_info__

```
data['gameRounds'][i]['frames'][j]              #j_th frame of i_th round
```

Here list the attributes in __*frames*__ branch:
>__Important information__:\
> 't', 'ct' \
> 'bomb',    ===============> bomb coordinate\
> 'tick', 'seconds',
> 
>__some Redundant information__:\
> 'tick'
> 'isKillFrame',  'bombPlanted', 
> 'clockTime', 'bombsite',  'projectiles', 'smokes', 'fires' \



### __player information__
```
data['gameRounds'][i]['frames'][j]['t']['player'][k]  # T side
data['gameRounds'][i]['frames'][j]['ct']['player'][k]  # CT side              
```
>__Important information__:\
> 'x', 'y', 'z', \
> 'velocityX', 'velocityY', 'velocityZ',\
> 'viewX', 'viewY', 
> 'hp', 'armor', 'hasHelmet', 'hasDefuse',
> 'activeWeapon', 
> 'flashGrenades', 'smokeGrenades', 'heGrenades', 'fireGrenades',
>  'hasBomb'
> 
>__some Redundant information__:\
> 'steamID', 'name', 'team', 'side',  'eyeX', 'eyeY','eyeZ',
> 'totalUtility', 'lastPlaceName', 'isAlive', 'isBot', 
> 'isBlinded', 'isAirborne', 'isDucking', 'isDuckingInProgress', 
> 'isUnDuckingInProgress', 'isDefusing', 'isPlanting', 'isReloading', 
> 'isInBombZone', 'isInBuyZone', 'isStanding', 'isScoped', 'isWalking', 
> 'isUnknown', 'inventory', 'spotters', 'equipmentValue', 
> 'equipmentValueFreezetimeEnd', 'equipmentValueRoundStart', 
> 'cash', 'cashSpendThisRound', 'cashSpendTotal','ping', 'zoomLevel' 

in TeamFrame:
>__Important information__:\
> 'name', \
> 'x', 'y', 'z',\
> 'velocityX', 'velocityY', 'velocityZ'\
> 'viewX', 'viewY'\
> 'hp', 'armor', 'activeWeapon', 'flashGrenades', 'smokeGrenades', 'heGrenades', 'fireGrenades',\
> 'isAlive', 'hasHelmet', 'hasDefuse'
> 
>__some Redundant information__:\
> 'steamID', 'team', 'side',
> 'eyeX', 'eyeY', 'eyeZ',
> 'viewX', 'viewY',
> 'totalUtility', 'lastPlaceName', 'isAlive',
> 'isBot', 'isBlinded',
> 'isAirborne', 'isDucking', 'isDuckingInProgress', 'isUnDuckingInProgress',
> 'isDefusing', 'isPlanting', 'isReloading', 'isInBombZone', 'isInBuyZone',
> 'isStanding', 'isScoped', 'isWalking', 'isUnknown','inventory', 'spotters', 
> 'equipmentValue', 'equipmentValueFreezetimeEnd', 'equipmentValueRoundStart', 
> 'cash', 'cashSpendThisRound', 'cashSpendTotal', 
>   'hasBomb', 'ping', 'zoomLevel'




## Database Structure Design

__Collection__: \

Team
```
[{'team': 'FaZe Clan'}, {'team': 'Team Liquid'}]
```

Player
```
 [{'name': 'ropz', 'steam_id': 76561197991272318}, ...]
```

Match
```
[{ 'matchID': 'Liquid-Faze-BLAST2022',   #can be designed by ourselves
  'mapName': 'de_mirage', 
  'team1': 'FaZe Clan', 
  'team2': 'Team Liquid'}]
```

Round 

Kill

Frame


