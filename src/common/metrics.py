import json
import time


def emit_metric(metric_name, value=1, unit="Count", dimensions=None):
    """Emit a CloudWatch custom metric via Embedded Metric Format (EMF).
    CloudWatch Logs automatically parses this structure into real metrics —
    no extra API calls, no extra cost beyond normal log ingestion."""
    dimensions = dimensions or {}
    emf_log = {
        "_aws": {
            "Timestamp": int(time.time() * 1000),
            "CloudWatchMetrics": [
                {
                    "Namespace": "EventTicketingSystem",
                    "Dimensions": [list(dimensions.keys())] if dimensions else [[]],
                    "Metrics": [{"Name": metric_name, "Unit": unit}],
                }
            ],
        },
        metric_name: value,
        **dimensions,
    }
    print(json.dumps(emf_log))
