from dataclasses import dataclass
from typing import List, TypeAlias


@dataclass
class PlayerPos:
    """
    player position: x,y,z
    """
    x: float
    y: float
    z: float


@dataclass
class TilePos:
    """
    tile coordinate: x,y,z
    """
    x: float
    y: float
    z: float


@dataclass
class FramePlayerInfo:
    """
    a dataclass containing player's basic frame information,
    List[player_name, player_pos, player_viewX, player_hp]
    """
    player_name: str
    player_pos: PlayerPos
    player_viewX: float
    player_hp: int


@dataclass
class FrameTeamInfo:
    """
    a dataclass containing team's basic frame information.
    List[FrameTeamInfo]
    """
    team_name: str
    team_player_info: List[FramePlayerInfo]


@dataclass
class TeamStateInfo:
    searcher_team_info: List[FramePlayerInfo]
    searchee_team_info: List[FramePlayerInfo]


@dataclass
class BFSTileInfo:
    """
    a dataclass containing tile's basic frame information: tile_id, tile_depth
    """
    tile_id: int
    tile_depth: float


TileDistance: TypeAlias = tuple[int, float]

TileID: TypeAlias = int

OnePlayerVisionCollection: TypeAlias = List[BFSTileInfo]
TeamVisionCollection: TypeAlias = List[OnePlayerVisionCollection]


@dataclass
class FrameTeamVisionCollection:
    """
    a dataclass containing both 2 teams' vision collection information:
    1.team_vision_collection: List[List[tile_id, tile_depth]]
    2.current_player_location: List[tile_id]
    """
    searcher_vision_collection: TeamVisionCollection
    searchee_vision_collection: TeamVisionCollection

    searcher_team_tile: List[TileID]
    searchee_team_tile: List[TileID]


@dataclass
class AreaCenterCoordinate:
    x: float
    y: float
    z: float


@dataclass
class FourAreaTiles:
    TSpawn: int
    CTSpawn: int
    BombsiteA: int
    BombsiteB: int
