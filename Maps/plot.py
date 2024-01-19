from typing import Dict

from matplotlib import patches, cm

import numpy as np
import pandas as pd
import mongoengine as mongo

import matplotlib.pyplot as plt

from Maps.utils import get_vision_collection_details
from data_type import TeamStateInfo, FrameTeamVisionCollection


def connect_db():
    return mongo.connect(db="csgo", username="lihong", password="1998918!", host="localhost", port=27017)


def get_NAV_csv():
    ...


class FrameVisualizer:
    def __init__(self, matchMap=r"./mapMetaData/de_inferno.png"):
        self.matchID = None
        self.map = matchMap
        self.inferno_parameter = {"pos_x": -2087.0, "pos_y": 3870.0, "scale": 4.9}
        self.nav_data = pd.read_csv("./mapMetaData/area_info.csv")

    def get_tile_to_plot(self, plot_block):
        nav = self.nav_data.copy()
        nav.areaName = nav.areaName.fillna("")
        nav = nav[nav["areaId"].isin(plot_block)][["northWestX", "northWestY", "southEastX", "southEastY"]]
        nav["northWestX"] = (nav["northWestX"] - self.inferno_parameter["pos_x"]) / self.inferno_parameter['scale']
        nav["southEastX"] = (nav["southEastX"] - self.inferno_parameter["pos_x"]) / self.inferno_parameter['scale']
        nav["northWestY"] = (-nav["northWestY"] + self.inferno_parameter["pos_y"]) / self.inferno_parameter['scale']
        nav["southEastY"] = (-nav["southEastY"] + self.inferno_parameter["pos_y"]) / self.inferno_parameter['scale']
        nav["height"] = abs(nav["northWestX"] - nav["southEastX"])
        nav["width"] = abs(nav["northWestY"] - nav["southEastY"])

        return nav

    def draw_block(self, team_state_info: TeamStateInfo, vision_collection: FrameTeamVisionCollection):
        searcher_tile_ids, searcher_tile_depth = get_vision_collection_details(vision_collection.searcher_vision_collection)
        searchee_tile_ids, searchee_tile_depth = get_vision_collection_details(vision_collection.searchee_vision_collection)

        searcher_nav = self.get_tile_to_plot(searcher_tile_ids)
        searchee_nav = self.get_tile_to_plot(searchee_tile_ids)

        img = plt.imread(self.map)
        fig, ax = plt.subplots(dpi=300)
        ax.imshow(img, zorder=0)

        for index, row in searcher_nav.iterrows():
            start_coordinate = (row["northWestX"], row["southEastY"])
            height, width = row["height"], row["width"]
            rectangle = patches.Rectangle(start_coordinate, width, height, linewidth=2, edgecolor='cyan', facecolor='cyan', alpha=0.3)
            ax.add_patch(rectangle)

        for index, row in searchee_nav.iterrows():
            start_coordinate = (row["northWestX"], row["southEastY"])
            height, width = row["height"], row["width"]
            rectangle = patches.Rectangle(start_coordinate, width, height, linewidth=2, edgecolor='coral', facecolor='coral', alpha=0.3)
            ax.add_patch(rectangle)

        searcher_player_info = team_state_info.searcher_team_info
        searchee_player_info = team_state_info.searchee_team_info

        plot_pos = [[player.player_pos.x, player.player_pos.y] for player in searcher_player_info]
        plot_viewX = [player.player_viewX for player in searcher_player_info]
        plot_hp = [player.player_hp for player in searcher_player_info]

        viewX = np.radians(plot_viewX)
        for index in range(5):
            x = plot_pos[index][0]
            y = plot_pos[index][1]
            marker = 'o' if plot_hp[index] != 0 else 'x'
            plt.scatter(x, y, marker=marker, color='blue')

            # player viewX
            R = 15
            x_view = x + R * np.cos(viewX[index])
            y_view = y + R * np.sin(viewX[index])
            if plot_hp[index] != 0:
                plt.plot([x, x_view], [y, y_view], color='yellow')

        plot_pos = [[player.player_pos.x, player.player_pos.y] for player in searchee_player_info]
        plot_viewX = [player.player_viewX for player in searchee_player_info]
        plot_hp = [player.player_hp for player in searchee_player_info]

        viewX = np.radians(plot_viewX)
        for index in range(5):
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

    def show_map_control(self, team_state_info: TeamStateInfo, tile_dict: Dict[int, float]):
        tile_ids = list(tile_dict.keys())
        tile_depth = list(tile_dict.values())

        nav = self.nav_data.copy()
        nav.areaName = nav.areaName.fillna("")
        nav = nav[nav["areaId"].isin(tile_ids)][["areaId", "northWestX", "northWestY", "southEastX", "southEastY"]]
        nav["northWestX"] = (nav["northWestX"] - self.inferno_parameter["pos_x"]) / self.inferno_parameter['scale']
        nav["southEastX"] = (nav["southEastX"] - self.inferno_parameter["pos_x"]) / self.inferno_parameter['scale']
        nav["northWestY"] = (-nav["northWestY"] + self.inferno_parameter["pos_y"]) / self.inferno_parameter['scale']
        nav["southEastY"] = (-nav["southEastY"] + self.inferno_parameter["pos_y"]) / self.inferno_parameter['scale']
        nav["height"] = abs(nav["northWestX"] - nav["southEastX"])
        nav["width"] = abs(nav["northWestY"] - nav["southEastY"])
        nav["depth"] = tile_depth

        print(set(nav.depth.values))

        img = plt.imread(self.map)
        fig, ax = plt.subplots(dpi=300)
        ax.imshow(img, zorder=0)

        cmap = cm.get_cmap('coolwarm')

        for index, row in nav.iterrows():
            if row['depth'] != 0:
                start_coordinate = (row["northWestX"], row["southEastY"])
                height, width = row["height"], row["width"]

                color = cmap(row['depth'])

                rectangle = patches.Rectangle(start_coordinate, width, height, linewidth=2, edgecolor=color, facecolor=color, alpha=0.5)
                ax.add_patch(rectangle)

        searcher_player_info = team_state_info.searcher_team_info

        plot_pos = [[player.player_pos.x, player.player_pos.y] for player in searcher_player_info]
        plot_viewX = [player.player_viewX for player in searcher_player_info]
        plot_hp = [player.player_hp for player in searcher_player_info]

        viewX = np.radians(plot_viewX)
        for index in range(5):
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
