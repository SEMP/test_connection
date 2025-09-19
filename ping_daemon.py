#!/usr/bin/env python3
"""
Ping Checker Daemon Service

A service that runs ping connectivity tests based on cron-like schedule configuration.
Uses APScheduler to manage periodic tasks defined in ping_schedule.conf
"""

import sys
import signal
import logging
import time
from typing import Dict
import configparser
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

# Import constants and ping functionality
from constants import (
    DAEMON_CONFIG_FILE, DAEMON_LOG_FILE, resolve_ip_file_path
)
from ping_checker import read_ip_list, setup_logging, ping_host, log_result
from concurrent.futures import ThreadPoolExecutor, as_completed


class PingDaemon:
    def __init__(self, config_file: str = None):
        self.config_file = config_file or str(DAEMON_CONFIG_FILE)
        self.scheduler = BlockingScheduler()
        self.running = False

        # Setup logging for the daemon
        self.setup_daemon_logging()

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Add scheduler event listeners
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)

    def setup_daemon_logging(self):
        """Setup logging for daemon operations"""
        log_file = str(DAEMON_LOG_FILE)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _signal_handler(self, signum, _):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()

    def _job_executed(self, event):
        """Log successful job execution"""
        self.logger.info(f"Job {event.job_id} executed successfully")

    def _job_error(self, event):
        """Log job execution errors"""
        self.logger.error(f"Job {event.job_id} failed: {event.exception}")

    def load_config(self) -> Dict:
        """
        Load schedule configuration from file

        Returns:
            dict: Configuration with job definitions
        """
        config_path = resolve_ip_file_path(self.config_file)

        if not config_path.exists():
            self.logger.error(f"Configuration file {config_path} not found")
            sys.exit(1)

        config = configparser.ConfigParser()
        config.read(config_path)

        return config

    def ping_job(self, job_name: str, ip_file: str, timeout: int = 3, count: int = 1, workers: int = 10):
        """
        Execute a ping job with specified parameters

        Args:
            job_name: Name identifier for the job
            ip_file: Path to file containing IP addresses
            timeout: Ping timeout in seconds
            count: Number of ping packets
            workers: Number of concurrent workers
        """
        self.logger.info(f"Starting ping job '{job_name}' with file '{ip_file}'")

        try:
            # Resolve IP file path
            ip_file_path = resolve_ip_file_path(ip_file)

            # Check if file exists
            if not ip_file_path.exists():
                self.logger.error(f"IP file '{ip_file_path}' does not exist for job '{job_name}'")
                return

            # Read IP addresses
            ip_list = read_ip_list(str(ip_file_path))
            if not ip_list:
                self.logger.warning(f"No IP addresses found in file '{ip_file}' for job '{job_name}'")
                return

            # Setup logging for this job
            success_log, failure_log = setup_logging()

            self.logger.info(f"Job '{job_name}': Testing {len(ip_list)} IPs (timeout={timeout}s, workers={workers})")

            start_time = time.time()
            successful = 0
            failed = 0

            # Execute pings concurrently
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_ip = {
                    executor.submit(ping_host, ip, timeout, count): ip
                    for ip in ip_list
                }

                for future in as_completed(future_to_ip):
                    ip_address, success, response_info = future.result()

                    # Log the result
                    log_result(ip_address, success, response_info, success_log, failure_log)

                    if success:
                        successful += 1
                    else:
                        failed += 1

            duration = time.time() - start_time

            self.logger.info(f"Job '{job_name}' completed: {successful} reachable, {failed} unreachable (duration: {duration:.2f}s)")

        except Exception as e:
            self.logger.error(f"Error in ping job '{job_name}': {str(e)}")

    def add_jobs_from_config(self):
        """Load and add all jobs from configuration file"""
        config = self.load_config()

        job_count = 0
        for section_name in config.sections():
            if section_name.startswith('job:'):
                job_name = section_name[4:]  # Remove 'job:' prefix
                section = config[section_name]

                # Required parameters
                if 'ip_file' not in section or 'schedule' not in section:
                    self.logger.error(f"Job '{job_name}' missing required parameters (ip_file, schedule)")
                    continue

                ip_file = section['ip_file']
                schedule = section['schedule']

                # Optional parameters with defaults
                timeout = section.getint('timeout', 3)
                count = section.getint('count', 1)
                workers = section.getint('workers', 10)

                try:
                    # Parse cron schedule
                    cron_parts = schedule.split()
                    if len(cron_parts) != 5:
                        self.logger.error(f"Job '{job_name}': Invalid cron schedule '{schedule}' (expected 5 fields)")
                        continue

                    minute, hour, day, month, day_of_week = cron_parts

                    # Add job to scheduler
                    self.scheduler.add_job(
                        func=self.ping_job,
                        trigger=CronTrigger(
                            minute=minute,
                            hour=hour,
                            day=day,
                            month=month,
                            day_of_week=day_of_week
                        ),
                        args=[job_name, ip_file, timeout, count, workers],
                        id=f"ping_job_{job_name}",
                        name=f"Ping Job: {job_name}",
                        replace_existing=True
                    )

                    self.logger.info(f"Added job '{job_name}': {ip_file} (schedule: {schedule})")
                    job_count += 1

                except Exception as e:
                    self.logger.error(f"Error adding job '{job_name}': {str(e)}")

        if job_count == 0:
            self.logger.error("No valid jobs found in configuration file")
            sys.exit(1)

        self.logger.info(f"Loaded {job_count} ping jobs from configuration")

    def start(self):
        """Start the daemon service"""
        self.logger.info("Starting Ping Checker Daemon")

        # Load jobs from configuration
        self.add_jobs_from_config()

        # Print next run times for all jobs
        self.logger.info("Scheduled jobs:")
        for job in self.scheduler.get_jobs():
            next_run = job.next_run_time
            self.logger.info(f"  - {job.name}: next run at {next_run}")

        self.running = True

        try:
            self.logger.info("Daemon started. Press Ctrl+C to stop.")
            self.scheduler.start()
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Scheduler error: {str(e)}")
        finally:
            self.shutdown()

    def shutdown(self):
        """Shutdown the daemon gracefully"""
        if self.running:
            self.logger.info("Shutting down daemon...")
            self.running = False

            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)

            self.logger.info("Daemon stopped")
            sys.exit(0)


def main():
    """Main entry point for the daemon"""
    import argparse

    parser = argparse.ArgumentParser(description='Ping Checker Daemon Service')
    parser.add_argument('-c', '--config', default='ping_schedule.conf',
                       help='Configuration file (default: ping_schedule.conf)')

    args = parser.parse_args()

    daemon = PingDaemon(config_file=args.config)
    daemon.start()


if __name__ == "__main__":
    main()