from queue import Queue
from typing import List, Literal

from data_type import OnePlayerVisionCollection, AreaCenterCoordinate

import pandas as pd


class MAPINFO:
    mapName = None
    mapScaleParameter = {"pos_x": -2087.0, "pos_y": 3870.0, "scale": 4.9}


def get_vision_collection_details(_vision_collection: List[OnePlayerVisionCollection]):
    _tile_ids = list(set([tile.tile_id for player_tiles_info in _vision_collection for tile in player_tiles_info]))
    _tile_depth = list(set([tile.tile_depth for player_tiles_info in _vision_collection for tile in player_tiles_info]))

    return _tile_ids, _tile_depth


def least_distance_between_two_nodes(graph, start_node, end_node):
    Q = Queue()
    visited_vertices = set()
    distance = {start_node: 0}
    Q.put(start_node)
    visited_vertices.update({start_node})
    while not Q.empty():
        current_vertex = Q.get()
        for neighbor in graph[current_vertex]:
            if neighbor not in visited_vertices:
                Q.put(neighbor)
                visited_vertices.update({neighbor})
                distance[neighbor] = distance[current_vertex] + 1
                if neighbor == end_node:
                    return distance[end_node]
    return -1


def get_site_center(area_name: Literal['BombsiteB', 'BombsiteA', 'CTSpawn', 'TSpawn']):
    area_name = [area_name]
    nav = pd.read_csv("./mapMetaData/area_info.csv")
    nav.areaName = nav.areaName.fillna("")
    nav = nav[nav["areaName"].isin(area_name)][["northWestX", "northWestY", 'northWestZ', "southEastX", "southEastY", 'southEastZ']]
    nav = nav.mean(axis=0)
    x = (nav["northWestX"] + nav["southEastX"]) / 2
    y = (nav["northWestY"] + nav["southEastY"]) / 2
    z = (nav["northWestZ"] + nav["southEastZ"]) / 2
    x = (x - MAPINFO.mapScaleParameter["pos_x"]) / MAPINFO.mapScaleParameter["scale"]
    y = (MAPINFO.mapScaleParameter["pos_y"] - y) / MAPINFO.mapScaleParameter["scale"]
    z = z

    return AreaCenterCoordinate(x, y, z)


def concave(dis, T_dis):
    return -0.5


def decay_coef(T_dis, CT_dis, A_dis, B_dis):
    decay_coef_value: int = -1
    conditions = {
        1: T_dis == CT_dis == A_dis == B_dis == -1,
        2: A_dis == B_dis == CT_dis == -1 and 0 <= T_dis <= 50,
        3: A_dis == B_dis == T_dis == -1 and 0 <= CT_dis <= 50,
        4: T_dis == B_dis == CT_dis == -1 and 0 <= A_dis <= 50,
        5: A_dis == T_dis == CT_dis == -1 and 0 <= B_dis <= 50,
        6: T_dis == A_dis == -1 and 0 <= CT_dis <= 50 and 0 <= B_dis <= 50,
        7: B_dis == A_dis == -1 and 0 <= CT_dis <= 50 and 0 <= T_dis <= 50,
        8: CT_dis == B_dis == -1 and 0 <= T_dis <= 50 and 0 <= A_dis <= 50,
        9: T_dis == B_dis == -1 and 0 <= CT_dis <= 50 and 0 <= A_dis <= 50,
        10: CT_dis == T_dis == -1 and 0 <= B_dis <= 50 and 0 <= A_dis <= 50,
        11: CT_dis == A_dis == -1 and 0 <= T_dis <= 50 and 0 <= B_dis <= 50,
        12: T_dis == -1 and 0 <= B_dis <= 50 and 0 <= A_dis <= 50 and 0 <= CT_dis <= 50,
        13: A_dis == -1 and 0 <= B_dis <= 50 and 0 <= T_dis <= 50 and 0 <= CT_dis <= 50,
        14: B_dis == -1 and 0 <= T_dis <= 50 and 0 <= A_dis <= 50 and 0 <= CT_dis <= 50,
        15: CT_dis == -1 and 0 <= B_dis <= 50 and 0 <= A_dis <= 50 and 0 <= T_dis <= 50,
        16: 0 <= T_dis <= 50 and 0 <= B_dis <= 50 and 0 <= A_dis <= 50 and 0 <= CT_dis <= 50,
    }
    decay_value = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: -1,
        7: concave(CT_dis, T_dis),
        8: concave(A_dis, T_dis),
        9: -1,
        10: -1,
        11: concave(B_dis, T_dis),
        12: -1,
        13: concave(B_dis, T_dis),
        14: concave(A_dis, T_dis),
        15: -1,
        16: -1
    }
    for condition, result in conditions.items():
        if result:
            decay_coef_value = decay_value[condition]

    return decay_coef_value
