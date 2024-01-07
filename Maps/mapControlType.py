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
    TileDistance, TileID)

from Maps import area_json, neighbors_dict
from plot import FrameVisualizer

map_scale_parameter = {"pos_x": -2087.0, "pos_y": 3870.0, "scale": 4.9}


def connect_db():
    return mongo.connect(db="csgo", username="lihong", password="1998918!", host="localhost", port=27017)


def _position_scaling(x: float, y: float, z: float, data: Literal["player", "tile"]):
    """
    scale the coordinates from the original dataset.
    :param data: the processed data type, "player" pos or "tile" pos.
    :return: a PlayerPos object with the scaled coordinates: x,y,z.
    """
    scaled_x = (x - map_scale_parameter["pos_x"]) / map_scale_parameter["scale"]
    scaled_y = (map_scale_parameter["pos_y"] - y) / map_scale_parameter["scale"]
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
    center: TilePos = _get_area_center("de_inferno", search_tile)
    to_check_tile_vec = np.array([center.x - player_pos.x, center.y - player_pos.y])

    normal_vec = [100 * np.cos(np.radians(viewX)), 100 * np.sin(np.radians(viewX))]
    cos_tile = np.dot(to_check_tile_vec, normal_vec) / (np.linalg.norm(to_check_tile_vec) * np.linalg.norm(normal_vec))
    tile_ang = np.degrees(np.arccos(cos_tile))
    return True if tile_ang < 140 / 2 else False


def bfs(team_player_info: List[FramePlayerInfo], max_depth: int):
    frame_player_pos: List[PlayerPos] = [info.player_pos for info in team_player_info]
    team_tile = get_team_tile(frame_player_pos, "de_inferno")

    player_blocks: List[List[TileID]] = []
    for idx, player in enumerate(team_player_info):
        current_player_pos: PlayerPos = player.player_pos
        current_player_viewX: float = player.player_viewX
        current_player_tile: TileID = team_tile[idx]

        start_depth = 0
        to_visit_tiles = deque([(current_player_tile, start_depth)])
        visited_tiles = set()
        plot_block: List[TileID] = []

        while to_visit_tiles:
            search_tile, current_depth = to_visit_tiles.popleft()
            if (search_tile not in visited_tiles) and (current_depth < max_depth):
                visited_tiles.add(search_tile)

                neighbors = neighbors_dict[search_tile]

                if len(list(neighbors_dict[search_tile])) == 0:
                    closest_neighbors = find_closest_neighbors(search_tile, "de_inferno", neighborNum=5)
                    neighbors = closest_neighbors

                if _is_tile_in_view(current_player_pos, current_player_viewX, search_tile):
                    plot_block.append(search_tile)

                for neighbor in neighbors:
                    if neighbor not in visited_tiles:
                        to_visit_tiles.append((neighbor, current_depth + 1))

        player_blocks.append(plot_block)

    return player_blocks


def retrieve_framePosInfo(matchID: ObjectId, roundNum: int, frame: int, team: Literal["team1", "team2"]):
    # map_name: str = database.Match.objects(id=matchID)[0].mapName
    connect_db()
    frame_team_info = database.Frame.objects(matchID=matchID, roundNum=roundNum)[frame][team + "FrameDict"]
    team_name = frame_team_info.teamName
    frame_player_dic = frame_team_info.playerFrameDict
    team_player_name = [one_player_info.playerName for one_player_info in frame_player_dic]

    team_player_pos: List[PlayerPos] = [
        _position_scaling(one_player_info.playerX, one_player_info.playerY, one_player_info.playerZ, "player")
        for one_player_info in frame_player_dic]

    team_player_viewX = [one_player_info.viewX for one_player_info in frame_player_dic]

    frame_player_info: List[FramePlayerInfo] = [FramePlayerInfo(name, pos, viewX)
                                                for name, pos, viewX in
                                                zip(team_player_name, team_player_pos, team_player_viewX)]

    return FrameTeamInfo(team_name,
                         frame_player_info)


output_path = f'output{0}.gif'
frames = []
visualizer = FrameVisualizer()
for i in tqdm(range(101)):
    frame_pos_info = retrieve_framePosInfo(ObjectId("656c9a14a038bfba3be1021d"), 0, i, "team1")

    player_info: List[FramePlayerInfo] = frame_pos_info.team_player_info
    plot_pos = [[player.player_pos.x, player.player_pos.y] for player in player_info]
    plot_viewX = [player.player_viewX for player in player_info]
    searched_tiles = bfs(player_info, 8)

    fig = visualizer.draw_block(searched_tiles, plot_pos, plot_viewX)
    img_data = BytesIO()
    fig.savefig(img_data, format='png')
    img_data.seek(0)

    frames.append(imageio.v2.imread(img_data))
    plt.close()

imageio.mimsave(output_path, frames, duration=300)
