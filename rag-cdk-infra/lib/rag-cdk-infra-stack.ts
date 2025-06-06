import * as cdk from 'aws-cdk-lib';
import { DockerImageCode, DockerImageFunction, FunctionUrlAuthType } from 'aws-cdk-lib/aws-lambda';
import { StringParameter } from 'aws-cdk-lib/aws-ssm';
import { Construct } from 'constructs';


export class RagCdkInfraStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

		const apiKeyParam = StringParameter.fromSecureStringParameterAttributes(this, 'GoogleApiKeyParam', {
			parameterName: '/myapp/google_api_key'
		});
		
		const apiImageCode = DockerImageCode.fromImageAsset("../image", {
			cmd: ["api_handler.handler"]
		});

		const apiFunction = new DockerImageFunction(this, 'ApiFunction', {
			code: apiImageCode,
			memorySize: 256, 
			timeout: cdk.Duration.seconds(30)
		});
		
		apiKeyParam.grantRead(apiFunction);
		apiFunction.addEnvironment('GOOGLE_API_KEY_PARAM', '/myapp/google_api_key');

		const functionUrl = apiFunction.addFunctionUrl({
			authType: FunctionUrlAuthType.NONE
		});

		new cdk.CfnOutput(this, "FunctionUrl", {
			value: functionUrl.url,
		});
  }
}
