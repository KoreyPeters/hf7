import os
import time

import google.api_core.exceptions
import orjson
import pendulum
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

client = None


def default(obj):
    if isinstance(obj, pendulum.DateTime):
        return obj.to_rfc3339_string()


def create_task(queue_name, task_name, data, delay_minutes=0):
    global client
    if not client:
        client = tasks_v2.CloudTasksClient()
    max_retries = 5
    attempt = 1
    successful = False
    scheduled_task_time = timestamp_pb2.Timestamp()
    scheduled_task_time.FromDatetime(
        pendulum.now() + pendulum.duration(minutes=delay_minutes)
    )

    while not successful and attempt < max_retries:
        try:
            client.create_task(
                request={
                    "parent": client.queue_path(
                        "human-flourishing-4", "us-central1", queue_name
                    ),
                    "task": {
                        "http_request": {
                            "http_method": tasks_v2.HttpMethod.POST,
                            "url": f"{os.environ['CURRENT_HOST']}/tasks/{queue_name}/",
                            "headers": {
                                "Content-Type": "application/json",
                                "x-api-key": os.environ["drf-token"],
                                "body": orjson.dumps(data, default=default),
                            },
                        },
                        "name": client.task_path(
                            "human-flourishing-4", "us-central1", queue_name, task_name
                        ),
                        "schedule_time": scheduled_task_time,
                    },
                }
            )
            successful = True
        except google.api_core.exceptions.ServiceUnavailable as e:
            attempt += 1
            if attempt <= max_retries:
                time.sleep(1)
            else:
                raise e
        except google.api_core.exceptions.AlreadyExists:
            pass
