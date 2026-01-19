# Logging Configuration

## Log Levels

| Level | Description |
|-------|-------------|
| DEBUG | Detailed information for debugging |
| INFO | General information about operation |
| WARNING | Indicates potential issues |
| ERROR | Errors that don't stop the application |
| CRITICAL | Severe errors that may stop the application |

## Configuration

Set via environment variable:
```bash
LOG_LEVEL=INFO
```

## Log Aggregation (Future)

For production, consider:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Loki + Grafana
- CloudWatch (AWS)
- Datadog

## Structured Logging

Logs are output in JSON format for production:
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "message": "Application started",
  "service": "loom"
}
```
