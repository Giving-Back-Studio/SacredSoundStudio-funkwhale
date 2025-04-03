import boto3
import os
import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
ecs_client = boto3.client('ecs')

# Get environment variables
CLUSTER_NAME = os.environ['CLUSTER_NAME']
TASK_DEFINITION = os.environ['TASK_DEFINITION']
SUBNET_A = os.environ['SUBNET_A']
SUBNET_B = os.environ['SUBNET_B']
SECURITY_GROUP = os.environ['SECURITY_GROUP']

def calculate_resources(size_bytes):
    """
    Calculate CPU and memory based on file size
    
    Args:
        size_bytes (int): Size of the file in bytes
        
    Returns:
        tuple: (cpu, memory) where cpu is in CPU units and memory is in GB with "GB" suffix
    """
    # Convert bytes to MB for easier calculation
    size_mb = size_bytes / (1024 * 1024)
    
    # Valid Fargate CPU and memory combinations:
    # 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB
    # 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB
    # 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB
    # 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments
    # 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments
    
    # Small files (< 100MB): Use minimal resources
    if size_mb < 100:
        return 256, "0.5GB"
    
    # Medium files (100MB - 500MB): Use moderate resources
    elif size_mb < 500:
        return 512, "1GB"
    
    # Large files (500MB - 1GB): Use more resources
    elif size_mb < 1024:
        return 1024, "2GB"
    
    # Very large files (1GB - 5GB): Use high resources
    elif size_mb < 5120:
        return 2048, "4GB"
    
    # Extremely large files (> 5GB): Use maximum resources
    else:
        return 4096, "8GB"

def lambda_handler(event, context):
    """
    Lambda function handler
    
    Args:
        event (dict): Event data from S3
        context (object): Lambda context
        
    Returns:
        dict: Response
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract bucket and key from the event
        bucket = event['detail']['bucket']['name']
        key = event['detail']['object']['key']
        
        logger.info(f"Processing file: s3://{bucket}/{key}")
        
        # Get object metadata to determine size
        response = s3_client.head_object(Bucket=bucket, Key=key)
        size_bytes = response['ContentLength']
        
        logger.info(f"File size: {size_bytes} bytes")
        
        # Calculate CPU and memory based on file size
        cpu, memory = calculate_resources(size_bytes)
        
        logger.info(f"Calculated resources: CPU={cpu}, Memory={memory}")
        
        # Run the ECS task with the calculated resources
        response = ecs_client.run_task(
            cluster=CLUSTER_NAME,
            taskDefinition=TASK_DEFINITION,
            count=1,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [SUBNET_A, SUBNET_B],
                    'securityGroups': [SECURITY_GROUP],
                    'assignPublicIp': 'DISABLED'
                }
            },
            overrides={
                'cpu': str(cpu),
                'memory': memory,
                'containerOverrides': [
                    {
                        'name': 'transcoder',
                        'command': ['funkwhale-manage', 'transcode_video', key]
                    }
                ]
            }
        )
        
        logger.info(f"ECS task started: {response['tasks'][0]['taskArn']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Transcoding task started successfully',
                'taskArn': response['tasks'][0]['taskArn'],
                'cpu': cpu,
                'memory': memory
            })
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise e
