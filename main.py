import json
from json_parse import JsonParser
import pandas as pd
from demo_parser import demo_parse

if __name__ == '__main__':
    # Set the parse_rate equal to the tick rate at which you would like to parse the frames of the demo.
    # This parameter only matters if parse_frames=True ()
    # For reference, MM demos are usually 64 ticks, and pro/FACEIT demos are usually 128 ticks.
    json_parser = JsonParser()
    json_parser.parse(r"D:\PGL-Major-Antwerp-2022-faze-vs-natus-vincere-m1.json ")
    json_parser.update()
