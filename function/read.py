import boto3
import json
import os


def handler(event, context):
    ecs = boto3.client("ecs")

    CLUSTER_ARN = os.getenv("CLUSTER_ARN")
    SERVICE_ARN = os.getenv("SERVICE_ARN")

    try:
        response = ecs.describe_services(
            cluster=CLUSTER_ARN,
            service=SERVICE_ARN,
        )

        desired_count = response["services"][0]["desiredCount"]
        running_count = response["services"][0]["runningCount"]
        print(desired_count)
        print(running_count)

    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": json.dumps({"message": "Read failed"})}

    return {
        "statusCode": 200,
        "body": json.dumps({"desiredCount": desired_count, "runningCount": running_count}),
    }
