#!/usr/bin/env python3
import json
import os
from datetime import datetime
import requests

from .query_templating import get_query_template

DATA_DIR = "data"


def get_data_dict():
    template_dict = get_query_template()

    response = requests.post(
        "http://shop.koralldata.se/WebServiceDispatcher.wso/CallAction/JSON",
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
            "Accept": "*/*",
            "Accept-Language": "sv-SE,sv;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "http://shop.koralldata.se/index.html?ID=SKANSTULL",
            "Content-Type": "application/json",
            "Origin": "http://shop.koralldata.se",
            "Connection": "keep-alive",
            "Cookie": "dfWebApp=D022FE1D-2A68-4E92-8318-588204DCCC7B",
        },
        json=template_dict,
    )

    if response.status_code != 200:
        raise Exception((response.status_code, response.text))

    return response.json()


def get_tire_names(data_dict) -> list[str]:
    tires = data_dict["Header"]["aActions"][1]["tData"]["c"]
    assert isinstance(tires, list), tires

    return [tire_data["c"][2]["c"][0]["c"][0]["v"] for tire_data in tires]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    data_dict = get_data_dict()

    raw_path = os.path.join(DATA_DIR, "raw_tire_data.json")
    if os.path.exists(raw_path):
        backup_path = raw_path + ".bak"
        os.replace(raw_path, backup_path)
        print(f"Backed up previous {raw_path} -> {backup_path}")

    with open(raw_path, "w") as f:
        f.write(json.dumps(data_dict, indent=4))

    tire_names: list[str] = get_tire_names(data_dict)
    print("\n".join(tire_names))

    date_str = datetime.now().strftime("%Y-%m-%d__%H_%M")

    filename = os.path.join(DATA_DIR, f"tire_names_{date_str}.txt")
    with open(filename, "w") as f:
        f.write("\n".join(tire_names))
    print(f"Wrote {len(tire_names)} lines of tyre data to {filename}")


if __name__ == "__main__":
    main()
