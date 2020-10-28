# New Relic CloudWatch LogGroups Connector

AWS Serverless application that subscribes log groups from CloudWatch Logs to New Relic log ingestion lambda function.

## Installation

To install the logGroups connector Lambda function:

1. Open the [AWS Serverless Application Repository](https://serverlessrepo.aws.amazon.com/applications) in your browser.
2. Search for newrelic and check **Show apps that create custom IAM roles or resource policies** to find newrelic-loggroup-connector.
3. Open the `newrelic-loggroup-connector` details and click **Deploy**.
4. Scroll to the **Application settings** and configure your Lambda function.
5. Acknowledge that the app creates custom IAM roles and then click **Deploy**.

## Configuration

You can configure logsGroups connector using the following environment variables:

Key|Description|Value|
-|-|-|
LAMBDA_ARN | **The Amazon Resource Name (ARN)** of the target Lambda function (the function that will receive CloudWatch logs via the Log Group subscription).&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| Default: `arn:aws:lambda:us-east-1:123456789000:function:NRLogIngestionLambda`
LOG_GROUP_PATTERN | **Regex** to filter Log Groups. Log Groups that match the regex will be subscribed to the connector. Replace Test with a  Javascript regex that filters your Log Groups as desired. | Default: `Test`
USE_EXISTING_LOG_GROUPS|Controls whether this function will be used to create subscription filters for existing log groups. Select **True** if you want to use the function for subscribing to the existing log groups.|Default: `false`|
LOG_GROUP_TAGS|**Comma-separated key-value pairs** for filtering logGroups using tags. For Example, `Key1=string,Key2=string`. Only log groups that match any one of the key-value pairs will be subscribed to the lambda function. Supported only when UseExistingLogs is set to false which means it works only for new log groups, not existing log groups.|Default: `''`|


## Manual Deployment

If your organization restricts access to deploy via SAR, follow these steps below to deploy the logGroups connector function manually.

### SAM

1. Clone this repository: `git clone https://github.com/aminoz007/aws-newrelic-loggroup-connector.git`
2. [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) Make sure you have >=0.33.0 installed, you can check with `sam --version`.
3. Build the SAM application `sam build`
4. Deploy the SAM application: `sam deploy --guided`

Additional notes:

* During the deployement you will be invited to set up the function's environement variables (for example `LOG_GROUP_PATTERN`)
