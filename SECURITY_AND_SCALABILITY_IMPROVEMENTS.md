# Security and Scalability Improvements

## Executive Summary

This document addresses critical security and scalability concerns identified in the CodeRoad platform review. These improvements are essential before production deployment.

---

## 🔴 CRITICAL: Code Execution Security

### Current Issue
The `JudgeService` executes user-submitted code directly on the host machine using `subprocess.run`, which poses severe security risks:
- Malicious code could delete files
- Access to environment variables (API keys, secrets)
- Denial-of-service attacks
- System compromise

### Current Status
- Sandbox directory (`backend/app/sandbox/`) contains only placeholder files
- No isolation between user code and host system

### Recommended Solutions

#### Option 1: Docker-based Sandbox (Recommended for AWS Deployment)
```python
# backend/app/sandbox/docker_runner.py
import docker
import tempfile
import os
from typing import Dict, Any

class DockerSandbox:
    def __init__(self):
        self.client = docker.from_env()
        self.image = "python:3.11-alpine"  # Minimal image
        
    def execute_code(self, code: str, test_input: str, timeout: int = 5) -> Dict[str, Any]:
        """Execute code in isolated Docker container"""
        try:
            # Create temporary directory for code
            with tempfile.TemporaryDirectory() as tmpdir:
                code_file = os.path.join(tmpdir, "solution.py")
                with open(code_file, 'w') as f:
                    f.write(code)
                
                # Run container with strict limits
                container = self.client.containers.run(
                    self.image,
                    command=f"python solution.py",
                    volumes={tmpdir: {'bind': '/code', 'mode': 'ro'}},
                    working_dir='/code',
                    mem_limit='128m',  # 128MB RAM limit
                    cpu_quota=50000,   # 50% CPU
                    network_disabled=True,  # No network access
                    read_only=True,    # Read-only filesystem
                    remove=True,       # Auto-remove container
                    detach=False,
                    stdin_open=True,
                    stdout=True,
                    stderr=True,
                    timeout=timeout
                )
                
                return {
                    "success": True,
                    "output": container.decode('utf-8'),
                    "error": None
                }
                
        except docker.errors.ContainerError as e:
            return {
                "success": False,
                "output": None,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": f"Execution error: {str(e)}"
            }
```

#### Option 2: AWS Lambda Execution (Best for Scalability)
```python
# backend/app/sandbox/lambda_executor.py
import boto3
import json
import base64

class LambdaExecutor:
    def __init__(self):
        self.lambda_client = boto3.client('lambda', region_name='us-east-1')
        self.function_name = 'code-execution-sandbox'
        
    def execute_code(self, code: str, test_input: str, timeout: int = 5) -> Dict[str, Any]:
        """Execute code in AWS Lambda sandbox"""
        payload = {
            'code': base64.b64encode(code.encode()).decode(),
            'input': test_input,
            'timeout': timeout
        }
        
        try:
            response = self.lambda_client.invoke(
                FunctionName=self.function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            result = json.loads(response['Payload'].read())
            return result
            
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": f"Lambda execution error: {str(e)}"
            }
```

#### Option 3: gVisor (Strongest Isolation)
```yaml
# docker-compose.yml addition
services:
  code-executor:
    image: gcr.io/gvisor-presubmit/runsc
    runtime: runsc
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
```

### Implementation Priority
1. **Immediate**: Implement Docker-based sandbox (Option 1)
2. **Production**: Migrate to AWS Lambda (Option 2) for better scalability
3. **High-Security**: Add gVisor runtime (Option 3) for defense-in-depth

---

## 🟠 HIGH: WebSocket Scalability

### Current Issue
WebSocket connections are stored in-memory, preventing horizontal scaling:
- Players in the same match connecting to different backend instances won't see each other
- No cross-node communication
- Single point of failure

### Current Implementation
```python
# backend/app/services/websocket_manager.py
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
```

### Recommended Solution: Redis Pub/Sub

#### Step 1: Add Redis to Infrastructure
```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  redis_data:
```

