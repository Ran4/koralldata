import json
import os

# Captured request body from a live Koralldata session (Firefox devtools ->
# the POST to WebServiceDispatcher.wso/CallAction/JSON when clicking "Visa
# artiklarna"). To refresh after the session expires, just paste a new capture
# into requestbody.json — no code changes needed.
REQUEST_BODY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "requestbody.json"
)


def get_query_template():
    with open(REQUEST_BODY_PATH) as f:
        return json.load(f)
