import json
import logging
from string import Template
from typing import cast

from requests import request
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(
            self,
            api_key: str,
            model: str,
            api_url: str,
            prompt_file: str = "prompt.txt",
            temperature: float = 0.7,
            timeout: int = 60
    ) -> None:
        """Initialize the AI analyzer.

        Args:
            api_key: API key for authentication.
            model: Model to use for analysis.
            api_url: API endpoint URL.
            prompt_file: Path to the prompt template file.
            temperature: Temperature for AI responses (0.0-1.0).
        """
        self.api_key = api_key
        self.model = model
        self.api_url = api_url
        self.prompt_file = prompt_file
        self.temperature = temperature
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_message(self, resume: str, job_description: str) -> str:
        """Build the message payload for the AI API.

        Args:
            resume: Resume text.
            job_description: Job description text.

        Returns:
            Formatted message string.
        """
        if not resume or not job_description:
            raise ValueError("Resume and job description must not be empty")

        translation_table = str.maketrans({
            "\n": " ",
            "\r": " ",
            "\t": " "
        })

        try:
            with open(self.prompt_file, encoding="utf-8") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_file}")
        except OSError as e:
            raise OSError(f"Error reading prompt file: {e}")

        template = Template(prompt_template)
        message = template.substitute(resume=resume, job_description=job_description)
        message = message.translate(translation_table).strip()

        return message

    def analyze_job(self, resume: str, job_description: str) -> dict | None:
        """Query the AI API to analyze a job description against a resume.

            Args:
                resume: Resume text.
                job_description: Job description text

            Returns:
                Full API response as a dictionary, or None if an error occurs.
        """
        if not resume or not job_description:
           raise ValueError("Resume and job description must not be empty")

        try:
            message = self._build_message(resume, job_description)

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "response_format": {"type": "json_object"},
                "temperature": self.temperature,
            }

            response = request(
                "POST",
                url=self.api_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()   # Raises HTTPError for 4XX/5XX responses
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Check if result["choices"][0]["message"]["content"] is already a dict 
            # before parsing.
            try:
                parsed = json.loads(content) if isinstance(content, str) else content
                return cast(dict, parsed)
            except json.JSONDecodeError:
                return cast(dict, content) # Fallback: return raw content
                
        except RequestException as e:
            logger.exception(f"API request failed: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            logger.exception(f"Invalid API response: {e}")
            return None
