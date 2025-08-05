"""
AI Service for generating questions and plans using OpenAI
"""
import json
import logging
from typing import List, Dict, Any
from openai import OpenAI
from config import settings
from schemas import (
    RefinementQuestion, 
    PlanStep, 
    PlanResource,
    QuestionGenerationResponse,
    PlanGenerationResponse
)

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def generate_refinement_questions(self, title: str, description: str) -> List[RefinementQuestion]:
        """
        Generate clarifying questions for an idea using LLM
        """
        prompt = f"""You are an expert consultant helping someone refine their business idea. 

Given this idea:
Title: "{title}"
Description: "{description}"

Generate 3-7 specific, thoughtful questions that will help clarify and improve this idea. Focus on:
- Target audience and users
- Implementation approach  
- Market positioning
- Technical requirements
- Business model considerations

Return ONLY a JSON array of questions in this exact format:
[
  {{"id": "q1", "question": "Who specifically are your target users and what problem does this solve for them?"}},
  {{"id": "q2", "question": "How do you envision users accessing this - web app, mobile app, browser extension, or API?"}},
  {{"id": "q3", "question": "What existing solutions are you competing with and how is yours different?"}}
]

Make each question specific to this idea. Avoid generic questions."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful business consultant. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            questions_json = response.choices[0].message.content.strip()
            logger.info(f"Generated questions JSON: {questions_json}")
            
            # Parse JSON response
            questions_data = json.loads(questions_json)
            
            # Convert to RefinementQuestion objects
            questions = [
                RefinementQuestion(id=q["id"], question=q["question"]) 
                for q in questions_data
            ]
            
            logger.info(f"Generated {len(questions)} questions for idea: {title}")
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM questions response: {e}")
            # Fallback to generic questions
            return self._get_fallback_questions()
        except Exception as e:
            logger.error(f"Failed to generate questions: {e}")
            return self._get_fallback_questions()

    async def generate_plan(self, title: str, description: str, answers: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate an implementation plan based on idea and refinement answers
        """
        # Format answers for the prompt
        answers_text = "\n".join([
            f"Q: {question_id}\nA: {answer}" 
            for question_id, answer in answers.items()
        ])

        prompt = f"""You are an expert project manager creating an implementation plan.

Original Idea:
Title: "{title}"
Description: "{description}"

Refinement Details:
{answers_text}

Create a detailed implementation plan with:
1. A clear 1-paragraph summary of the refined idea
2. 5-10 specific, actionable steps to build this
3. Helpful resources (tools, articles, services)

Return ONLY a JSON object in this exact format:
{{
  "summary": "A clear paragraph describing what will be built and for whom...",
  "steps": [
    {{"order": 1, "title": "Research and Planning", "description": "Analyze competitors and define core features", "estimated_time": "1-2 weeks"}},
    {{"order": 2, "title": "Design Mockups", "description": "Create wireframes and user interface designs", "estimated_time": "1 week"}}
  ],
  "resources": [
    {{"title": "Figma", "url": "https://figma.com", "type": "tool", "description": "For creating mockups and prototypes"}},
    {{"title": "OpenAI API", "url": "https://openai.com/api", "type": "service", "description": "For AI-powered features"}}
  ]
}}

Make it specific to this exact idea and answers."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful project manager. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            plan_json = response.choices[0].message.content.strip()
            logger.info(f"Generated plan JSON: {plan_json[:200]}...")
            
            # Parse JSON response
            plan_data = json.loads(plan_json)
            
            # Convert steps and resources to proper objects
            steps = [
                PlanStep(
                    order=step["order"],
                    title=step["title"], 
                    description=step["description"],
                    estimated_time=step.get("estimated_time")
                ) for step in plan_data["steps"]
            ]
            
            resources = [
                PlanResource(
                    title=res["title"],
                    url=res.get("url"),
                    type=res.get("type", "tool"),
                    description=res.get("description")
                ) for res in plan_data.get("resources", [])
            ]
            
            result = {
                "summary": plan_data["summary"],
                "steps": steps,
                "resources": resources
            }
            
            logger.info(f"Generated plan with {len(steps)} steps and {len(resources)} resources")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM plan response: {e}")
            return self._get_fallback_plan(title, description)
        except Exception as e:
            logger.error(f"Failed to generate plan: {e}")
            return self._get_fallback_plan(title, description)

    def _get_fallback_questions(self) -> List[RefinementQuestion]:
        """Fallback questions if LLM fails"""
        return [
            RefinementQuestion(id="q1", question="Who are your target users and what specific problem does this solve for them?"),
            RefinementQuestion(id="q2", question="How do you plan to build and deliver this solution?"),
            RefinementQuestion(id="q3", question="What makes your approach different from existing solutions?"),
            RefinementQuestion(id="q4", question="What's your timeline and what resources do you have available?")
        ]

    def _get_fallback_plan(self, title: str, description: str) -> Dict[str, Any]:
        """Fallback plan if LLM fails"""
        return {
            "summary": f"Implementation plan for '{title}': {description[:100]}... This plan needs to be refined with more specific details.",
            "steps": [
                PlanStep(order=1, title="Research Phase", description="Analyze the problem and existing solutions", estimated_time="1 week"),
                PlanStep(order=2, title="Planning Phase", description="Define requirements and create project roadmap", estimated_time="1 week"),
                PlanStep(order=3, title="Development Phase", description="Build the core functionality", estimated_time="4-6 weeks"),
                PlanStep(order=4, title="Testing Phase", description="Test with real users and gather feedback", estimated_time="2 weeks"),
                PlanStep(order=5, title="Launch Phase", description="Deploy and announce the solution", estimated_time="1 week")
            ],
            "resources": [
                PlanResource(title="Project Management Tool", type="tool", description="Use Trello, Notion, or similar for tracking progress"),
                PlanResource(title="User Feedback Platform", type="tool", description="Use Typeform or similar for collecting user input")
            ]
        }

    def generate_markdown(self, plan_data: Dict[str, Any], idea_title: str) -> str:
        """
        Generate markdown version of the plan
        """
        markdown = f"""# {idea_title} - Implementation Plan

## Summary
{plan_data["summary"]}

## Steps

"""
        
        for step in plan_data["steps"]:
            markdown += f"### {step.order}. {step.title}\n"
            markdown += f"{step.description}\n"
            if step.estimated_time:
                markdown += f"**Estimated Time:** {step.estimated_time}\n"
            markdown += "\n"
        
        if plan_data["resources"]:
            markdown += "## Resources\n\n"
            for resource in plan_data["resources"]:
                markdown += f"- **{resource.title}**"
                if resource.url:
                    markdown += f" ([Link]({resource.url}))"
                markdown += f" - {resource.description}\n"
        
        return markdown