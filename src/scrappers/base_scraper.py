from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
import os
from time import time
from typing import List, Dict, Any

import boto3
from botocore.exceptions import NoCredentialsError, ClientError

class BaseScraper(ABC):
    def __init__(self, base_url: str, name: str):
        self.base_url = base_url
        self.name = name
        self.jobs = []

    @abstractmethod
    def get_jobs(self, term: str) -> List[Dict[str, Any]]:
        """Fetch and return jobs for a given serch term."""
        pass

    def remove_older_jobs(self, days_threshold: int) -> None:
        """Removes jobs older than the specified number of days."""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        filtered_jobs = []
        for job in self.jobs:
            job_date = datetime.strptime(job['date_published'], "%Y-%m-%d")
            if job_date.date() >= cutoff_date.date():
                filtered_jobs.append(job)
        self.jobs = filtered_jobs

    def _extract_job_details(self, job_element) -> Dict[str, Any]:
        """Extract job details from a job element. To be implemented by subclasses."""
        return {
            "company": self.extract_company(job_element),
            "title": self.extract_title(job_element),
            "url": self.extract_url(job_element),
            "date_published": self.extract_date_published(job_element)
        }

    def _build_search_url(self, term: str) -> str:
        """Construct the search URL for the given term."""
        raise NotImplementedError("This scrapper does not use URL based search.")

    def _build_api_payload(self, term: str) -> dict:
        """Construct the API payload for the given term."""
        raise NotImplementedError("This scrapper does not use API based search.")

    @abstractmethod
    def extract_company(self, job_element) -> str:
        pass

    @abstractmethod
    def extract_title(self, job_element) -> str:
        pass

    @abstractmethod
    def extract_url(self, job_element) -> str:
        pass

    @abstractmethod
    def extract_date_published(self, job_element) -> str:
        pass

    @abstractmethod
    def extract_job_description(self, job_url: str) -> str:
        """Extract job description from the job URL."""
        pass

    @staticmethod
    def _connect_dynamodb_table(table_name: str):
        """Connect to a DynamoDB table.

        Args:
            table_name: Name of the DynamoDB table.

        Returns:
            boto3.resources.factory.dynamodb.Table: DynamoDB table resource.

        Raises:
            ValueError: If the table name is empty or AWS credentials are missing.
            botocore.exceptions.ClientError: If the table doesn’t exist or AWS access is denied.
        """
        if not table_name:
            raise ValueError("Table name cannot be empty.")

        try:
            ddb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
            return ddb.Table(table_name)
        except NoCredentialsError:
            raise ValueError("AWS credentials not configured.")
        except ClientError as e:
            raise ValueError(f"Failed to connect to DynamoDB table: {e}")

    def _store_new(self, job_id: str) -> None:
        """Store a new job ID in job cache.

        Args:
            job_id: Job ID to store.

        Raises:
            ValueError: If the job ID is empty or DynamoDB access fails.
        """
        if not job_id:
            raise ValueError("Job ID cannot be empty.")

        # Add RETENTION_DAYS to today's date
        expiry_date = datetime.now(timezone.utc) + timedelta(days=int(os.getenv("RETENTION_DAYS", 30)))

        # Convert to Unix timestamp
        expires_at = int(expiry_date.timestamp())

        try:
            table = self._connect_dynamodb_table(os.getenv('JOBS_TABLE'))
            table.put_item(
                Item={
                    "job_id": job_id,
                    "site": self.name,
                    "date_added": datetime.strftime(datetime.now(), '%Y-%m-%d'),
                    'expires_at': expires_at
                }
            )
        except ClientError as e:
            raise ValueError(f"Failed to save job in DynamoDB: {e}")

    def _get_existing_job_ids(self) -> set[str]:
        """Fetch all existing job IDs from DynamoDB."""
        table = self._connect_dynamodb_table(os.getenv('JOBS_TABLE'))
        response = table.scan(ProjectionExpression="job_id")
        return {item["job_id"] for item in response.get("Items", [])}

    def _store_new_jobs(self, new_jobs: list[str]) -> None:
        """Store new jobs in jobs cache"""
        if not new_jobs:
            return

        table = self._connect_dynamodb_table(os.getenv("JOBS_TABLE"))
        try:
            with table.batch_writer() as batch:
                for job_id in new_jobs:
                    # Add RETENTION_DAYS to today's date
                    expiry_date = datetime.now(timezone.utc) + timedelta(days=int(os.getenv("RETENTION_DAYS", 30)))

                    # Convert to Unix timestamp
                    expires_at = int(expiry_date.timestamp())

                    batch.put_item({
                        "job_id": job_id,
                        "site": self.name,
                        "date_added": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                        "expires_at": expires_at
                    })
        except ClientError as e:
            raise ValueError(f"Failed to save jobs in DynamoDB: {e}")
