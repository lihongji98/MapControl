from collections import deque
from io import BytesIO

import imageio
import mongoengine as mongo
import numpy as np
from bson import ObjectId
from typing import Literal, List, Dict

from matplotlib import pyplot as plt
from tqdm import tqdm

import database
from data_type import (
    PlayerPos,
    TilePos,
    FramePlayerInfo,
    FrameTeamInfo,
    TileDistance,
    TileID,
    BfsTileInfo,
    OnePlayerVisionCollection,
    TeamVisionCollection, FrameTeamVisionCollection)

from Maps import area_json, neighbors_dict
from plot import FrameVisualizer


class MAPINFO:
    mapName = None
    mapScaleParameter = {"pos_x": -2087.0, "pos_y": 3870.0, "scale": 4.9}


def connect_db():
    return mongo.connect(db="csgo", username="lihong", password="1998918!", host="localhost", port=27017)


def _position_scaling(x: float, y: float, z: float, data: Literal["player", "tile"]):
    """
    scale the coordinates from the original dataset.
    :param data: the processed data type, "player" pos or "tile" pos.
    :return: a PlayerPos object with the scaled coordinates: x,y,z.
    """
    scaled_x = (x - MAPINFO.mapScaleParameter["pos_x"]) / MAPINFO.mapScaleParameter["scale"]
    scaled_y = (MAPINFO.mapScaleParameter["pos_y"] - y) / MAPINFO.mapScaleParameter["scale"]
    scaled_z = z

    return PlayerPos(scaled_x, scaled_y, scaled_z) if data == "player" else TilePos(scaled_x, scaled_y, scaled_z)


def _get_area_center(map_name: str, tile_id: int):
    """
    :param map_name: str
    :param tile_id: int
    :return: TilePos object with the center coordinates: x,y,z.
    """
    tile_x = (area_json[map_name][tile_id]["southEastX"] + area_json[map_name][tile_id]["northWestX"]) / 2
    tile_y = (area_json[map_name][tile_id]["southEastY"] + area_json[map_name][tile_id]["northWestY"]) / 2
    tile_z = (area_json[map_name][tile_id]["southEastZ"] + area_json[map_name][tile_id]["northWestZ"]) / 2
    tile_center: TilePos = _position_scaling(tile_x, tile_y, tile_z, "tile")

    return tile_center


def get_team_tile(team_player_pos: List[PlayerPos], map_name: str):
    """
    get the current tile of each player position of the team.
    :param team_player_pos: a list containing the position of the players
    :param map_name: str
    :return: a list containing 5 tile ids.
    """
    team_closest_block: List[TileID] = []
    for player_pos in team_player_pos:
        x, y, z = player_pos.x, player_pos.y, player_pos.z
        tile_dis_dict: Dict[int, float] = {}
        for area_id in area_json[map_name]:
            tile_center = _get_area_center(map_name, area_id)

            distance = np.sqrt(
                (x - tile_center.x) ** 2 + (y - tile_center.y) ** 2 + (z - tile_center.z) ** 2
            )

            tile_dis_dict[area_id] = distance
        tile_dis_closest: TileDistance = sorted(tile_dis_dict.items(), key=lambda tile_dist: tile_dist[1])[0]
        team_closest_block.append(tile_dis_closest[0])

    return team_closest_block


def find_closest_neighbors(source_id: int, map_name: str, neighborNum: int):
    """
    Get the list of closest neighbors' ids.
    :param map_name: str
    :param source_id: int
    :param neighborNum: the number of neighbors to the source tile
    :return: A list containing the closest neighbors' ids.
    """
    source_tile_center: TilePos = _get_area_center(map_name, source_id)

    tile_dis_dict: Dict[int, float] = {}
    for tile_id in area_json[map_name]:
        if tile_id != source_id:
            tile_center: TilePos = _get_area_center(map_name, tile_id)
            distance = np.sqrt(
                (source_tile_center.x - tile_center.x) ** 2
                + (source_tile_center.y - tile_center.y) ** 2
                + (source_tile_center.z - tile_center.z) ** 2
            )
            tile_dis_dict[tile_id] = distance

    tile_dis_closest: List[TileDistance] = sorted(tile_dis_dict.items(), key=lambda tile_dist: tile_dist[1])[
                                           :neighborNum]
    closest_neighbors: List[TileID] = [tileDist[0] for tileDist in tile_dis_closest]

    return closest_neighbors


