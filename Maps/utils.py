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
    ...


def get_area_center(area_name: Literal['BombsiteB', 'BombsiteA', 'CTSpawn', 'TSpawn']):
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


center_coordinate = get_area_center('BombsiteB')
print(center_coordinate)
