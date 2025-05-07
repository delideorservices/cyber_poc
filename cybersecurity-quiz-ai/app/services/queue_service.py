import json
import redis
from app.config import REDIS_HOST, REDIS_PORT

class QueueService:
    def __init__(self):
        self.redis = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), decode_responses=True)
        
    def publish(self, channel, message):
        """Publish a message to a Redis channel"""
        if isinstance(message, dict):
            message = json.dumps(message)
        return self.redis.publish(channel, message)
        
    def subscribe(self, channel):
        """Subscribe to a Redis channel"""
        pubsub = self.redis.pubsub()
        pubsub.subscribe(channel)
        return pubsub
        
    def get_message(self, pubsub, timeout=None):
        """Get a message from a pubsub channel"""
        message = pubsub.get_message(timeout=timeout)
        if message and message['type'] == 'message':
            try:
                return json.loads(message['data'])
            except:
                return message['data']
        return None
        
    # Queue helper methods
    def enqueue(self, queue_name, data):
        """Add a job to a queue"""
        job_id = self.redis.incr(f"{queue_name}:id")
        job_data = {
            'id': job_id,
            'status': 'pending',
            'data': data,
            'created_at': json.dumps(datetime.now(), default=str)
        }
        self.redis.hset(f"{queue_name}:jobs", job_id, json.dumps(job_data))
        self.redis.lpush(f"{queue_name}:queue", job_id)
        return job_id
        
    def dequeue(self, queue_name):
        """Get the next job from a queue"""
        job_id = self.redis.rpop(f"{queue_name}:queue")
        if not job_id:
            return None
            
        job_data = self.redis.hget(f"{queue_name}:jobs", job_id)
        if not job_data:
            return None
            
        job = json.loads(job_data)
        job['status'] = 'processing'
        self.redis.hset(f"{queue_name}:jobs", job_id, json.dumps(job))
        return job
        
    def complete_job(self, queue_name, job_id, result=None):
        """Mark a job as complete"""
        job_data = self.redis.hget(f"{queue_name}:jobs", job_id)
        if not job_data:
            return False
            
        job = json.loads(job_data)
        job['status'] = 'completed'
        job['result'] = result
        job['completed_at'] = json.dumps(datetime.now(), default=str)
        self.redis.hset(f"{queue_name}:jobs", job_id, json.dumps(job))
        return True
        
    def get_job_status(self, queue_name, job_id):
        """Get the status of a job"""
        job_data = self.redis.hget(f"{queue_name}:jobs", job_id)
        if not job_data:
            return None
        job = json.loads(job_data)
        return job['status']

# Create a singleton instance
queue_service = QueueService()