#!/usr/bin/env python3
import json
from datetime import datetime
import requests

from query_templating import get_query_template


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
            "Cookie": "dfWebApp=1E0B667E-4911-4A31-837A-B07DD79D50D9",
        },
        json=template_dict,
    )

    if response.status_code != 200:
        raise Exception((response.status_code, response.text))

    return response.json()


def get_tire_names(data_dict) -> list[str]:
    breakpoint()
    tires = data_dict["Header"]["aActions"][1]["tData"]["c"]
    assert isinstance(tires, list), tires

    return [tire_data["c"][2]["c"][0]["c"][0]["v"] for tire_data in tires]


def main():
    data_dict = get_data_dict()

    with open("raw_tire_data.json", "w") as f:
        f.write(json.dumps(data_dict, indent=4))

    tire_names: list[str] = get_tire_names(data_dict)
    print("\n".join(tire_names))

    date_str = datetime.now().strftime("%Y-%m-%d__%H_%M")

    with open(filename := f"tire_names_{date_str}.txt", "w") as f:
        f.write("\n".join(tire_names))
    print(f"Wrote {len(tire_names)} lines of tyre data to {filename}")


if __name__ == "__main__":
    main()