def _is_tile_in_view(player_pos: PlayerPos, viewX: float, search_tile: TileID):
    center: TilePos = _get_area_center(MAPINFO.mapName, search_tile)
    to_check_tile_vec = np.array([center.x - player_pos.x, center.y - player_pos.y])

    normal_vec = [np.cos(np.radians(viewX)), np.sin(np.radians(viewX))]
    cos_tile = np.dot(to_check_tile_vec, normal_vec) / (np.linalg.norm(to_check_tile_vec) * np.linalg.norm(normal_vec))
    tile_ang = np.degrees(np.arccos(cos_tile))
    return True if tile_ang < 120 / 2 else False


def _bfs(team_player_info: List[FramePlayerInfo], team_tile: List[int], max_depth=8):
    team_vision_collection: List[OnePlayerVisionCollection] = []
    for idx, player in enumerate(team_player_info):
        current_player_pos: PlayerPos = player.player_pos
        current_player_viewX: float = player.player_viewX
        current_player_tile: TileID = team_tile[idx]

        start_depth = 0
        to_visit_tiles = deque([(current_player_tile, start_depth)])
        visited_tiles = set()

        # one player's vision collection
        individual_vision_collection: OnePlayerVisionCollection = []

        # starting bfs from the start tile only when player is alive in that frame
        while to_visit_tiles and team_tile[idx]:
            search_tile, current_depth = to_visit_tiles.popleft()
            if (search_tile not in visited_tiles) and (current_depth < max_depth):
                visited_tiles.add(search_tile)

                neighbors = neighbors_dict[search_tile]

                if not list(neighbors_dict[search_tile]):
                    closest_neighbors = find_closest_neighbors(search_tile, MAPINFO.mapName, neighborNum=5)
                    neighbors = closest_neighbors

                if _is_tile_in_view(current_player_pos, current_player_viewX, search_tile):
                    individual_vision_collection.append(BfsTileInfo(search_tile, current_depth))

                for neighbor in neighbors:
                    if neighbor not in visited_tiles:
                        to_visit_tiles.append((neighbor, current_depth + 1))

        team_vision_collection.append(individual_vision_collection)

    return team_vision_collection


def get_holistic_version_collection(_searcher_team_info: List[FramePlayerInfo],
                                    _searchee_team_info: List[FramePlayerInfo]):
    searcher_frame_player_pos: List[PlayerPos] = [info.player_pos for info in _searcher_team_info]
    searcher_team_tile: List[int] = get_team_tile(searcher_frame_player_pos, MAPINFO.mapName)

    searchee_frame_player_pos: List[PlayerPos] = [info.player_pos for info in _searchee_team_info]
    searchee_team_tile: List[int] = get_team_tile(searchee_frame_player_pos, MAPINFO.mapName)

    # dead player's start tile is marked as -1
    searcher_team_tile = [0 if _searcher_team_info[idx].player_hp == 0 else searcher_team_tile[idx] for idx, _ in
                          enumerate(searcher_team_tile)]
    searchee_team_tile = [0 if _searchee_team_info[idx].player_hp == 0 else searchee_team_tile[idx] for idx, _ in
                          enumerate(searchee_team_tile)]

    searcher_team_vision_collection: TeamVisionCollection = _bfs(_searcher_team_info, searcher_team_tile, max_depth=10)
    searchee_team_vision_collection: TeamVisionCollection = _bfs(_searchee_team_info, searchee_team_tile, max_depth=10)

    vision_collection = FrameTeamVisionCollection(searcher_team_vision_collection,
                                                  searchee_team_vision_collection,
                                                  searcher_team_tile,
                                                  searchee_team_tile)

    return vision_collection


