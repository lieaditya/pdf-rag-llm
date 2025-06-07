import * as cdk from 'aws-cdk-lib';
import { AttributeType, BillingMode, Table } from 'aws-cdk-lib/aws-dynamodb';
import { DockerImageCode, DockerImageFunction, FunctionUrlAuthType } from 'aws-cdk-lib/aws-lambda';
import { StringParameter } from 'aws-cdk-lib/aws-ssm';
import { Construct } from 'constructs';


export class RagCdkInfraStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

		// Create DynamoDB table to store the query data and results
		const ragQueryTable = new Table(this, "RagQueryTable", {
			partitionKey: { name: "query_id", type: AttributeType.STRING },
			billingMode: BillingMode.PAY_PER_REQUEST,
		});

		// Create Lambda function to handle the worker logic using Docker
		const workerImageCode = DockerImageCode.fromImageAsset("../image", {
			cmd: ["worker_handler.handler"]
		});
		const workerFunction = new DockerImageFunction(this, 'WorkerFunction', {
			code: workerImageCode,
			memorySize: 512, 
			timeout: cdk.Duration.seconds(60),
			environment: {
				TABLE_NAME: ragQueryTable.tableName,
			},
		});

		// Lambda function to handle the API requests
		const apiImageCode = DockerImageCode.fromImageAsset("../image", {
			cmd: ["api_handler.handler"]
		});
		const apiFunction = new DockerImageFunction(this, 'ApiFunction', {
			code: apiImageCode,
			memorySize: 256, 
			timeout: cdk.Duration.seconds(30),
			environment: {
				TABLE_NAME: ragQueryTable.tableName,
				WORKER_LAMBDA_NAME: workerFunction.functionName,
			},
		});


		// Setup environment to be able to use GOOGLE_API_KEY
		const apiKeyParam = StringParameter.fromSecureStringParameterAttributes(this, 'GoogleApiKeyParam', {
			parameterName: '/myapp/google_api_key'
		});
		apiFunction.addEnvironment('GOOGLE_API_KEY_PARAM', '/myapp/google_api_key');

		// Grant permissions
		ragQueryTable.grantReadWriteData(workerFunction);
		ragQueryTable.grantReadWriteData(apiFunction);
		apiKeyParam.grantRead(workerFunction);
		workerFunction.grantInvoke(apiFunction);

		// Set HTTPS Url
		const functionUrl = apiFunction.addFunctionUrl({
			authType: FunctionUrlAuthType.NONE
		});
		new cdk.CfnOutput(this, "FunctionUrl", {
			value: functionUrl.url,
		});
  }
}
