from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_sns as sns,
    aws_lambda,
    aws_sns_subscriptions as subscriptions,
    aws_iam as iam,
    aws_apigateway as apigateway,
    CfnOutput,
    Stack,
)
from constructs import Construct


class EcsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "EcsPocVpc", max_azs=2)

        cluster = ecs.Cluster(self, "EcsPocCluster", vpc=vpc)

        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "EcsPocFargateService",
            cluster=cluster,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry(
                    "amazon/amazon-ecs-sample")
            ),
            desired_count=1,
            public_load_balancer=True,
        )

        cluster_arn = fargate_service.cluster.cluster_arn
        service_arn = fargate_service.service.service_arn

        CfnOutput(
            self,
            "EcsPocLoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name,
        )

        # Lambda + API Gateway
        # Import an existing SNS topic provided an ARN.
        topic = sns.Topic.from_topic_arn(
            self,
            "EcsPocSnsTopic",
            "arn:aws:sns:us-west-2:093575270853:SnsStack-SnsTopic2C1570A4-vQxMRmZoFWHQ",
        )

        update_function = aws_lambda.Function(
            self,
            "EcsPocUpdateFunction",
            function_name="EcsPocUpdateFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_asset("function"),
            handler="update.handler",
            vpc=vpc,
            environment={
                "CLUSTER_ARN": cluster_arn,
                "SERVICE_ARN": service_arn,
            }
        )

        read_function = aws_lambda.Function(
            self,
            "EcsPocReadFunction",
            function_name="EcsPocReadFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_asset("function"),
            handler="read.handler",
            vpc=vpc,
            environment={
                "CLUSTER_ARN": cluster_arn,
                "SERVICE_ARN": service_arn,
            }
        )

        topic.add_subscription(
            subscriptions.LambdaSubscription(update_function))

        ecsPermissions = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],
            actions=["ecs:UpdateService", "ecs:DescribeServices"],
        )

        update_function.add_to_role_policy(ecsPermissions)
        read_function.add_to_role_policy(ecsPermissions)

        apigateway.LambdaRestApi(
            self,
            "EcsReadAPI",
            handler=read_function,
            endpoint_configuration=apigateway.EndpointConfiguration(
                types=[apigateway.EndpointType.PRIVATE]),
            policy=iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=['execute-api:Invoke'],
                        principals=[iam.StarPrincipal()],
                        resources=['execute-api:/*/*/*'],
                    ),
                    iam.PolicyStatement(
                        effect=iam.Effect.DENY,
                        principals=[iam.StarPrincipal()],
                        actions=['execute-api:Invoke'],
                        resources=['execute-api:/*/*/*'],
                        conditions={
                            'StringNotEquals': {
                                "aws:sourceVpce": 'vpce-0ff79e86f67595ca1'
                            }
                        }
                    )
                ]
            )
        )
