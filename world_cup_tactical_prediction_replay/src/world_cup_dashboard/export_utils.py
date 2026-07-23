import json
def json_bytes(value):return json.dumps(value,ensure_ascii=False,indent=2).encode("utf-8")

