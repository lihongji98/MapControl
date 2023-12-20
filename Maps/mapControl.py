import numpy as np
from bson import ObjectId

import database
from Maps import area_json, mapGraph, neighbors_dict
import mongoengine as mongo

map_scale_parameter = {"pos_x": -2087.0, "pos_y": 3870.0, "scale": 4.9}


def connect_db():
    return mongo.connect(db="csgo", username="lihong", password="1998918!", host="localhost", port=27017)


def _position_scaling(x, y):
    scaled_x = (x - map_scale_parameter["pos_x"]) / map_scale_parameter["scale"]
    scaled_y = (map_scale_parameter["pos_y"] - y) / map_scale_parameter["scale"]
    return scaled_x, scaled_y


def _get_area_center(map_name, area_id):
    area_x = (area_json[map_name][area_id]["southEastX"] + area_json[map_name][area_id]["northWestX"]) / 2
    area_y = (area_json[map_name][area_id]["southEastY"] + area_json[map_name][area_id]["northWestY"]) / 2
    return area_x, area_y


def _get_team_block(team_player_pos, map_name):
    closest_block_team = []
    for player_pos in team_player_pos:
        area_dis_dict = {}
        for area_id in area_json[map_name]:
            unscaled_center_x, unscaled_center_y = _get_area_center(map_name, area_id)
            center_x, center_y = _position_scaling(unscaled_center_x, unscaled_center_y)
            distance = np.sqrt(
                (player_pos[0] - center_x) ** 2 + (player_pos[1] - center_y) ** 2
            )
            area_dis_dict[area_id] = distance
        area_dis_dict = sorted(area_dis_dict.items(), key=lambda x: x[1])[0]
        closest_block_team.append(area_dis_dict[0])
    return closest_block_team


def _find_closest_block(frames_info, map_name, frameNum):
    team1_player_info = frames_info[frameNum].team1FrameDict.playerFrameDict
    team1_player_pos = [_position_scaling(player_info.playerX, player_info.playerY) for player_info in
                        team1_player_info]

    team2_player_info = frames_info[frameNum].team2FrameDict.playerFrameDict
    team2_player_pos = [_position_scaling(player_info.playerX, player_info.playerY) for player_info in
                        team2_player_info]

    team1_viewX = [player_info.viewX for player_info in team1_player_info]
    team2_viewX = [player_info.viewX for player_info in team2_player_info]

    team1_closest_block = _get_team_block(team1_player_pos, map_name)
    team2_closest_block = _get_team_block(team2_player_pos, map_name)

    team1_closest_tile_info = [[x, y, z] for x, y, z in zip(team1_player_pos, team1_viewX, team1_closest_block)]
    team2_closest_tile_info = [[x, y, z] for x, y, z in zip(team2_player_pos, team2_viewX, team2_closest_block)]

    return team1_closest_tile_info, team2_closest_tile_info


def _is_tile_in_view(player_pos, player_viewX, neighbor):
    # 16:9 angle -> 106.26º
    return True


def _dfs(matchID, roundNum, frameNum, neighbors):
    connect_db()
    map_name = database.Match.objects(id=matchID)[0].mapName
    frames_info = database.Frame.objects(matchID=matchID, roundNum=roundNum)
    team1_closest_block, team2_closest_block = _find_closest_block(frames_info, map_name, frameNum)

    for player_pos, player_viewX, tile in team1_closest_block:
        tile_seen = set()
        max_depth = 3

        def _dfs_recursive(cur_tile, depth):
            if depth > max_depth:
                return
            if cur_tile not in tile_seen:
                print(cur_tile)
                tile_seen.add(cur_tile)
                for neighbor in neighbors[cur_tile]:
                    if _is_tile_in_view(player_pos, player_viewX, neighbor):
                        _dfs_recursive(neighbor, depth + 1)

        _dfs_recursive(tile, 0)
        print("*" * 100)
    print(neighbors[tile])


def get_block_mask(player_info):
    _dfs(player_info, player_info, player_info)
    return 0


def compute_player_area_influence(player_info):
    return 0


def compute_team_area_influence(team):
    team_area_influence = 0
    for player_info in team:
        area_influence = compute_player_area_influence(player_info)
        block_mask = get_block_mask(player_info)
        team_area_influence += area_influence * block_mask
    return team_area_influence


def sigmoid(x):
    return (1 + np.exp(-x)) ** (-1)


def compute_team_map_control(team1, team2):
    team1_control = compute_team_area_influence(team1)
    team2_control = compute_team_area_influence(team2)
    team_control = sigmoid(team1_control - team2_control)
    return team_control


def compute_frame_map_control(frame):
    compute_team_map_control(frame)
    pass


_dfs(ObjectId("656c9a14a038bfba3be1021d"), 0, 0, neighbors_dict)
print(neighbors_dict[23])
