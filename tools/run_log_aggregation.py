#!/usr/bin/env python


# Configure logging
logger = logging.getLogger(__name__)

"""
Log Aggregation Runner

This script aggregates logs from multiple sources and sends them to various
destinations, such as Elasticsearch, Logstash, or files.

Usage:
    python tools/run_log_aggregation.py [--app-name APP_NAME] [--log-dir LOG_DIR] [--es-host ES_HOST] [--es-port ES_PORT] [--es-index ES_INDEX] [--logstash-host LOGSTASH_HOST] [--logstash-port LOGSTASH_PORT] [--output-file OUTPUT_FILE]

Arguments:
    --app-name APP_NAME             Name of the application (default: pAIssive_income)
    --log-dir LOG_DIR               Directory containing log files (default: logs)
    --es-host ES_HOST               Elasticsearch host (if not provided, Elasticsearch is not used)
    --es-port ES_PORT               Elasticsearch port (default: 9200)
    --es-index ES_INDEX             Elasticsearch index name (default: logs)
    --logstash-host LOGSTASH_HOST   Logstash host (if not provided, Logstash is not used)
    --logstash-port LOGSTASH_PORT   Logstash port (default: 5000)
    --output-file OUTPUT_FILE       Output file for aggregated logs (if not provided, no file output)
"""

import argparse
import logging
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the log aggregation utilities
from common_utils.logging.log_aggregation import (
    aggregate_logs,
    configure_log_aggregation,
)
from common_utils.logging.secure_logging import get_secure_logger

# Configure logging


# Set up logging
logger = get_secure_logger("log_aggregation_runner")


def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments

    """
    parser = argparse.ArgumentParser(description="Log Aggregation Runner")
    parser.add_argument(
        "--app-name",
        type=str,
        default="pAIssive_income",
        help="Name of the application (default: pAIssive_income)",
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs",
        help="Directory containing log files (default: logs)",
    )
    parser.add_argument(
        "--es-host",
        type=str,
        help="Elasticsearch host (if not provided, Elasticsearch is not used)",
    )
    parser.add_argument(
        "--es-port",
        type=int,
        default=9200,
        help="Elasticsearch port (default: 9200)",
    )
    parser.add_argument(
        "--es-index",
        type=str,
        default="logs",
        help="Elasticsearch index name (default: logs)",
    )
    parser.add_argument(
        "--logstash-host",
        type=str,
        help="Logstash host (if not provided, Logstash is not used)",
    )
    parser.add_argument(
        "--logstash-port",
        type=int,
        default=5000,
        help="Logstash port (default: 5000)",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="Output file for aggregated logs (if not provided, no file output)",
    )
    parser.add_argument(
        "--configure",
        action="store_true",
        help="Configure log aggregation to run periodically",
    )
    return parser.parse_args()


def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()

    # Create the log directory if it doesn't exist
    os.makedirs(args.log_dir, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(args.log_dir, "log_aggregation.log")),
        ],
    )

    try:
        if args.configure:
            # Configure log aggregation to run periodically
            logger.info("Configuring log aggregation to run periodically")
            configure_log_aggregation(
                app_name=args.app_name,
                log_dir=args.log_dir,
                es_host=args.es_host,
                es_port=args.es_port,
                es_index=args.es_index,
                logstash_host=args.logstash_host,
                logstash_port=args.logstash_port,
                output_file=args.output_file,
            )

            # Keep the main thread alive
            import time
            while True:
                time.sleep(1)
        else:
            # Run log aggregation once
            logger.info("Running log aggregation")
            aggregate_logs(
                app_name=args.app_name,
                log_dir=args.log_dir,
                es_host=args.es_host,
                es_port=args.es_port,
                es_index=args.es_index,
                logstash_host=args.logstash_host,
                logstash_port=args.logstash_port,
                output_file=args.output_file,
            )
    except Exception as e:
        logger.error("Error running log aggregation: %s", e)
        sys.exit(1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
