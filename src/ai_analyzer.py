import json
import logging
import re
import time
from string import Template

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
        num_retries: int = 3,
        request_delay: float = 1.5,  # seconds between API calls
    ) -> None:
        """Initialize the AI analyzer.

        Args:
            api_key: API key for authentication.
            provider: AI provider (e.g., "openai").
            model: Model to use for analysis.
            prompt_file: Path to the prompt template file.
            temperature: Temperature for AI responses (0.0-1.0).
            timeout: Timeout for API requests in seconds.
            num_retries: Number of retries for failed API requests.
            request_delay: Delay between API requests in seconds.
        """
        self.api_key = api_key
        self.provider = provider
        self.model = model
        self.prompt_file = prompt_file
        self.temperature = temperature
        self.timeout = timeout
        self.num_retries = num_retries
        self.request_delay = request_delay

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
        message = template.substitute(resume=resume)
        message = message.translate(translation_table).strip()

        return message

    @staticmethod
    def _extract_json_object(content: str) -> dict | None:
        """Extract and parse the first JSON object from a raw LLM response.

        Models frequently wrap the JSON in markdown code fences
        (```json ... ```) or add prose around it, which makes a plain
        json.loads() fail. This strips fences and falls back to the
        outermost {...} block before parsing.

        Args:
            content: Raw text returned by the model.

        Returns:
            The parsed dictionary, or None if no valid JSON object is found.
        """
        cleaned = content.strip()

        # Strip markdown code fences if present (```json ... ``` or ``` ... ```)
        fence_match = re.search(
            r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL | re.IGNORECASE
        )
        if fence_match:
            cleaned = fence_match.group(1).strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            # Fall back to the outermost {...} block, ignoring surrounding text
            block_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if not block_match:
                return None
            try:
                parsed = json.loads(block_match.group(0))
            except json.JSONDecodeError:
                return None

        return parsed if isinstance(parsed, dict) else None

    @staticmethod
    def _normalize_evaluation(evaluation: dict) -> dict:
        """Normalize an evaluation dict to the shape expected downstream.

        Ensures ``match_score`` is a string of the form "N/100", since the
        model sometimes returns a bare number.

        Args:
            evaluation: The parsed evaluation dict.

        Returns:
            The normalized evaluation dict.
        """
        score = evaluation.get("match_score")
        if isinstance(score, bool):
            evaluation["match_score"] = "0/100"
        elif isinstance(score, (int, float)):
            evaluation["match_score"] = f"{score}/100"
        elif isinstance(score, str) and "/" not in score:
            evaluation["match_score"] = f"{score.strip()}/100"
        return evaluation

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

            # Add a delay to respect API rate limits
            logger.debug(f"Delaying API call by {self.request_delay} seconds")
            time.sleep(self.request_delay)

            response = completion(
                model=f"{self.provider}/{self.model}",
                api_key=self.api_key,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": job_description},
                ],
                temperature=self.temperature,
                timeout=self.timeout,
                num_retries=self.num_retries,
                retry_strategy="exponential_backoff_retry",
            )

            if not response.choices:
                logger.debug("API response received: No choices returned")
                return None

            content = response.choices[0].message.content
            logger.debug(f"{'=' * 50}\nAPI response received:\n{content}\n{'=' * 50}")

            if isinstance(content, dict):
                return self._normalize_evaluation(content)

            if not isinstance(content, str):
                logger.warning(
                    "Unexpected AI response content type: %s",
                    type(content).__name__,
                )
                return None

            parsed = self._extract_json_object(content)
            if parsed is None:
                logger.warning(
                    "Could not parse a JSON object from the AI response: %.500s",
                    content,
                )
                return None

            return self._normalize_evaluation(parsed)

        except (APIError, RateLimitError) as e:
            logger.exception(f"API request failed: {e}")
            return None