#### Step 2: Update WebSocket Manager
```python
# backend/app/services/websocket_manager.py
import redis.asyncio as redis
import json
from typing import Dict, List
from fastapi import WebSocket

class RedisConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.redis_client = None
        self.pubsub = None
        
    async def connect_redis(self):
        """Initialize Redis connection"""
        self.redis_client = await redis.from_url(
            "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=True
        )
        self.pubsub = self.redis_client.pubsub()
        
    async def connect(self, websocket: WebSocket, room_id: str):
        """Connect WebSocket and subscribe to Redis channel"""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
            # Subscribe to Redis channel for this room
            await self.pubsub.subscribe(f"room:{room_id}")
            
        self.active_connections[room_id].append(websocket)
        
    async def disconnect(self, websocket: WebSocket, room_id: str):
        """Disconnect WebSocket"""
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            
            if not self.active_connections[room_id]:
                # Unsubscribe if no more connections
                await self.pubsub.unsubscribe(f"room:{room_id}")
                del self.active_connections[room_id]
                
    async def broadcast_to_room(self, room_id: str, message: dict):
        """Broadcast message to all nodes via Redis"""
        # Publish to Redis channel
        await self.redis_client.publish(
            f"room:{room_id}",
            json.dumps(message)
        )
        
    async def listen_for_messages(self):
        """Listen for Redis messages and broadcast to local connections"""
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                channel = message['channel']
                room_id = channel.split(':')[1]
                data = json.loads(message['data'])
                
                # Broadcast to local WebSocket connections
                if room_id in self.active_connections:
                    for connection in self.active_connections[room_id]:
                        try:
                            await connection.send_json(data)
                        except Exception:
                            pass  # Connection closed
```

#### Step 3: Update Dependencies
```txt
# backend/requirements.txt
redis[hiredis]>=5.0.0
```

#### Step 4: AWS Deployment with ElastiCache
```yaml
# AWS CloudFormation/Terraform
Resources:
  RedisCluster:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupDescription: CodeRoad WebSocket Pub/Sub
      Engine: redis
      CacheNodeType: cache.t3.micro
      NumCacheClusters: 2
      AutomaticFailoverEnabled: true
      MultiAZEnabled: true
```

---

## 🟡 MEDIUM: Database Configuration

### Current Issue
- Default configuration uses SQLite (not suitable for production)
- SQLite doesn't support concurrent writes
- No horizontal scaling capability

### Current Status
```env
# .env
DATABASE_URL=sqlite:///./coderoad.db
```

### Recommended Solution

#### Development Environment
```env
# backend/.env
DATABASE_URL=postgresql://coderoad:password@localhost:5432/coderoad_dev
```

#### Production Environment (AWS RDS)
```env
# Production .env (use AWS Secrets Manager)
DATABASE_URL=postgresql://admin:${DB_PASSWORD}@coderoad-db.xxxxx.us-east-1.rds.amazonaws.com:5432/coderoad_prod
```

#### Update docker-compose.yml
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: coderoad
      POSTGRES_PASSWORD: ${DB_PASSWORD:-devpassword}
      POSTGRES_DB: coderoad_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U coderoad"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

#### Migration Script
```python
# backend/scripts/migrate_sqlite_to_postgres.py
import sqlite3
import psycopg2
from sqlalchemy import create_engine
from app.core.database import Base

def migrate():
    """Migrate data from SQLite to PostgreSQL"""
    # Connect to both databases
    sqlite_conn = sqlite3.connect('coderoad.db')
    pg_engine = create_engine('postgresql://coderoad:password@localhost:5432/coderoad_dev')
    
    # Create tables in PostgreSQL
    Base.metadata.create_all(bind=pg_engine)
    
    # Migrate data table by table
    tables = ['players', 'matches', 'submissions', 'challenges', 'ratings']
    
    for table in tables:
        print(f"Migrating {table}...")
        df = pd.read_sql(f"SELECT * FROM {table}", sqlite_conn)
        df.to_sql(table, pg_engine, if_exists='append', index=False)
        
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
```

---

## 📋 Implementation Checklist

### Phase 1: Critical Security (Week 1)
- [ ] Implement Docker-based code execution sandbox
- [ ] Add resource limits (CPU, memory, timeout)
- [ ] Disable network access in sandbox
- [ ] Add filesystem restrictions
- [ ] Test with malicious code samples
- [ ] Update JudgeService to use sandbox

### Phase 2: Scalability (Week 2)
- [ ] Set up Redis for WebSocket Pub/Sub
- [ ] Update ConnectionManager to use Redis
- [ ] Test multi-node WebSocket communication
- [ ] Add Redis health checks
- [ ] Configure Redis persistence

### Phase 3: Database Migration (Week 2)
- [ ] Switch development environment to PostgreSQL
- [ ] Create migration script for existing data
- [ ] Update all database queries for PostgreSQL compatibility
- [ ] Set up connection pooling
- [ ] Configure database backups

