# Logging Dashboard and ELK Stack Integration

This document provides information about the logging dashboard and ELK stack integration in the pAIssive_income project.

## Logging Dashboard

The logging dashboard is a web-based tool for visualizing and analyzing logs from the pAIssive_income project. It provides real-time log streaming, advanced filtering, statistical analysis, and visualization capabilities.

### Features

- Real-time log streaming and viewing
- Advanced filtering by log level, module, time range, and custom fields
- Interactive log statistics and visualizations
- Pattern detection and anomaly highlighting
- Performance metrics visualization
- Error rate tracking and alerting
- Integration with ELK stack (Elasticsearch, Logstash, Kibana)
- Export capabilities for logs and visualizations
- Customizable dashboards and views

### Installation

To install the required dependencies for the logging dashboard, run:

```bash
pip install -r requirements-elk.txt
```

### Usage

To start the logging dashboard, run:

```bash
python tools/log_dashboard.py [--port PORT] [--log-dir LOG_DIR] [--es-host ES_HOST] [--es-port ES_PORT] [--refresh SECONDS] [--theme THEME]
```

Arguments:
- `--port PORT`: Port to run the dashboard on (default: 8050)
- `--log-dir LOG_DIR`: Directory containing log files (default: current directory)
- `--es-host ES_HOST`: Elasticsearch host for advanced analytics (default: None)
- `--es-port ES_PORT`: Elasticsearch port (default: 9200)
- `--refresh SECONDS`: Refresh interval in seconds (default: 30)
- `--theme THEME`: Dashboard theme (default: light)

### Dashboard Navigation

#### Main Navigation Tabs

The logging dashboard has several main tabs:

1. **Dashboard**: View and filter log entries from files in the specified directory.
2. **Analytics**: Analyze log patterns, detect anomalies, and view performance metrics.
3. **ELK Integration**: Connect to Elasticsearch to fetch and analyze logs from the ELK stack.
4. **Settings**: Configure dashboard settings and export options.

#### Predefined Dashboards

The dashboard includes a dropdown menu in the top navigation bar that allows you to quickly switch between predefined dashboard layouts:

1. **Main Dashboard**: General overview of log data
2. **Error Monitoring**: Focus on error detection and analysis
3. **Performance Monitoring**: Focus on performance metrics and bottlenecks
4. **Security Monitoring**: Focus on security-related events and anomalies
5. **Service Health**: Focus on service availability and health metrics

To use a predefined dashboard:
1. Click on the "Dashboards" dropdown in the top navigation bar
2. Select one of the available dashboard options

The selected dashboard will immediately appear below the navigation bar. For more details on the predefined dashboards, see the [Predefined Dashboards](predefined_dashboards.md) documentation.

## ELK Stack Integration

The pAIssive_income project includes integration with the ELK stack (Elasticsearch, Logstash, Kibana) for centralized logging and log analysis.

### Components

1. **Elasticsearch**: A distributed, RESTful search and analytics engine.
2. **Logstash**: A server-side data processing pipeline that ingests data from multiple sources, transforms it, and then sends it to Elasticsearch.
3. **Kibana**: A data visualization dashboard for Elasticsearch.

### Setting Up ELK Stack

#### Using Docker Compose

The easiest way to set up the ELK stack is using Docker Compose. Create a `docker-compose.yml` file with the following content:

```yaml
version: '3'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - elk

  logstash:
    image: docker.elastic.co/logstash/logstash:7.17.0
    ports:
      - "5000:5000/udp"
      - "5000:5000/tcp"
      - "9600:9600"
    volumes:
      - ./logstash/config:/usr/share/logstash/config
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    networks:
      - elk
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:7.17.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    networks:
      - elk
    depends_on:
      - elasticsearch

networks:
  elk:
    driver: bridge

volumes:
  elasticsearch_data:
```

Then run:

```bash
docker-compose up -d
```

### Configuring Centralized Logging with ELK

To configure centralized logging with ELK stack integration, use the following code:

```python
from common_utils.logging.centralized_logging import (
    CentralizedLoggingService,
    FileOutput,
    ElasticsearchOutput,
    LogstashOutput,
    LevelFilter,
    SensitiveDataFilter,
)

# Server side
service = CentralizedLoggingService(
    host="0.0.0.0",
    port=5000,
    outputs=[
        FileOutput(directory="logs", rotation="daily"),
        ElasticsearchOutput(hosts=["elasticsearch:9200"], index_prefix="logs"),
        LogstashOutput(host="logstash", port=5000),
    ],
    filters=[
        SensitiveDataFilter(),
        LevelFilter(min_level="INFO"),
    ]
)
service.start()

# Client side
from common_utils.logging.centralized_logging import configure_centralized_logging, get_centralized_logger

# Configure centralized logging with buffering and retry
configure_centralized_logging(
    app_name="my_app",
    host="logging_server",
    port=5000,
    buffer_size=100,
    retry_interval=5,
    secure=True
)

# Get a logger
logger = get_centralized_logger(__name__)

# Log messages with structured data
logger.info("User logged in", extra={"user_id": "12345", "ip": "192.168.1.1"})
logger.error("Database connection failed", extra={"db": "users", "error_code": 500})
```

## Advanced Features

### Log Aggregation

The centralized logging service supports log aggregation from multiple distributed applications. Logs are collected, filtered, and stored in various outputs (files, Elasticsearch, Logstash).

### Log Rotation

The file output supports log rotation based on size or time (daily, hourly). This helps manage log file sizes and organize logs by date.

### Secure Logging

The centralized logging service supports secure communication using SSL/TLS. This ensures that logs are transmitted securely between clients and the server.

### Log Buffering and Retry

The logging client supports buffering log entries and retrying failed transmissions. This helps prevent log loss in case of network issues or server downtime.

### Sensitive Data Filtering

The centralized logging service includes a filter for masking sensitive data in logs, such as passwords, API keys, and personal information.

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure that the centralized logging service is running and accessible from the client.
2. **Missing Logs**: Check that the log level is set correctly and that the logs are not being filtered out.
3. **High CPU Usage**: Reduce the refresh interval or increase the buffer size to reduce the frequency of log transmissions.
4. **Memory Issues**: Reduce the batch size for Elasticsearch output or increase the flush interval to reduce memory usage.

### Logging Dashboard Issues

1. **Dashboard Not Loading**: Ensure that all required dependencies are installed and that the dashboard is running on the correct port.
2. **No Logs Displayed**: Check that the log directory is correct and contains log files.
3. **Elasticsearch Connection Failed**: Ensure that Elasticsearch is running and accessible from the dashboard.

## Contributing

Contributions to the logging dashboard and ELK stack integration are welcome. Please follow the project's contribution guidelines and submit pull requests for new features or bug fixes.
