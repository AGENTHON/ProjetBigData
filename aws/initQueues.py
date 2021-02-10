import boto3

REQUEST_QUEUE_NAME = 'requestQueue.fifo'
RESPONSE_QUEUE_NAME = "responseQueue.fifo"

def initQueues() :

    sqs = boto3.resource('sqs')

    return initQueueByName(sqs, REQUEST_QUEUE_NAME), initQueueByName(sqs, RESPONSE_QUEUE_NAME)

def initQueueByName(sqs, queueName) :
    try:
        # Get queue by name
        queue = sqs.get_queue_by_name(QueueName=queueName)
    except:
        # If queue does not exist, create one (we use FIFO queue here)
        queue = sqs.create_queue(QueueName=queueName, Attributes={'FifoQueue': 'true', 'DelaySeconds': '5', 'ContentBasedDeduplication': 'true'})
    return queue