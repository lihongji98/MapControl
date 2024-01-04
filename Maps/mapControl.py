import numpy as np
from bson import ObjectId

import database
from Maps import area_json, mapGraph, neighbors_dict
import mongoengine as mongo
from collections import deque

from plot import FrameVisualizer

map_scale_parameter = {"pos_x": -2087.0, "pos_y": 3870.0, "scale": 4.9}


def connect_db():
    return mongo.connect(db="csgo", username="lihong", password="1998918!", host="localhost", port=27017)


def _position_scaling(x, y, z):
    scaled_x = (x - map_scale_parameter["pos_x"]) / map_scale_parameter["scale"]
    scaled_y = (map_scale_parameter["pos_y"] - y) / map_scale_parameter["scale"]
    scaled_z = z
    return scaled_x, scaled_y, scaled_z


def _get_area_center(map_name, area_id):
    area_x = (area_json[map_name][area_id]["southEastX"] + area_json[map_name][area_id]["northWestX"]) / 2
    area_y = (area_json[map_name][area_id]["southEastY"] + area_json[map_name][area_id]["northWestY"]) / 2
    area_z = (area_json[map_name][area_id]["southEastZ"] + area_json[map_name][area_id]["northWestZ"]) / 2
    return area_x, area_y, area_z


def _get_team_block(team_player_pos, map_name):
    closest_block_team = []
    for player_pos in team_player_pos:
        area_dis_dict = {}
        for area_id in area_json[map_name]:
            unscaled_center_x, unscaled_center_y, unscaled_center_z = _get_area_center(map_name, area_id)
            center_x, center_y, center_z = _position_scaling(unscaled_center_x, unscaled_center_y, unscaled_center_z)
            distance = np.sqrt(
                (player_pos[0] - center_x) ** 2 + (player_pos[1] - center_y) ** 2 + (player_pos[2] - center_z) ** 2
            )
            area_dis_dict[area_id] = distance
        area_dis_dict = sorted(area_dis_dict.items(), key=lambda x: x[1])[0]
        closest_block_team.append(area_dis_dict[0])
    return closest_block_team


def _find_closest_block(frames_info, map_name, frameNum, team):
    """
    This is the function which finds the tile that the player are located in currently.
    :param team: choose "team1" or "team2" (str)
    :return: return [x, y, z] for each player, x->player's (x,y,
    z) : tuple, y->viewX: float, z->player's closest_block_id: int
    """
    team_player_info = frames_info[frameNum][team + "FrameDict"].playerFrameDict
    team_player_pos = [_position_scaling(player_info.playerX, player_info.playerY, player_info.playerZ)
                       for player_info in team_player_info]
    team_viewX = [player_info.viewX for player_info in team_player_info]
    team_closest_block = _get_team_block(team_player_pos, map_name)
    team_player_tile_info = [[x, y, z] for x, y, z in zip(team_player_pos, team_viewX, team_closest_block)]

    return team_player_tile_info


def _is_tile_in_view(player_pos, player_viewX, neighbor):
    # 16:9 angle -> 106.26º
    return True


def _bfs(matchID, roundNum, frameNum, team, max_depth=10):
    connect_db()
    map_name = database.Match.objects(id=matchID)[0].mapName
    frames_info = database.Frame.objects(matchID=matchID, roundNum=roundNum)
    team_player_tile_info = _find_closest_block(frames_info, map_name, frameNum, team)
    """
    Attention:
    The graph is Directed Graph with 990 nodes and 3166 edges,
    but neighbor_dict only has 909 nodes.
    """
    plot_blocks = []
    for player_info in team_player_tile_info:
        pos_x, pos_y, pos_z = player_info[0][0], player_info[0][1], player_info[0][2]
        viewX, start_tile = player_info[1], player_info[2]
        start_depth = 0
        to_visit_tiles = deque([(start_tile, start_depth)])
        visited_tiles = set()
        plot_block = []
        while to_visit_tiles:
            search_tile, current_depth = to_visit_tiles.popleft()
            if search_tile not in visited_tiles and current_depth < max_depth:
                visited_tiles.add(search_tile)
                plot_block.append(search_tile)
                for neighbor in neighbors_dict.get(search_tile, {}):
                    if neighbor not in visited_tiles:
                        to_visit_tiles.append((neighbor, current_depth + 1))
        plot_blocks.append(plot_block)
    return plot_blocks


def compute_player_area_influence(player_info):
    return 0


def compute_team_area_influence(team):
    team_area_influence = 0
    for player_info in team:
        area_influence = compute_player_area_influence(player_info)
        team_area_influence += area_influence
    return team_area_influence


def sigmoid(x):
    return (1 + np.exp(-x)) ** (-1)


def compute_team_map_control(team1, team2):
    team1_control = compute_team_area_influence(team1)
    team2_control = compute_team_area_influence(team2)
    team_control = sigmoid(team1_control - team2_control)
    return team_control


def compute_frame_map_control(frame):
    pass


matchid = ObjectId("656c9a14a038bfba3be1021d")
plot_blocks = _bfs(matchid, 0, 50, "team1")
visualizer = FrameVisualizer()
visualizer.draw_block(plot_blocks[1])
