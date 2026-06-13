import json

def parse_database(file_path):
    """read a cloudtrail JSONL file and return normalized events."""
    events = []
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            events.append(normalize_event(raw))
    return events

def normalize_event(raw:dict) -> dict:
    """extract secuity-relevant fields from a raw CloudTrail record."""
    identity = raw.get("userIdentity", {})
    # determine who did this
    if identity.get("type") == "AssumedRole":
        user = identity.get("sessionContext", {}).get("sessionIssuer", {}).get("userName", "unknown")
        principle_type = "AssumedRole"
    elif identity.get("type") == "AWSService":
        user = identity.get("invokedBy", "aws-service")
        principle_type = "AWSService"
    else:
        user = identity.get("userName", "unknown")
        principle_type = identity.get("type", "unknown")
    return {
        "timestamp": raw.get("@timestamp"),
        "event_name": raw.get("eventName"),
        "event_source": raw.get("eventSource").replace(".amazonaws.com", ""),
        "source_ip": raw.get("sourceIPAddress"),
        "user": user,
        "principle_type": principle_type,
        "region": raw.get("awsRegion"),
        "user_agent": raw.get("userAgent", ""),
        "request_params": json.dumps(raw.get("requestParameters")),
        "resources": json.dumps(raw.get("resources", [])),
    }