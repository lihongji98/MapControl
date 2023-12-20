from awpy import DemoParser


def demo_parse(candidate_demo_file, candidate_demo_id, demo_parse_rate=64):
    demo_parser = DemoParser(
        demofile=candidate_demo_file,
        demo_id=candidate_demo_id,
        parse_rate=demo_parse_rate)  # 64tick -> 2 Hz sampling frequency

    print("========= parsing ============")
    data = demo_parser.parse(return_type='df')
    print("======== parse completed ==========")

    return data

