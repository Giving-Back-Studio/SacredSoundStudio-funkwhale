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
        tuple: (cpu, memory) where cpu is in CPU units and memory is in MB
    """
    # Convert bytes to MB for easier calculation
    size_mb = size_bytes / (1024 * 1024)
    
    # Base values
    base_cpu = 1024  # 1 vCPU
    base_memory = 2048  # 2GB
    
    # Small files (< 100MB): Use base values
    if size_mb < 100:
        return base_cpu, base_memory
    
    # Medium files (100MB - 1GB): Scale up linearly
    elif size_mb < 1024:
        cpu = min(2048, int(base_cpu * (1 + size_mb / 200)))
        memory = min(4096, int(base_memory * (1 + size_mb / 200)))
        return cpu, memory
    
    # Large files (1GB - 5GB): Use higher resources
    elif size_mb < 5120:
        cpu = min(4096, int(base_cpu * (1 + size_mb / 400)))
        memory = min(8192, int(base_memory * (1 + size_mb / 300)))
        return cpu, memory
    
    # Very large files (> 5GB): Use maximum resources
    else:
        return 4096, 8192  # 4 vCPU, 8GB

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
        
        logger.info(f"Calculated resources: CPU={cpu}, Memory={memory}MB")
        
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
                'memory': str(memory),
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
