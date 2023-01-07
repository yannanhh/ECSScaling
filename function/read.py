import boto3
import json


def handler(event, context):
    ecs = boto3.client("ecs")

    try:
        response = ecs.describe_services(
            cluster="arn:aws-cn:ecs:cn-northwest-1:425039140189:cluster/EcsStack-EcsPocCluster08C3EA8A-LP8qIBbIc9So",
            services=["EcsStack-EcsPocFargateService6F213248-eCS49Dp66DZi"],
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