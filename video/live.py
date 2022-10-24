import requests
import json
from video.helpers.integration_config import options

def get_live_stream_info(options):
    headers = {"Content-Type": "application/json"}
    mux_live = "https://api.mux.com/video/v1/live-streams"
    r = requests.get(
        mux_live, headers=headers, auth=(options["mux_token_id"], options["mux_secret"])
    )
    muxIds = []
    for ts_stream in options["mapping"]:
        muxIds.append(options["mapping"][ts_stream])
    data = None
    if r.status_code == 200:
        for liveStream in json.loads(r.text)["data"]:
            if muxIds:
                if liveStream["id"] in muxIds:
                    data = json.loads(r.text)["data"]
    else:
        data = {
            "error": "Unable to get data from mux",
            "status_code": r.status_code,
            "detail": r.text,
        }
    return data


def parse_metrics(data, options):
    streams_dict = {}
    selected_metrics = options["metrics"]
    metric_list = []
    if data:
        for live_stream in data:
            streams_dict[live_stream["id"]] = {}
            streams_dict[live_stream["id"]]["info"] = {"id": live_stream["id"]}
            for metric in selected_metrics:
                metric_struct = {
                    "name": None,
                    "value": None,
                    "type": "text",
                    "visible": True,
                    "status": 1,
                }
                metric_struct["name"] = metric
                metric_struct["value"] = live_stream[metric]
                metric_struct["type"] = "text"
                metric_struct["visible"] = True
                if metric == "playback_ids":
                    metric_struct["name"] = "Stream Policy"
                    metric_struct["value"] = live_stream[metric][0]["policy"]
                elif metric == "max_continuous_duration":
                    metric_struct["name"] = "Max Duration"
                    metric_struct["type"] = "numeric"
                else:
                    metric_struct["value"] = live_stream[metric]
                metric_list.append(metric_struct)
            streams_dict[live_stream["id"]]["metrics"] = metric_list
    else:
        print("Most probably the mapping ts:mux is not up to date")
    return streams_dict


def build_metric_group(data, options):
    e2e_dict = {}
    for entry in options["mapping"]:
        try:
            e2e_dict[entry] = {}
            e2e_dict[entry][entry] = {}
            playback_id = data[options["mapping"][entry]]["info"]["id"]
            for metric in data[options["mapping"][entry]]["metrics"]:
                if metric["name"] == "Status":
                    if metric["value"] == "active":
                        metric_group_status = 100
                    elif metric["value"] == "idle":
                        metric_group_status = 75
                    elif metric["value"] == "disabled":
                        metric_group_status = 0
            metric_group = [
                {
                    "Mux Live Stream": {
                        "status": metric_group_status,
                        "level": 1,
                        "external_links": [
                            {
                                "name": "Mux Video",
                                "url": f"https://dashboard.mux.com/organizations/hk8iqt/environments/ifqdr3/video/live-streams/{playback_id}",
                                "launch_type": "external",
                            }
                        ],
                        "metrics": data[options["mapping"][entry]]["metrics"],
                    }
                }
            ]
            e2e_dict[entry][entry] = metric_group
        except Exception as e:
            print(f"Update the mapping in the config file\n{e}")
    return e2e_dict


def validate_thresholds(data, options):
    for live_stream in data:
        for metric in data[live_stream]["metrics"]:
            for threshold in options["thresholds"]:
                for entry in threshold.keys():
                    if metric["name"] == entry:
                        if metric["name"] == "status":
                            metric["name"] = "Status"
                            if threshold[entry][metric["value"]] == "info":
                                metric.pop("status", None)
                                data[live_stream]["info"]["metric_group_status"] = 65
                            else:
                                metric["status"] = threshold[entry][metric["value"]]
                                if threshold[entry][metric["value"]] == "active":
                                    data[live_stream]["info"][
                                        "metric_group_status"
                                    ] = 100
                                elif threshold[entry][metric["value"]] == "disabled":
                                    data[live_stream]["info"]["metric_group_status"] = 0
    return data

def e2e_send(data, options):
    url = f"https://{options['ts_system']}.touchstream.global/api/rest/e2eMetrics/"
    headers = options["headers"]
    r = requests.post(url, headers=headers, data=json.dumps(data))
    print(r.status_code)
    print(r.text)

def mux_video_api_handler(mux_api, options):
    if mux_api == "live":
        liveStream_data = get_live_stream_info(options)
        metrics_info = parse_metrics(liveStream_data, options)
        validated_data = validate_thresholds(metrics_info, options)
        get_metric_group = build_metric_group(validated_data, options)
        e2e_send(get_metric_group, options)
    if mux_api == "vod":
        pass


def main():
    mux_video_api_handler("live", options)


if __name__ == "__main__":
    main()
