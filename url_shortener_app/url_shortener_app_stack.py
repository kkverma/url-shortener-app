from aws_cdk import (
    RemovalPolicy,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_ec2 as ec2,
    aws_elasticache as elasticache,
    aws_secretsmanager as secretsmanager
)
from constructs import Construct

class UrlShortenerAppStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Create a VPC with public subnets
        vpc = ec2.Vpc(self, "VPC",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(name="public",subnet_type=ec2.SubnetType.PUBLIC,cidr_mask=24),
                ec2.SubnetConfiguration(name="private",subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,cidr_mask=24)
            ]
        )

        # Security Group for ElastiCache
        cache_security_group = ec2.SecurityGroup(self, "CacheSG",
            vpc=vpc,
            description="Allow traffic to ElastiCache",
            allow_all_outbound=True
        )
        cache_security_group.node.add_dependency(vpc)
        cache_security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(6379),
            description="Allow Redis traffic from anywhere"
        )
        private_subnets_ids = [ps.subnet_id for ps in vpc.private_subnets]
        cache_subnet_group = elasticache.CfnSubnetGroup(
            scope=self,
            id="redis_subnet_group",
            subnet_ids=private_subnets_ids,  # todo: add list of subnet ids here
            description="subnet group for redis"
        )

        # Define DynamoDB Table
        table = dynamodb.Table(
            self, "URLMappingsTable",
            partition_key=dynamodb.Attribute(name="shortUrl", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Define ElastiCache Cluster (Redis)
        redis_cache = elasticache.CfnCacheCluster(
            self, "RedisCache",
            cache_node_type="cache.t3.micro",
            engine="redis",
            num_cache_nodes=1,
            vpc_security_group_ids=[cache_security_group.security_group_id],
            cache_subnet_group_name=cache_subnet_group.ref
        )
        redis_cache.node.add_dependency(cache_security_group)
        redis_cache.node.add_dependency(vpc)

        # Define Lambda Layer
        lambda_layer = _lambda.LayerVersion(self, f'SharedLambdaLayer',
            code=_lambda.Code.from_asset("./assets/lambda_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="A layer to include third party library package"
        )
        # Define Lambda Functions
        shorten_lambda = _lambda.Function(
            self, "ShortenURLFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="shorten_lambda.lambda_handler",
            code=_lambda.Code.from_asset("./assets/lambda"),
            environment={
                "TABLE_NAME": table.table_name,
                "REDIS_ENDPOINT": redis_cache.attr_redis_endpoint_address,
                "REDIS_PORT": redis_cache.attr_redis_endpoint_port
            },
            layers=[lambda_layer]
        )
        
        redirect_lambda = _lambda.Function(
            self, "RedirectFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="redirect_lambda.lambda_handler",
            code=_lambda.Code.from_asset("./assets/lambda"),
            environment={
                "TABLE_NAME": table.table_name,
                "REDIS_ENDPOINT": redis_cache.attr_redis_endpoint_address,
                "REDIS_PORT": redis_cache.attr_redis_endpoint_port
            },
            layers=[lambda_layer]
        )
        
        stats_lambda = _lambda.Function(
            self, "StatsFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="stats_lambda.lambda_handler",
            code=_lambda.Code.from_asset("./assets/lambda"),
            environment={
                "TABLE_NAME": table.table_name
            },
            layers=[lambda_layer]
        )

        # Grant Lambda functions permissions to access DynamoDB
        table.grant_read_write_data(shorten_lambda)
        table.grant_read_write_data(redirect_lambda)
        table.grant_read_data(stats_lambda)

        # Define API Gateway
        api = apigateway.RestApi(self, "URLShortenerAPI",
            rest_api_name="URL Shortener Service",
            description="This service shortens URLs and handles redirection."
        )

        # POST /shorten
        shorten_integration = apigateway.LambdaIntegration(shorten_lambda)
        api.root.add_resource("shorten").add_method("POST", shorten_integration)

        # GET /{shortUrl}
        redirect_integration = apigateway.LambdaIntegration(redirect_lambda)
        url_resource = api.root.add_resource("{shortUrl}")
        url_resource.add_method("GET", redirect_integration)

        # GET /{shortUrl}/stats (Optional)
        stats_integration = apigateway.LambdaIntegration(stats_lambda)
        url_resource.add_resource("stats").add_method("GET", stats_integration)
