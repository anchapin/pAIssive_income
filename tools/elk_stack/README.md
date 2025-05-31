# ELK Stack Integration

This directory contains configuration files for setting up the ELK (Elasticsearch, Logstash, Kibana) stack for log aggregation and analysis.

## Overview

The ELK stack is a powerful set of tools for collecting, processing, storing, and visualizing logs:

- **Elasticsearch**: A distributed, RESTful search and analytics engine for storing logs
- **Logstash**: A server-side data processing pipeline for ingesting and transforming logs
- **Kibana**: A web UI for visualizing and exploring logs stored in Elasticsearch
- **Filebeat**: A lightweight shipper for forwarding logs (optional)

## Setup

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB of RAM available for the ELK stack

### Installation

1. Create the necessary directories:

```bash
mkdir -p tools/elk_stack/logstash/pipeline
mkdir -p tools/elk_stack/logstash/config
mkdir -p tools/elk_stack/kibana/config
mkdir -p tools/elk_stack/filebeat/config
mkdir -p logs
```

2. Copy the configuration files to the appropriate directories (already done if you're using this repository).

3. Start the ELK stack:

```bash
cd tools/elk_stack
docker-compose up -d
```

4. Verify that the services are running:

```bash
docker-compose ps
```

5. Access Kibana at http://localhost:5601

### Configuration

The ELK stack is configured to:

- Collect logs from the `logs` directory
- Accept logs sent via UDP/TCP on port 5000
- Store logs in daily indices in Elasticsearch
- Provide visualization through Kibana

## Usage

### Sending Logs to the ELK Stack

You can send logs to the ELK stack using the provided log aggregation module:

```python
from common_utils.logging.log_aggregation import configure_log_aggregation

# Configure log aggregation
configure_log_aggregation(
    app_name="my_app",
    log_dir="logs",
    es_host="localhost",
    es_port=9200,
    logstash_host="localhost",
    logstash_port=5000,
)
```

### Viewing Logs in Kibana

1. Open Kibana at http://localhost:5601
2. Create an index pattern:
   - Go to Management > Stack Management > Kibana > Index Patterns
   - Create a new index pattern with the pattern `logs-*`
   - Select `@timestamp` as the time field
   - Click "Create index pattern"
3. View logs:
   - Go to Analytics > Discover
   - Select the `logs-*` index pattern
   - Use the time picker to select a time range
   - Use the search bar to filter logs

### Creating Dashboards

You can create custom dashboards in Kibana to visualize your logs:

1. Go to Analytics > Dashboard
2. Click "Create dashboard"
3. Add visualizations:
   - Click "Create visualization"
   - Choose a visualization type (e.g., bar chart, line chart, pie chart)
   - Configure the visualization using your log data
   - Save the visualization
4. Arrange visualizations on the dashboard
5. Save the dashboard

## Troubleshooting

### Elasticsearch Won't Start

If Elasticsearch fails to start, it might be due to insufficient memory or file permissions:

```bash
# Check Elasticsearch logs
docker logs elasticsearch
```

Common solutions:
- Increase the memory limit in `docker-compose.yml`
- Set the correct permissions on the data directory

### Logstash Won't Connect to Elasticsearch

If Logstash can't connect to Elasticsearch:

```bash
# Check Logstash logs
docker logs logstash
```

Common solutions:
- Ensure Elasticsearch is running
- Check network connectivity between containers
- Verify Elasticsearch URL in Logstash configuration

### Kibana Won't Connect to Elasticsearch

If Kibana can't connect to Elasticsearch:

```bash
# Check Kibana logs
docker logs kibana
```

Common solutions:
- Ensure Elasticsearch is running
- Check network connectivity between containers
- Verify Elasticsearch URL in Kibana configuration

## Additional Resources

- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Logstash Documentation](https://www.elastic.co/guide/en/logstash/current/index.html)
- [Kibana Documentation](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Filebeat Documentation](https://www.elastic.co/guide/en/beats/filebeat/current/index.html)
