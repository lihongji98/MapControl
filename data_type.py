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
    which are :
    player_name, player_pos, player_viewX
    """
    player_name: str
    player_pos: PlayerPos
    player_viewX: float


@dataclass
class FrameTeamInfo:
    """
    a dataclass containing team's basic frame information.
    """
    team_name: str
    team_player_info: List[FramePlayerInfo]


TileDistance: TypeAlias = tuple[int, float]

TileID: TypeAlias = int
