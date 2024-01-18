from typing import List

from matplotlib import patches

import numpy as np
import pandas as pd
import mongoengine as mongo

import matplotlib.pyplot as plt

from data_type import FramePlayerInfo


def connect_db():
    return mongo.connect(db="csgo", username="lihong", password="1998918!", host="localhost", port=27017)


class FrameVisualizer:
    def __init__(self, matchMap=r"D:\pycharm_projects\MapControl\Maps\mapMetaData\de_inferno.png"):
        self.matchID = None
        self.map = matchMap
        self.inferno_parameter = {"pos_x": -2087.0,
                                  "pos_y": 3870.0,
                                  "scale": 4.9}

    def draw_block(self, plot_block, player_info: List[FramePlayerInfo]):
        # plot_block = np.concatenate(plot_block).tolist()
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

        plot_pos = [[player.player_pos.x, player.player_pos.y] for player in player_info]
        plot_viewX = [player.player_viewX for player in player_info]
        plot_hp = [player.player_hp for player in player_info]

        viewX = np.radians(plot_viewX)
        for index in range(5):
            # player pos
            x = plot_pos[index][0]
            y = plot_pos[index][1]
            marker = 'o' if plot_hp[index] != 0 else 'x'
            plt.scatter(x, y, marker=marker, color='red')

            # player viewX
            R = 15
            x_view = x + R * np.cos(viewX[index])
            y_view = y + R * np.sin(viewX[index])
            if plot_hp[index] != 0:
                plt.plot([x, x_view], [y, y_view], color='yellow')

        ax.get_xaxis().set_visible(b=False)
        ax.get_yaxis().set_visible(b=False)
        # plt.show()
        return fig
