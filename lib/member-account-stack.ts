import * as cdk from '@aws-cdk/core';
import { IRule, Rule, RuleTargetConfig } from '@aws-cdk/aws-events';
import { Effect, PolicyStatement, Role, ServicePrincipal } from '@aws-cdk/aws-iam';
import { CfnParameter } from '@aws-cdk/core';

export class AwsOrganizationsEventBridgeSetupMemberStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const eventBusName = new CfnParameter(this, "eventBusName", {
      type: "String",
      description: "Management Account event bus name."
    });

    const publishingRole = new Role(this, "PublishingRole", {
      assumedBy: new ServicePrincipal('events.amazonaws.com')
    });
    publishingRole.addToPolicy(
      new PolicyStatement({
        effect: Effect.ALLOW,
        resources: [`arn:aws:events:${process.env.REGION}:${process.env.CDK_MANAGEMENT_ACCOUNT}:event-bus/${eventBusName.valueAsString}`],
        actions: [
          "events:PutEvents"
        ]
      })
    );

    const rule = {
      name: 'MemberContegixEventBridgeRule',
      sources: ['aws.cloudwatch', 'aws.ec2', 'aws.rds'],
      description: 'The Rule propagates all Amazon CloudWatch Events, AWS EC2 Events, AWS RDS Events to the management account'
    };

    const cdkRule = new Rule(this, rule.name, {
      description: rule.description,
      ruleName: rule.name,
      eventPattern: {
        source: rule.sources,
      }
    });
    cdkRule.addTarget({
      bind(_rule: IRule, generatedTargetId: string): RuleTargetConfig {
        return {
          arn: `arn:aws:events:${process.env.REGION}:${process.env.CDK_MANAGEMENT_ACCOUNT}:event-bus/${eventBusName.valueAsString}`,
          id: generatedTargetId,
          role: publishingRole
        };
      }
    });

  }
}
