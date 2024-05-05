from aws_cdk import (
    Duration,
    CfnOutput,
    Stack,
    aws_dynamodb as ddb,
    aws_lambda as _lambda,
    aws_ecr_assets as ecr_assets,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as apigwv2_integrations
)
from constructs import Construct
from aws_cdk import aws_lambda


class TodoInfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ddb_table = ddb.Table(
            self, "Tasks",
            partition_key=ddb.Attribute(
                name="task_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute="ttl"
        )

        ddb_table.add_global_secondary_index(
            index_name="user-index",
            partition_key=ddb.Attribute(
                name="user_id", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="created_time",
                                   type=ddb.AttributeType.NUMBER)
        )

        # api = _lambda.Function(
        #     self, "API",
        #     runtime=_lambda.Runtime.PYTHON_3_12,
        #     handler="todo.handler",
        #     code=_lambda.Code.from_asset("../api"),
        #     environment={
        #         "TABLE_NAME": ddb_table.table_name
        #     }
        # )

        api = _lambda.DockerImageFunction(
            self, "API",
            code=_lambda.DockerImageCode.from_image_asset(
                "../api", platform=ecr_assets.Platform.LINUX_ARM64),
            memory_size=1024,
            timeout=Duration.seconds(300),
            architecture=_lambda.Architecture.ARM_64,
            environment={
                "TABLE_NAME": ddb_table.table_name
            }
        )

        functionUrl = api.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.AWS_IAM,
            cors=aws_lambda.FunctionUrlCorsOptions(
                allowed_origins=["*"],
                allowed_methods=[aws_lambda.HttpMethod.ALL],
                allowed_headers=["*"]
            )
        )

        ddb_table.grant_read_write_data(api)

        apigw = apigwv2.HttpApi(
            self, id="api_gw", api_name="todo_api")

        apigw.add_routes(
            path="/",
            methods=[apigwv2.HttpMethod.GET],
            integration=apigwv2_integrations.HttpLambdaIntegration(
                "inventoryapi_lambda_integration", api)
        )
        apigw.add_routes(
            path="/create-task",
            methods=[apigwv2.HttpMethod.PUT],
            integration=apigwv2_integrations.HttpLambdaIntegration(
                "inventoryapi_lambda_integration", api)
        )

        apigw.add_routes(
            path="/get-task/{task_id}",
            methods=[apigwv2.HttpMethod.GET],
            integration=apigwv2_integrations.HttpLambdaIntegration(
                "inventoryapi_lambda_integration", api)
        )

        apigw.add_routes(
            path="/list-tasks/{user_id}",
            methods=[apigwv2.HttpMethod.GET],
            integration=apigwv2_integrations.HttpLambdaIntegration(
                "inventoryapi_lambda_integration", api)
        )

        apigw.add_routes(
            path="/update-task",
            methods=[apigwv2.HttpMethod.PUT],
            integration=apigwv2_integrations.HttpLambdaIntegration(
                "inventoryapi_lambda_integration", api)
        )

        apigw.add_routes(
            path="/delete-task/{task_id}",
            methods=[apigwv2.HttpMethod.DELETE],
            integration=apigwv2_integrations.HttpLambdaIntegration(
                "inventoryapi_lambda_integration", api)
        )

        apigw.add_routes(
            path="/docs",
            methods=[apigwv2.HttpMethod.ANY],
            integration=apigwv2_integrations.HttpLambdaIntegration(
                "inventoryapi_lambda_integration", api)
        )

        apigw.add_routes(
            path="/openapi.json",
            methods=[apigwv2.HttpMethod.GET],
            integration=apigwv2_integrations.HttpLambdaIntegration(
                "inventoryapi_lambda_integration", api)
        )

        apigw.add_stage(
            id="dev",
            stage_name="dev",
            auto_deploy=True,
        )

        CfnOutput(
            self,
            "API Url",
            value=functionUrl.url
        )
        CfnOutput(
            self,
            "APIGWURL",
            value=apigw.api_endpoint)