def get_version_collection_details(_version_collection: List[OnePlayerVisionCollection]):
    _tile_ids = list(set([tile.tile_id for player_tiles_info in _version_collection for tile in player_tiles_info]))
    _tile_depth = list(
        set([tile.tile_depth for player_tiles_info in _version_collection for tile in player_tiles_info]))

    return _tile_ids, _tile_depth


def get_observed_opponent_version_collection(vision_collection: FrameTeamVisionCollection, _searchee_team_info: List[FramePlayerInfo]):
    searchee_team_tiles: List[int] = vision_collection.searchee_team_tile

    searcher_team_vision_collection: TeamVisionCollection = vision_collection.searcher_vision_collection
    searcher_tile_ids, _ = get_version_collection_details(searcher_team_vision_collection)

    observed_searchee_vision_collection: List[List[BfsTileInfo]] = [[] for _ in range(5)]
    for idx, player_tile_id in enumerate(searchee_team_tiles):
        if (player_tile_id != 0) and (player_tile_id in searcher_tile_ids):
            print(f"{idx} : {player_tile_id}")
            bfs_searchee_player = _bfs(_searchee_team_info, searchee_team_tiles, max_depth=10)[idx]
            bfs_searchee_tiles = [tiles_info.tile_id for tiles_info in bfs_searchee_player]
            bfs_searchee_depth = [tiles_info.tile_depth for tiles_info in bfs_searchee_player]
            for tile_id, tile_depth in zip(bfs_searchee_tiles, bfs_searchee_depth):
                observed_player_info = BfsTileInfo(tile_id, tile_depth)
                observed_searchee_vision_collection[idx].append(observed_player_info)
    return observed_searchee_vision_collection


def retrieve_framePosInfo(matchID: ObjectId, roundNum: int, frame: int, team: Literal["team1", "team2"]):
    # map_name: str = database.Match.objects(id=matchID)[0].mapName
    frame_team_info = database.Frame.objects(matchID=matchID, roundNum=roundNum)[frame][team + "FrameDict"]
    team_name = frame_team_info.teamName
    frame_player_dic = frame_team_info.playerFrameDict
    team_player_name = [one_player_info.playerName for one_player_info in frame_player_dic]

    team_player_pos: List[PlayerPos] = [
        _position_scaling(one_player_info.playerX, one_player_info.playerY, one_player_info.playerZ, "player")
        for one_player_info in frame_player_dic]

    # do not know what happen, but multiplying by -1 modifies the direction
    team_player_viewX = [-1 * one_player_info.viewX for one_player_info in frame_player_dic]

    team_player_hp = [one_player_info.hp for one_player_info in frame_player_dic]

    frame_player_info: List[FramePlayerInfo] = [FramePlayerInfo(name, pos, viewX, hp)
                                                for name, pos, viewX, hp in zip(team_player_name,
                                                                                team_player_pos,
                                                                                team_player_viewX,
                                                                                team_player_hp)]

    return FrameTeamInfo(team_name,
                         frame_player_info)


def get_roundFrame(matchID: ObjectId, roundNum: int):
    connect_db()
    frame_team_info = database.Frame.objects(matchID=matchID, roundNum=roundNum)
    return len(frame_team_info)


def retrieve_match_info(matchID: ObjectId):
    connect_db()
    match = database.Match.objects(id=matchID)
    map_name = match[0].mapName
    return map_name


