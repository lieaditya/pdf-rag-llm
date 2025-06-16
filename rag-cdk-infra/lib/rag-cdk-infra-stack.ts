import * as cdk from 'aws-cdk-lib';
import { AttributeType, BillingMode, Table } from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { DockerImageCode, DockerImageFunction, FunctionUrlAuthType } from 'aws-cdk-lib/aws-lambda';
import { BlockPublicAccess, Bucket } from 'aws-cdk-lib/aws-s3';
import { StringParameter } from 'aws-cdk-lib/aws-ssm';
import { Construct } from 'constructs';
import { FileSystem } from 'aws-cdk-lib/aws-efs';
import { Vpc } from 'aws-cdk-lib/aws-ec2';


export class RagCdkInfraStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

		// Create VPC for EFS + Lambda functions
		// const vpc = new Vpc(this, 'LambdaVpc', {
		// 	ipAddresses: ec2.IpAddresses.cidr('10.10.0.0/16'),
		// 	natGateways: 0,
		// 	subnetConfiguration: [
		// 		{
		// 			name: 'public-subnet',
		// 			subnetType: ec2.SubnetType.PUBLIC,
		// 			cidrMask: 24,
		// 		},
		// 	],
		// });

		// Create access point from the EFS for the Lambda functions
		// const chromaFileSystem = new FileSystem(this, 'ChromaFileSystem', {
		// 	vpc: vpc,
		// 	removalPolicy: cdk.RemovalPolicy.DESTROY,
		// });
		// const accessPoint = chromaFileSystem.addAccessPoint('ChromaAccessPoint', {
		// 	path: '/chroma',
		// 	posixUser: {
		// 		uid: '1000',
		// 		gid: '1000',
		// 	},
		// 	createAcl: {
		// 		ownerUid: '1000',
		// 		ownerGid: '1000',
		// 		permissions: '750',
		// 	},
		// });
		
		// Create S3 to store the PDFs
		const userDocumentBucket = new Bucket(this, 'UserDocumentBucket', {
			removalPolicy: cdk.RemovalPolicy.DESTROY,
			autoDeleteObjects: true,
			publicReadAccess: true,
			blockPublicAccess: new BlockPublicAccess({
				blockPublicAcls: false,
				blockPublicPolicy: false,
				ignorePublicAcls: false,
				restrictPublicBuckets: false,
			}),
		});
		
		// Create DynamoDB table to store the query data and results
		const ragQueryTable = new Table(this, "RagQueryTable", {
			partitionKey: { name: "query_id", type: AttributeType.STRING },
			sortKey: { name: "user_id", type: AttributeType.STRING },
			billingMode: BillingMode.PAY_PER_REQUEST,
			timeToLiveAttribute: "ttl",
			removalPolicy: cdk.RemovalPolicy.DESTROY,
		});
		ragQueryTable.addGlobalSecondaryIndex({
			indexName: "UserIdSortedByCreatedAt",
			partitionKey: { name: "user_id", type: AttributeType.STRING },
			sortKey: { name: "created_at", type: AttributeType.NUMBER },
		});

		// Create Lambda function to handle the worker logic using Docker
		const workerImageCode = DockerImageCode.fromImageAsset("../image", {
			cmd: ["worker_handler.handler"]
		});
		const workerFunction = new DockerImageFunction(this, 'WorkerFunction', {
			code: workerImageCode,
			memorySize: 512, 
			timeout: cdk.Duration.seconds(180),
			// vpc: vpc,
			// vpcSubnets: {
			// 	subnetType: ec2.SubnetType.PUBLIC,
			// },
			// allowPublicSubnet: true,
			// filesystem: lambda.FileSystem.fromEfsAccessPoint(
			// 	accessPoint,
			// 	'/mnt/chroma',
			// ),
			environment: {
				BUCKET_NAME: userDocumentBucket.bucketName,
				TABLE_NAME: ragQueryTable.tableName,
				// CHROMA_DB_PATH: '/mnt/chroma',
			},
		});

		// Lambda function to handle the API requests
		const apiImageCode = DockerImageCode.fromImageAsset("../image", {
			cmd: ["api_handler.handler"]
		});
		const apiFunction = new DockerImageFunction(this, 'ApiFunction', {
			code: apiImageCode,
			memorySize: 512, 
			timeout: cdk.Duration.seconds(120),
			// vpc: vpc,
			// vpcSubnets: {
			// 	subnetType: ec2.SubnetType.PUBLIC,
			// },
			// allowPublicSubnet: true,
			// filesystem: lambda.FileSystem.fromEfsAccessPoint(
			// 	accessPoint,
			// 	'/mnt/chroma',
			// ),
			environment: {
				BUCKET_NAME: userDocumentBucket.bucketName,
				TABLE_NAME: ragQueryTable.tableName,
				WORKER_LAMBDA_NAME: workerFunction.functionName,
				// CHROMA_DB_PATH: '/mnt/chroma',
			},
		});


		// Setup environment to be able to use GOOGLE_API_KEY
		const googleApiKeyParam = StringParameter.fromSecureStringParameterAttributes(this, 'GoogleApiKeyParam', {
			parameterName: '/rag-app/google_api_key'
		});
		const chromaApiKeyParam = StringParameter.fromSecureStringParameterAttributes(this, 'ChromaApiKeyParam', {
			parameterName: '/rag-app/chroma_api_key',
		});
		workerFunction.addEnvironment('GOOGLE_API_KEY_PARAM', '/rag-app/google_api_key');
		apiFunction.addEnvironment('GOOGLE_API_KEY_PARAM', '/rag-app/google_api_key');
		workerFunction.addEnvironment('CHROMA_API_KEY_PARAM', '/rag-app/chroma_api_key');
		apiFunction.addEnvironment('CHROMA_API_KEY_PARAM', '/rag-app/chroma_api_key');

		// Grant permissions
		userDocumentBucket.grantReadWrite(workerFunction);
		userDocumentBucket.grantReadWrite(apiFunction);
		ragQueryTable.grantReadWriteData(workerFunction);
		ragQueryTable.grantReadWriteData(apiFunction);
		googleApiKeyParam.grantRead(workerFunction);
		googleApiKeyParam.grantRead(apiFunction);
		chromaApiKeyParam.grantRead(workerFunction);
		chromaApiKeyParam.grantRead(apiFunction);
		workerFunction.grantInvoke(apiFunction);

		// Set HTTPS Url
		const functionUrl = apiFunction.addFunctionUrl({
			authType: FunctionUrlAuthType.NONE
		});

		// Output
		new cdk.CfnOutput(this, "FunctionUrl", {
			value: functionUrl.url,
		});
		new cdk.CfnOutput(this, "UserDocumentBucketName", {
			value: userDocumentBucket.bucketName,
		});
		new cdk.CfnOutput(this, "RagQueryTableName", {
			value: ragQueryTable.tableName,
		});
		// new cdk.CfnOutput(this, "ChromaFileSystemId", {
		// 	value: chromaFileSystem.fileSystemId,
		// });
  }
}
