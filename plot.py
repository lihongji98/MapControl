from io import BytesIO

from matplotlib import patches
from tqdm import tqdm

import database
import numpy as np
import pandas as pd
import mongoengine as mongo

import matplotlib.pyplot as plt
import imageio


def connect_db():
    return mongo.connect(db="csgo", username="lihong", password="1998918!", host="localhost", port=27017)


class FrameVisualizer:
    def __init__(self, matchMap=r"D:\pycharm_projects\MapControl\Maps\mapMetaData\de_inferno.png"):
        self.matchID = None
        self.map = matchMap
        self.inferno_parameter = {"pos_x": -2087.0,
                                  "pos_y": 3870.0,
                                  "scale": 4.9}

    def position_transformation(self, coordinate, pos_type):
        start_x = self.inferno_parameter["pos_x"]
        start_y = self.inferno_parameter["pos_y"]
        scale = self.inferno_parameter["scale"]
        if pos_type == "player":
            coordinate = np.array(coordinate).reshape(5, 2)
            for i in range(len(coordinate)):
                coordinate[i][0] = (coordinate[i][0] - start_x) / scale
                coordinate[i][1] = (start_y - coordinate[i][1]) / scale
        elif pos_type == "bomb":
            coordinate = np.array(coordinate).reshape(1, 2)
            coordinate[0][0] = (coordinate[0][0] - start_x) / scale
            coordinate[0][1] = (start_y - coordinate[0][1]) / scale
        else:
            msg = "Choose 'player' or 'bomb' position!"
            ValueError(msg)
        return coordinate

    def match_info_retrieve(self,
                            para_series,
                            para_mapName,
                            para_teamLose,
                            para_teamWin):
        match = database.Match.objects(series=para_series,
                                       mapName=para_mapName,
                                       teamWin=para_teamWin,
                                       teamLose=para_teamLose)
        self.matchID = match[0].id

    def frame_info_retrieve(self, round_num=0, frame_num=0):
        frame_info = database.Frame.objects(matchID=self.matchID, roundNum=round_num)

        first_frame = frame_info[frame_num]  # choose which frame to plot
        bomb_coordinate = [[first_frame.bomb.x, first_frame.bomb.y]]

        # "name": first_frame.team1FrameDict.teamName,
        def get_player_position(teamSide):
            playerInfoDict = first_frame.team1FrameDict.playerFrameDict if teamSide == "team1" \
                else first_frame.team2FrameDict.playerFrameDict

            team = {"player1_pos": [playerInfoDict[0].playerX, playerInfoDict[0].playerY,
                                    playerInfoDict[0].viewX, playerInfoDict[0].hp],
                    "player2_pos": [playerInfoDict[1].playerX, playerInfoDict[1].playerY,
                                    playerInfoDict[1].viewX, playerInfoDict[1].hp],
                    "player3_pos": [playerInfoDict[2].playerX, playerInfoDict[2].playerY,
                                    playerInfoDict[2].viewX, playerInfoDict[2].hp],
                    "player4_pos": [playerInfoDict[3].playerX, playerInfoDict[3].playerY,
                                    playerInfoDict[3].viewX, playerInfoDict[3].hp],
                    "player5_pos": [playerInfoDict[4].playerX, playerInfoDict[4].playerY,
                                    playerInfoDict[4].viewX, playerInfoDict[4].hp]
                    }
            team_pos = [[team[player_index][0], team[player_index][1]] for player_index in team.keys()]
            team_view = [team[player_index][2] for player_index in team.keys()]
            team_hp = [team[player_index][3] for player_index in team.keys()]
            return team_pos, team_view, team_hp

        team1_pos, team1_view, team1_hp = get_player_position("team1")
        team2_pos, team2_view, team2_hp = get_player_position("team2")

        team1_position = self.position_transformation(team1_pos, "player")
        team2_position = self.position_transformation(team2_pos, "player")
        bomb_position = self.position_transformation(bomb_coordinate, "bomb")

        pos_dict = {"team1": {"name": first_frame.team1FrameDict.teamName,
                              "position": team1_position,
                              "view": team1_view,
                              "hp": team1_hp},
                    "team2": {"name": first_frame.team2FrameDict.teamName,
                              "position": team2_position,
                              "view": team2_view,
                              "hp": team2_hp},
                    "bomb": bomb_position}
        return pos_dict

    def plot(self, pos_dict):
        img = plt.imread(self.map)
        fig, ax = plt.subplots(dpi=100)
        ax.imshow(img, zorder=0)

        team1_name, team1_position, team1_view, team1_hp = (pos_dict["team1"]["name"], pos_dict["team1"]["position"],
                                                            pos_dict["team1"]["view"], pos_dict["team1"]["hp"])
        team2_name, team2_position, team2_view, team2_hp = (pos_dict["team2"]["name"], pos_dict["team2"]["position"],
                                                            pos_dict["team2"]["view"], pos_dict["team2"]["hp"])
        bomb_position = pos_dict["bomb"]

        x_values1, y_values1 = zip(*team1_position)
        x_values2, y_values2 = zip(*team2_position)
        x_bomb, y_bomb = zip(*bomb_position)

        R = 15
        team1_view = np.radians(team1_view)
        team2_view = np.radians(team2_view)

        x_view1 = np.array(x_values1) + R * np.cos(team1_view)
        y_view1 = np.array(y_values1) + R * np.sin(team1_view)

        x_view2 = np.array(x_values2) + R * np.cos(team2_view)
        y_view2 = np.array(y_values2) + R * np.sin(team2_view)

        for i in range(len(x_view1)):
            if team1_hp[i] > 0:
                plt.plot([x_values1[i], x_view1[i]], [y_values1[i], y_view1[i]], color='yellow')

        for j in range(len(x_view2)):
            if team2_hp[j] > 0:
                plt.plot([x_values2[j], x_view2[j]], [y_values2[j], y_view2[j]], color='yellow')

        for x, y, hp1 in zip(x_values1, y_values1, team1_hp):
            marker = '.' if hp1 > 0 else 'x'
            plt.scatter(x=x, y=y, color='blue', marker=marker)

        for x, y, hp2 in zip(x_values2, y_values2, team2_hp):
            marker = '.' if hp2 > 0 else 'x'
            plt.scatter(x=x, y=y, color='red', marker=marker)

        plt.scatter(x=x_bomb, y=y_bomb, color='orange', marker='.')

        ax.get_xaxis().set_visible(b=False)
        ax.get_yaxis().set_visible(b=False)
        # plt.show()

        return fig

    def run(self):
        connect_db()
        self.match_info_retrieve(para_series="PGL-Major-Antwerp-2022-faze-vs-natus-vincere",
                                 para_mapName="de_inferno",
                                 para_teamWin="FaZe Clan",
                                 para_teamLose="Natus Vincere")
        pos = self.frame_info_retrieve(round_num=0, frame_num=0)
        self.plot(pos)

    def draw_block(self, plot_block, plot_pos, plot_viewX):
        plot_block = np.concatenate(plot_block).tolist()
        # player block
        NAV_CSV = pd.read_csv(r"D:\pycharm_projects\MapControl\Maps\mapMetaData\area_info.csv")
        NAV_CSV.areaName = NAV_CSV.areaName.fillna("")
        NAV_CSV = NAV_CSV[NAV_CSV["areaId"].isin(plot_block)][["northWestX", "northWestY", "southEastX", "southEastY"]]
        NAV_CSV["northWestX"] = (NAV_CSV["northWestX"] - self.inferno_parameter["pos_x"]) / self.inferno_parameter[
            'scale']
        NAV_CSV["southEastX"] = (NAV_CSV["southEastX"] - self.inferno_parameter["pos_x"]) / self.inferno_parameter[
            'scale']
        NAV_CSV["northWestY"] = (-NAV_CSV["northWestY"] + self.inferno_parameter["pos_y"]) / self.inferno_parameter[
            'scale']
        NAV_CSV["southEastY"] = (-NAV_CSV["southEastY"] + self.inferno_parameter["pos_y"]) / self.inferno_parameter[
            'scale']
        NAV_CSV["height"] = abs(NAV_CSV["northWestX"] - NAV_CSV["southEastX"])
        NAV_CSV["width"] = abs(NAV_CSV["northWestY"] - NAV_CSV["southEastY"])
        img = plt.imread(self.map)
        fig, ax = plt.subplots(dpi=300)
        ax.imshow(img, zorder=0)
        for index, row in NAV_CSV.iterrows():
            start_coordinate = (row["northWestX"], row["southEastY"])
            height, width = row["height"], row["width"]
            rectangle = patches.Rectangle(start_coordinate, width, height, linewidth=2, edgecolor='green',
                                          facecolor='green', alpha=0.5)
            ax.add_patch(rectangle)

        viewX = np.radians(plot_viewX)
        for index in range(5):
            # player pos
            x = plot_pos[index][0]
            y = plot_pos[index][1]
            plt.scatter(x, y, marker='o', color='red')

            # player viewX
            R = 15
            x_view = x + R * np.cos(viewX[index])
            y_view = y + R * np.sin(viewX[index])
            plt.plot([x, x_view], [y, y_view], color='yellow')

        ax.get_xaxis().set_visible(b=False)
        ax.get_yaxis().set_visible(b=False)
        # plt.show()
        return fig

# a = FrameVisualizer()
# a.make_gif()
