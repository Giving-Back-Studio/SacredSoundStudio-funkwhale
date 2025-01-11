## AWS Documentation

### DevOps.yaml

This template defines the resources needed for a Pipeline that automatically tests, builds, and deploys this application onto AWS. Any changes to the pipeline itself will also be deployed in the pipeline.

* 1 CodePipeline
* 3 CodeBuild Jobs (defined in the [builds](builds/) directory)
  * Code Tests
  * Docker Build
  * End-to-end Tests
* Developer Access IAM Policy
  * Read all CodePipeline, CodeBuild, and CloudFormation resources
  * Restart CodePipeline
* Supporting Resources
  * IAM Roles
  * Artifacts S3 Bucket
  * ECR Repositories

#### Getting up and running

To create a new development stage using this template, run the following command:

```sh
$> aws cloudformation create-stack --stack-name [branch]-30sec-devops --parameters ParameterKey=GitBranch,ParameterValue=[branch] --template-body file://AWS/cloudformation/DevOps.yaml --role-arn arn:aws:iam::333435094895:role/CloudFormationRole --capabilities CAPABILITY_IAM
```

### Stack.yaml

This template is the root CloudFormation template that deploys the application itself. It has a few shared resources and several nested stacks.

* Nested Stacks
  * Web App Fargate Service ([FargateService.yaml](FargateService.yaml))
  * Worker Fargate Service ([FargateService.yaml](FargateService.yaml))
  * RDS Cluster ([RDS.yaml](RDS.yaml))
  * VPC ([VPC.yaml](VPC.yaml))
* Shared Resources
  * Load Balancer
  * IAM Roles
  * ECS Cluster
  * Security Groups


### FargateService.yaml

This template is used for both the WebApp and Worker applications. They take a docker container passed in from the build step, and run it as a Fargate Service. There is Auto-Scaling built-in to keep up with changes in web traffic and worker demands.


### VPC.yaml

This template creates a VPC for us to launch all of the compute resources into.


### RDS.yaml

This template creates an RDS cluster to store permanent relational data from the apps.