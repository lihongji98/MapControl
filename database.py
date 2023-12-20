from mongoengine.fields import *
import mongoengine as meng


class Team(meng.DynamicDocument):
    team = StringField(required=True, unique=True)

    meta = {
        'db_alias': 'default'
    }


class Match(meng.DynamicDocument):
    series = StringField(required=True, unique=True)
    mapName = StringField()
    teamWin = StringField(required=True)
    teamLose = StringField(required=True)

    meta = {
        'indexes': ['Series', 'teamWin', 'teamLose'],
        'db_alias': 'default'
    }


class Player(meng.DynamicDocument):
    player_name = StringField(required=True, unique=True)
    steam_id = IntField(required=True)
    team = StringField()

    meta = {
        'indexes': ['player_name', 'steam_id'],
        'db_alias': 'default'
    }


class Round(meng.DynamicDocument):
    matchID = ReferenceField(Match)
    roundNum = IntField()
    startTick = IntField()
    endTick = IntField()
    bombPlantTick = IntField()
    tScore = IntField()
    ctScore = IntField()
    winningTeam = StringField()
    losingTeam = StringField()
    roundEndReason = StringField()
    ctBuyType = StringField()
    tBuyType = StringField()

    meta = {
        'indexes': ['player_name', 'steam_id'],
        'db_alias': 'default'
    }


class Frag(meng.DynamicDocument):
    matchID = ReferenceField(Match)
    roundNum = IntField()
    seconds = FloatField()
    attackerName = StringField()
    attackerX, attackerY, attackerZ = FloatField(), FloatField(), FloatField()
    attackerViewX, attackerViewY = FloatField(), FloatField()
    victimName = StringField()
    victimX, victimY, victimZ = FloatField(), FloatField(), FloatField()
    victimViewX, victimViewY = FloatField(), FloatField()
    distance = FloatField()
    isFirstKill = BooleanField()
    isHeadshot = BooleanField()
    weapon, weaponClass = StringField(), StringField()

    meta = {
        'indexes': ['matchID', 'roundNum', 'attackerName', 'victimName'],
        'db_alias': 'default'
    }


class OnePlayerFrame(meng.EmbeddedDocument):
    playerName = StringField()
    playerX, playerY, playerZ = FloatField(), FloatField(), FloatField()
    velocityX, velocityY, velocityZ = FloatField(), FloatField(), FloatField()
    viewX, viewY = FloatField(), FloatField()
    hp, armor, hasHelmet, hasDefuse = IntField(), IntField(), BooleanField(), BooleanField()
    activeWeapon = StringField()
    flash, smoke, grenade, incendiary = IntField(), IntField(), IntField(), IntField()


class TeamFrame(meng.EmbeddedDocument):
    teamName = StringField()
    playerFrameDict = ListField(field=EmbeddedDocumentField(OnePlayerFrame))


class BombCoordinates(meng.EmbeddedDocument):
    x = FloatField()
    y = FloatField()
    z = FloatField()


class Frame(meng.DynamicDocument):
    matchID = ReferenceField(Match)
    roundNum = IntField()
    seconds = FloatField()
    bomb = EmbeddedDocumentField(BombCoordinates)
    team1FrameDict = EmbeddedDocumentField(TeamFrame)
    team2FrameDict = EmbeddedDocumentField(TeamFrame)

    meta = {
        'indexes': ['matchID', 'roundNum'],
        'db_alias': 'default'
    }