"""
def make_gif(_currentMatchID, _currentRound):
    roundTotalFrame = get_roundFrame(_currentMatchID, _currentRound)

    for i in tqdm(range(roundTotalFrame)):
        _searcher_team_frame_pos: FrameTeamInfo = retrieve_framePosInfo(matchID=_currentMatchID, roundNum=_currentRound,
                                                                        frame=i, team="team1")
        _searchee_team_frame_pos: FrameTeamInfo = retrieve_framePosInfo(matchID=_currentMatchID, roundNum=_currentRound,
                                                                        frame=i, team="team2")

        searcher_player_info: List[FramePlayerInfo] = _searcher_team_frame_pos.team_player_info
        searchee_player_info: List[FramePlayerInfo] = _searchee_team_frame_pos.team_player_info

        team_tiles_info: List[OnePlayerVisionCollection] = get_version_collection(searcher_player_info, searchee_player_info)
        # searchee_tiles_info[0] -> tile index, searchee_tiles_info[1] -> tile depth

        _tile_ids = [tile.tile_id for player_tiles_info in team_tiles_info for tile in player_tiles_info]
        _fig = visualizer.draw_block(_tile_ids, searcher_player_info)
        img_data = BytesIO()
        _fig.savefig(img_data, format='png')
        img_data.seek(0)

        frames.append(imageio.v2.imread(img_data))
        plt.close()

    imageio.mimsave(output_path, frames, duration=300)
"""

output_path = f'output{0}.gif'
frames = []
visualizer = FrameVisualizer()

currentMatchID = ObjectId("656c9a14a038bfba3be1021d")
MAPINFO.mapName = retrieve_match_info(currentMatchID)
currentRound = 0

# make_gif(currentMatchID, currentRound)
searcher_team_frame_pos: FrameTeamInfo = retrieve_framePosInfo(matchID=currentMatchID, roundNum=currentRound,
                                                               frame=55, team="team1")
searchee_team_frame_pos: FrameTeamInfo = retrieve_framePosInfo(matchID=currentMatchID, roundNum=currentRound,
                                                               frame=55, team="team2")

searcher_team_info: List[FramePlayerInfo] = searcher_team_frame_pos.team_player_info
searchee_team_info: List[FramePlayerInfo] = searchee_team_frame_pos.team_player_info

version_collection: FrameTeamVisionCollection = get_holistic_version_collection(searcher_team_info, searchee_team_info)

tile_ids, depth = get_version_collection_details(version_collection.searcher_vision_collection)

fig = visualizer.draw_block(tile_ids, searcher_team_info)
plt.show()

observed_searchee_team_info: TeamVisionCollection = get_observed_opponent_version_collection(version_collection, searchee_team_info)
version_collection.searchee_vision_collection = observed_searchee_team_info

print(version_collection.searcher_team_tile)
print(version_collection.searcher_vision_collection)
print(version_collection.searchee_team_tile)
print(version_collection.searchee_vision_collection)

# roundTotalFrame = get_roundFrame(currentMatchID, currentRound)
# for i in range(roundTotalFrame):
#     searcher_team_frame_pos: FrameTeamInfo = retrieve_framePosInfo(matchID=currentMatchID, roundNum=currentRound,
#                                                                    frame=i, team="team1")
#     searchee_team_frame_pos: FrameTeamInfo = retrieve_framePosInfo(matchID=currentMatchID, roundNum=currentRound,
#                                                                    frame=i, team="team2")
#
#     searcher_team_info: List[FramePlayerInfo] = searcher_team_frame_pos.team_player_info
#     searchee_team_info: List[FramePlayerInfo] = searchee_team_frame_pos.team_player_info
#
#     version_collection: FrameTeamVisionCollection = get_version_collection(searcher_team_info, searchee_team_info)
#
#     tile_ids, depth = get_version_collection_info(version_collection.searcher_vision_collection)
#
#     # fig = visualizer.draw_block(tile_ids, searcher_team_info)
#     # plt.show()
#
#     parse_version_collection(version_collection, searchee_team_info)
#     print(f"{i} frame")
