import json
import database
import mongoengine as mongo


def connect_db():
    return mongo.connect(db="csgo", username="lihong", password="1998918!", host="localhost", port=27017)


class JsonParser:
    def __init__(self):
        self.Matches = []
        self.Teams = []
        self.Players = []
        self.Rounds = []
        self.Frags = []
        self.Frames = []

    def parse(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)

        """
        First get the general match information.
        """
        # general_info_keys = ['matchID', 'mapName']
        match_info_dict = {'series': data['matchID'],
                           'mapName': data['mapName']}

        if data['gameRounds'][-1]['endTScore'] > data['gameRounds'][-1]['endCTScore']:
            team_win = data['gameRounds'][-1]['tSide']['teamName']
            team_lose = data['gameRounds'][-1]['ctSide']['teamName']
        else:
            team_lose = data['gameRounds'][-1]['tSide']['teamName']
            team_win = data['gameRounds'][-1]['ctSide']['teamName']

        match_info_dict['teamWin'] = team_win
        match_info_dict['teamLose'] = team_lose
        self.Matches.append(match_info_dict)

        """
        Second get the team information.
        """
        self.Teams.append({'team': data['gameRounds'][0]['ctSide']['teamName']})
        self.Teams.append({'team': data['gameRounds'][0]['tSide']['teamName']})

        """
        Third get the Player information.
        """

        def player_info_retrieve(team_side):
            for i_player in range(len(data['gameRounds'][0]['frames'][0][team_side]['players'])):
                player_name = data['gameRounds'][0]['frames'][0][team_side]['players'][i_player]['name']
                player_steam_id = data['gameRounds'][0]['frames'][0][team_side]['players'][i_player]['steamID']
                player_team = data['gameRounds'][0]['frames'][0][team_side]['players'][i_player]['team']
                self.Players.append({'player_name': player_name, 'steam_id': player_steam_id, 'team': player_team})

        player_info_retrieve('t')
        player_info_retrieve('ct')

        """
        Forth get the Round information
        """
        round_candidate_attributes = ['roundNum', 'startTick', 'endTick', 'bombPlantTick', 'tScore', 'ctScore',
                                      'winningTeam', 'losingTeam',
                                      'roundEndReason', 'ctBuyType', 'tBuyType']
        # data['gameRounds'][i] == > i_th round info
        for i in range(len(data['gameRounds'])):
            temp_round_info = {}
            for candidate_att in round_candidate_attributes:
                temp_round_info[candidate_att] = data['gameRounds'][i][candidate_att]
            self.Rounds.append(temp_round_info)

        """
        Fifth get the Frag information
        """
        frag_candidate_attributes = ['seconds',
                                     'attackerName', 'attackerX', 'attackerY', 'attackerZ', 'attackerViewX',
                                     'attackerViewY',
                                     'victimName', 'victimX', 'victimY', 'victimZ', 'victimViewX', 'victimViewY',
                                     'distance',
                                     'isFirstKill', 'isHeadshot',
                                     'weapon', 'weaponClass']
        for i in range(len(data['gameRounds'])):
            for j in range(len(data['gameRounds'][i]['kills'])):
                temp_frag_info = {'roundNum': i}
                for candidate_att in frag_candidate_attributes:
                    temp_frag_info[candidate_att] = data['gameRounds'][i]['kills'][j][candidate_att]
                self.Frags.append(temp_frag_info)

        """
        Sixth get the frame information
        """
        # frame_candidate_attributes = ['seconds', 'bomb']
        for i in range(len(data['gameRounds'])):
            for j in range(len(data['gameRounds'][i]['frames'])):
                frame_info = {'roundNum': i,
                              'bomb': data['gameRounds'][i]['frames'][j]['bomb'],
                              'seconds': data['gameRounds'][i]['frames'][j]['seconds'],
                              'team1FrameDict': {'teamName': data['gameRounds'][0]['ctTeam'], 'playerFrameDict': []},
                              'team2FrameDict': {'teamName': data['gameRounds'][0]['tTeam'], 'playerFrameDict': []}}

                for team_data in [data['gameRounds'][i]['frames'][j]['ct'], data['gameRounds'][i]['frames'][j]['t']]:
                    team_name = team_data['teamName']

                    team_dict = frame_info['team1FrameDict'] if team_name == frame_info['team1FrameDict'][
                        'teamName'] else frame_info['team2FrameDict']

                    for m in range(len(team_data['players'])):
                        playerData = team_data['players'][m]

                        playerInfo = {
                            'playerName': playerData['name'],
                            'playerX': playerData['x'],
                            'playerY': playerData['y'],
                            'playerZ': playerData['z'],
                            'velocityX': playerData['velocityX'],
                            'velocityY': playerData['velocityY'],
                            'velocityZ': playerData['velocityZ'],
                            'viewX': playerData['viewX'],
                            'viewY': playerData['viewY'],
                            'hp': playerData['hp'],
                            'armor': playerData['armor'],
                            'hasHelmet': playerData['hasHelmet'],
                            'hasDefuse': playerData['hasDefuse'],
                            'activeWeapon': playerData['activeWeapon'],
                            'flash': playerData['flashGrenades'],
                            'smoke': playerData['smokeGrenades'],
                            'grenade': playerData['heGrenades'],
                            'incendiary': playerData['fireGrenades']
                        }

                        team_dict['playerFrameDict'].append(playerInfo)

                sorted_player_frame_dict = sorted(frame_info['team1FrameDict']['playerFrameDict'],
                                                  key=lambda x: x['playerName'].strip())
                frame_info['team1FrameDict']['playerFrameDict'] = sorted_player_frame_dict

                sorted_player_frame_dict = sorted(frame_info['team2FrameDict']['playerFrameDict'],
                                                  key=lambda x: x['playerName'].strip())
                frame_info['team2FrameDict']['playerFrameDict'] = sorted_player_frame_dict

                self.Frames.append(frame_info)

    def update(self):
        connect_db()

        match_insert = False

        for item in self.Matches:
            if database.Match.objects(matchID=item['series']).first():
                print(f"The match with mathID '{item['series']}' is already in Match collection.")
            else:
                new_match = database.Match(**item)
                new_match.save()
                match_insert = True

        for item in self.Teams:
            if database.Team.objects(team=item['team']).first():
                print(f"The team : '{item['team']}' is already in Team collection.")
            else:
                database.Team(**item).save()

        for item in self.Players:
            if database.Player.objects(player_name=item['player_name']).first():
                print(f"The player: '{item['player_name']}' is already in Player collection.")
            else:
                database.Player(**item).save()

        if match_insert:
            match_id = {"matchID": new_match.id}
            for i in range(len(self.Rounds)):
                self.Rounds[i] = {**self.Rounds[i], **match_id}
            for item in self.Rounds:
                new_round = database.Round(**item)
                new_round.save()

            for i in range(len(self.Frags)):
                self.Frags[i] = {**self.Frags[i], **match_id}
            for item in self.Frags:
                new_frag = database.Frag(**item)
                new_frag.save()

            for i in range(len(self.Frames)):
                self.Frames[i] = {**self.Frames[i], **match_id}
            for item in self.Frames:
                new_frame = database.Frame(**item)
                new_frame.save()

    def reset_attributes(self):
        self.Matches = []
        self.Teams = []
        self.Players = []
        self.Rounds = []
        self.Frags = []
        self.Frames = []
