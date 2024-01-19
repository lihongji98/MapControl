from collections import defaultdict

import pandas as pd
import numpy as np
import networkx as nx
from scipy.spatial import distance


def transform_csv_to_json(sample_csv: pd.DataFrame):
    final_dic = {}
    for cur_map in sample_csv["mapName"].unique():
        map_dic = {}
        for i in sample_csv[sample_csv["mapName"] == cur_map].index:
            cur_tile = sample_csv.iloc[i]
            cur_dic = {
                cur_feature: cur_tile[cur_feature]
                for cur_feature in sample_csv.columns
                if cur_feature not in ["mapName", "areaId"]
            }
            map_dic[cur_tile["areaId"]] = cur_dic  # type: ignore[assignment]
        final_dic[cur_map] = map_dic
    return final_dic


def create_nav_graphs(nav):
    nav_graphs: dict[str, nx.DiGraph] = {}
    for map_name in nav:
        if map_name == 'de_inferno':
            map_graph = nx.DiGraph()
            for area_id in nav[map_name]:
                area = nav[map_name][area_id]
                map_graph.add_nodes_from(
                    [
                        (
                            area_id,
                            {
                                "mapName": map_name,
                                "areaID": area_id,
                                "areaName": area["areaName"],
                                "northWestX": area["northWestX"],
                                "northWestY": area["northWestY"],
                                "northWestZ": area["northWestZ"],
                                "southEastX": area["southEastX"],
                                "southEastY": area["southEastY"],
                                "southEastZ": area["southEastZ"],
                                "center": [
                                    (area["northWestX"] + area["southEastX"]) / 2,
                                    (area["northWestY"] + area["southEastY"]) / 2,
                                    (area["northWestZ"] + area["southEastZ"]) / 2,
                                ],
                                "size": np.sqrt(
                                    (area["northWestX"] - area["southEastX"]) ** 2
                                    + (area["northWestY"] - area["southEastY"]) ** 2
                                    + (area["northWestZ"] - area["southEastZ"]) ** 2
                                ),
                            },
                        ),
                    ]
                )
            with open(
                    "./mapMetaData/de_inferno.txt", encoding="utf8"
            ) as edge_list:
                edge_list_lines = edge_list.readlines()
            for line in edge_list_lines:
                areas = line.strip().split(",")
                map_graph.add_edge(
                    int(areas[0]),
                    int(areas[1]),
                    weight=distance.euclidean(
                        map_graph.nodes[int(areas[0])]["center"],
                        map_graph.nodes[int(areas[1])]["center"],
                    ),
                )
            nav_graphs[map_name] = map_graph
    return nav_graphs


def graph_to_tile_neighbors(neighbor_pairs):
    tile_to_neighbors = defaultdict(set)

    for tile_1, tile_2 in neighbor_pairs:
        tile_to_neighbors[tile_1].add(tile_2)
        tile_to_neighbors[tile_2].add(tile_1)

    return tile_to_neighbors


AREA_CSV = pd.read_csv(r"./mapMetaData/area_info.csv")
AREA_CSV.areaName = AREA_CSV.areaName.fillna("")
area_json = transform_csv_to_json(AREA_CSV)
mapGraph = create_nav_graphs(area_json)
neighbors_dict = graph_to_tile_neighbors(list(mapGraph["de_inferno"].edges))
