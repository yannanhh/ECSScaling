import boto3
import json
import os


def handler(event, context):
    ecs = boto3.client("ecs")

    CLUSTER_ARN = os.getenv("CLUSTER_ARN")
    SERVICE_ARN = os.getenv("SERVICE_ARN")

    try:
        ecs_task_desired_count = int(event["Records"][0]["Sns"]["Message"])
        print(ecs_task_desired_count)
        if ecs_task_desired_count > 0 and ecs_task_desired_count <= 3:
            ecs.update_service(
                cluster=CLUSTER_ARN,
                service=SERVICE_ARN,
                desiredCount=ecs_task_desired_count,
            )

    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": json.dumps({"message": "Update failed"})}

    return {
        "statusCode": 200,
        "body": json.dumps({"desiredCount": ecs_task_desired_count}),
    }
