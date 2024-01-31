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

    def draw_block(self, tile_ids):
        nav = self.nav_data.copy()
        nav.areaName = nav.areaName.fillna("")
        nav = nav[nav["areaId"].isin(tile_ids)][["areaId", "northWestX", "northWestY", "southEastX", "southEastY"]]
        nav["northWestX"] = (nav["northWestX"] - self.inferno_parameter["pos_x"]) / self.inferno_parameter['scale']
        nav["southEastX"] = (nav["southEastX"] - self.inferno_parameter["pos_x"]) / self.inferno_parameter['scale']
        nav["northWestY"] = (-nav["northWestY"] + self.inferno_parameter["pos_y"]) / self.inferno_parameter['scale']
        nav["southEastY"] = (-nav["southEastY"] + self.inferno_parameter["pos_y"]) / self.inferno_parameter['scale']
        nav["height"] = abs(nav["northWestX"] - nav["southEastX"])
        nav["width"] = abs(nav["northWestY"] - nav["southEastY"])

        img = plt.imread(self.map)
        fig, ax = plt.subplots(dpi=300)
        ax.imshow(img, zorder=0)

        for index, row in nav.iterrows():
            start_coordinate = (row["northWestX"], row["southEastY"])
            height, width = row["height"], row["width"]

            rectangle = patches.Rectangle(start_coordinate, width, height, linewidth=2, edgecolor='green', facecolor='green', alpha=0.5)
            ax.add_patch(rectangle)

        plt.show()

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

        img = plt.imread(self.map)
        fig, ax = plt.subplots(dpi=100)
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

        # ax.get_xaxis().set_visible(b=False)
        # ax.get_yaxis().set_visible(b=False)

        return fig

# a = FrameVisualizer()
# a.draw_block([302, 3047, 1793, 2961, 967, 2878, 84, 2711, 2855, 1662, 2862, 485, 346, 1204, 1948, 117, 956, 2876, 53, 2628, 2871, 3028, 2802, 8, 2564, 2925, 396, 2567, 2805, 359, 898, 939, 2477, 2563, 2970, 58, 358, 2831, 2149, 2715, 531, 2801, 959, 111, 345, 2794, 269, 2669, 2971, 3156, 2717, 1627, 2995, 479, 598, 97, 2826, 384, 2640, 31, 2941, 2503, 2562, 774, 2505, 2520, 3048, 1423, 585, 63, 1471, 2633, 2651, 303, 496, 1358, 15, 2828, 966, 277, 740, 1606, 575, 749, 3001, 20, 2626, 2109, 2716, 2370, 2877, 2968, 2882, 205, 2940, 2990, 2020, 3129, 1418, 1619, 2793, 2766, 2863, 2939, 769, 730, 775, 2866, 2884, 1721, 1432, 940, 961, 1605, 944, 2315, 1608, 464, 1807, 765, 98, 2367, 2712, 2639, 244, 363, 2713, 2873, 3046, 2808, 2832, 81, 3, 2953, 3143, 2323, 2634, 2883, 3050, 338, 406, 3029, 1203, 243, 180, 2868, 311, 2951, 897, 181, 2653, 2559, 2765, 10, 481, 43, 2944, 412, 2969, 1733, 2872, 2954, 32, 3051, 2952, 2308, 850, 124, 80, 2946, 200, 2942, 312, 272, 2627, 2718, 525, 2807, 86, 2641, 1620, 1625, 1674, 2827, 2304, 2885, 1615, 600, 700, 202, 887, 2714, 2856, 532, 1425, 2642, 2825, 2945, 21]
# )