### Phase 4: AWS Production Setup (Week 3)
- [ ] Deploy RDS PostgreSQL instance
- [ ] Deploy ElastiCache Redis cluster
- [ ] Configure ECS task definitions with proper security groups
- [ ] Set up AWS Lambda for code execution (optional)
- [ ] Configure auto-scaling policies
- [ ] Set up CloudWatch monitoring

---

## 🔒 Additional Security Recommendations

### 1. Environment Variables Protection
```python
# backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Use AWS Secrets Manager in production
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    GROQ_API_KEYS: list[str]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    @classmethod
    def from_aws_secrets(cls):
        """Load from AWS Secrets Manager"""
        import boto3
        client = boto3.client('secretsmanager')
        secret = client.get_secret_value(SecretId='coderoad/prod')
        return cls(**json.loads(secret['SecretString']))

@lru_cache()
def get_settings():
    if os.getenv('ENV') == 'production':
        return Settings.from_aws_secrets()
    return Settings()
```

### 2. Rate Limiting
```python
# backend/app/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Apply to submission endpoint
@router.post("/submit")
@limiter.limit("10/minute")  # Max 10 submissions per minute
async def submit_code(...):
    pass
```

### 3. Input Validation
```python
# backend/app/schemas/submission_schema.py
from pydantic import BaseModel, validator

class SubmissionCreate(BaseModel):
    code: str
    language: str = "python"
    
    @validator('code')
    def validate_code_length(cls, v):
        if len(v) > 50000:  # 50KB limit
            raise ValueError('Code too long')
        return v
        
    @validator('code')
    def validate_dangerous_imports(cls, v):
        dangerous = ['os', 'sys', 'subprocess', 'socket', '__import__']
        for module in dangerous:
            if f'import {module}' in v or f'from {module}' in v:
                raise ValueError(f'Import of {module} is not allowed')
        return v
```

---

## 📊 Monitoring and Observability

### CloudWatch Metrics
```python
# backend/app/middleware/metrics.py
import boto3
from datetime import datetime

cloudwatch = boto3.client('cloudwatch')

def log_code_execution_metric(duration_ms: float, success: bool):
    """Log code execution metrics to CloudWatch"""
    cloudwatch.put_metric_data(
        Namespace='CodeRoad/Execution',
        MetricData=[
            {
                'MetricName': 'ExecutionDuration',
                'Value': duration_ms,
                'Unit': 'Milliseconds',
                'Timestamp': datetime.utcnow()
            },
            {
                'MetricName': 'ExecutionSuccess',
                'Value': 1 if success else 0,
                'Unit': 'Count',
                'Timestamp': datetime.utcnow()
            }
        ]
    )
```

---

## 🚀 Deployment Architecture

### Recommended AWS Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     Application Load Balancer                │
│                    (SSL/TLS Termination)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐       ┌───────▼────────┐
│  ECS Service   │       │  ECS Service   │
│  (Backend 1)   │       │  (Backend 2)   │
│  + WebSocket   │       │  + WebSocket   │
└───────┬────────┘       └───────┬────────┘
        │                         │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   ElastiCache Redis     │
        │   (Pub/Sub + Cache)     │
        └─────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │      RDS PostgreSQL     │
        │   (Multi-AZ, Encrypted) │
        └─────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │    AWS Lambda           │
        │  (Code Execution)       │
        └─────────────────────────┘
```

---

## 💰 Cost Estimation (AWS)

### Monthly Costs (Estimated)
- **ECS Fargate** (2 tasks, 0.5 vCPU, 1GB RAM): ~$30
- **RDS PostgreSQL** (db.t3.micro, Multi-AZ): ~$30
- **ElastiCache Redis** (cache.t3.micro, 2 nodes): ~$25
- **Application Load Balancer**: ~$20
- **Lambda** (code execution, 1M invocations): ~$10
- **CloudWatch Logs**: ~$5
- **Data Transfer**: ~$10

**Total: ~$130/month** (for moderate traffic)

---

## 📝 Next Steps

1. **Review this document** with your team
2. **Prioritize** based on deployment timeline
3. **Implement Phase 1** (Critical Security) immediately
4. **Test thoroughly** in staging environment
5. **Deploy incrementally** to production

---

## 📚 References

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [AWS Lambda Security](https://docs.aws.amazon.com/lambda/latest/dg/lambda-security.html)
- [Redis Pub/Sub Documentation](https://redis.io/docs/manual/pubsub/)
- [PostgreSQL on AWS RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [gVisor Documentation](https://gvisor.dev/docs/)

---

**Document Version**: 1.0  
**Last Updated**: March 4, 2026  
**Status**: Ready for Implementation
