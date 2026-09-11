import json
import logging
from string import Template
from typing import cast

from litellm import completion
from litellm.exceptions import APIError, RateLimitError

logger = logging.getLogger(__name__)


class AIAnalyzer:
    def __init__(
        self,
        api_key: str,
        provider: str,
        model: str,
        prompt_file: str = "prompt.txt",
        temperature: float = 0.7,
        timeout: int = 60,
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
        self.provider = provider
        self.model = model
        self.prompt_file = prompt_file
        self.temperature = temperature
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_system_instructions(self, resume: str) -> str:
        """Build the instructions for the AI system based on the resume.

        Args:
            resume: Resume text.

        Returns:
            Formatted message string.
        """
        if not resume:
            raise ValueError("Resume must not be empty")

        translation_table = str.maketrans({"\n": " ", "\r": " ", "\t": " "})

        try:
            with open(self.prompt_file, encoding="utf-8") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_file}")
        except OSError as e:
            raise OSError(f"Error reading prompt file: {e}")

        template = Template(prompt_template)
        message = template.substitute(resume=resume,)
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
            prompt = self._build_system_instructions(resume)

            response = completion(
                model=f"{self.provider}/{self.model}",
                api_key=self.api_key,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": job_description}
                ],
                temperature=self.temperature,
                timeout=self.timeout,
                num_retries=3,
            ) 

            if not response.choices:
                return None

            content = response.choices[0].message.content

            try:
                parsed = json.loads(content) if isinstance(content, str) else content
                return cast(dict, parsed)
            except json.JSONDecodeError:
                return cast(dict, content)

        except (APIError, RateLimitError) as e:
            logger.exception(f"API request failed: {e}")
            return None

