"""
AI Service for generating questions and plans using OpenAI
"""
import json
import logging
import re
from typing import List, Dict, Any, Tuple
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
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout
        )
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

        # Detect project type and get contextual prompt
        project_type, persona = self._detect_project_type(title, description, answers)
        prompt = self._get_contextual_prompt(project_type, persona, title, description, answers_text)
        
        logger.info(f"Generating plan for project type: {project_type} with persona: {persona}")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are {persona} helping break down a project into its functional components. Always respond with valid JSON only. Focus on architecture and implementation, not generic project phases."},
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

    def _detect_project_type(self, title: str, description: str, answers: Dict[str, str] = None) -> Tuple[str, str]:
        """
        Detect the project type based on content to select appropriate prompt template
        Returns: (project_type, persona)
        """
        combined_text = f"{title} {description}".lower()
        if answers:
            combined_text += " " + " ".join(answers.values()).lower()
        
        # Detection patterns for different project types
        if any(word in combined_text for word in ['api', 'scrape', 'crawl', 'data pipeline', 'etl', 'automation', 'bot', 'script', 'cli']):
            return "technical_tool", "a solutions architect"
        elif any(word in combined_text for word in ['blog', 'content', 'newsletter', 'course', 'book', 'writing', 'publish']):
            return "content_creation", "a content strategist"
        elif any(word in combined_text for word in ['marketplace', 'ecommerce', 'subscription', 'saas', 'platform', 'service']):
            return "business_service", "a business analyst"
        elif any(word in combined_text for word in ['research', 'analysis', 'study', 'survey', 'report', 'dashboard']):
            return "research_analysis", "a research analyst"
        elif any(word in combined_text for word in ['app', 'mobile', 'web app', 'website', 'frontend', 'ui']):
            return "application", "a product architect"
        elif any(word in combined_text for word in ['community', 'network', 'forum', 'social', 'group']):
            return "community_platform", "a community strategist"
        else:
            return "general", "a strategic consultant"

    def _get_contextual_prompt(self, project_type: str, persona: str, title: str, description: str, answers_text: str) -> str:
        """
        Generate a context-aware prompt based on project type
        """
        # Base context that varies by project type
        context_templates = {
            "technical_tool": """Break down this project by its technical architecture and data flow:
- What data sources and ingestion methods are needed?
- What processing or transformation logic is required?
- What storage or caching strategy makes sense?
- What's the simplest MVP that delivers core value?
- What are the key technical dependencies and risks?""",
            
            "content_creation": """Break down this project by content operations and distribution:
- What content creation or curation process is needed?
- What tools and workflows will streamline production?
- How will content be organized and discovered?
- What distribution channels make sense?
- What's the minimum viable content strategy?""",
            
            "business_service": """Break down this project by business operations and value delivery:
- What's the core value proposition and how is it delivered?
- What operational processes are needed?
- How will customers discover and engage with this?
- What's the revenue model and pricing strategy?
- What's the leanest path to first paying customer?""",
            
            "research_analysis": """Break down this project by data collection and insight generation:
- What data needs to be collected and from where?
- What analysis methods will generate insights?
- How will findings be validated and presented?
- What tools enable efficient research workflow?
- What's the minimum viable research output?""",
            
            "application": """Break down this project by user experience and system design:
- What are the core user flows and features?
- What's the data model and state management approach?
- What integrations or APIs are needed?
- What's the simplest deployable version?
- What are the key technical and UX decisions?""",
            
            "community_platform": """Break down this project by community dynamics and engagement:
- What brings people together and keeps them engaged?
- What moderation and governance is needed?
- How will the community grow and stay healthy?
- What features enable meaningful connections?
- What's the minimum viable community experience?""",
            
            "general": """Break down this project by its core components and dependencies:
- What are the main functional components?
- How do these components interact?
- What are the critical dependencies?
- What's the simplest working version?
- What are the key decisions and trade-offs?"""
        }
        
        breakdown_approach = context_templates.get(project_type, context_templates["general"])
        
        return f"""You are {persona} creating an implementation breakdown for a specific project.

Original Idea:
Title: "{title}"
Description: "{description}"

Refinement Details:
{answers_text}

Create a practical implementation plan that breaks down the project by its functional components and logical layers, NOT by generic project phases.

{breakdown_approach}

DO NOT structure your response using generic phases like: Research, Planning, Development, Testing, Launch.
Instead, identify the specific components, systems, or workflows needed for THIS particular idea.

Return ONLY a JSON object in this exact format:
{{
  "summary": "A clear paragraph describing the refined concept, its target users, and core value proposition...",
  "steps": [
    {{"order": 1, "title": "[Specific component/layer name]", "description": "[What this component does and why it's needed]", "estimated_time": "[Realistic time estimate]"}},
    {{"order": 2, "title": "[Another specific component]", "description": "[Its purpose and implementation approach]", "estimated_time": "[Time estimate]"}}
  ],
  "resources": [
    {{"title": "[Specific tool/service name]", "url": "[actual URL if applicable]", "type": "[tool/service/reference]", "description": "[Why this specific resource helps]"}}
  ]
}}

Make each step and resource specific to this exact idea. Focus on WHAT needs to be built and HOW the pieces fit together."""

    def _get_fallback_questions(self) -> List[RefinementQuestion]:
        """Fallback questions if LLM fails"""
        return [
            RefinementQuestion(id="q1", question="Who are your target users and what specific problem does this solve for them?"),
            RefinementQuestion(id="q2", question="How do you plan to build and deliver this solution?"),
            RefinementQuestion(id="q3", question="What makes your approach different from existing solutions?"),
            RefinementQuestion(id="q4", question="What's your timeline and what resources do you have available?")
        ]

    def _get_fallback_plan(self, title: str, description: str) -> Dict[str, Any]:
        """Fallback plan if LLM fails - now with more contextual approach"""
        # Try to detect project type even for fallback
        project_type, _ = self._detect_project_type(title, description)
        
        # More contextual fallback steps based on project type
        if project_type == "technical_tool":
            steps = [
                PlanStep(order=1, title="Data Source Integration", description="Define and connect to required data sources", estimated_time="1 week"),
                PlanStep(order=2, title="Core Processing Logic", description="Build the main data transformation or automation logic", estimated_time="2-3 weeks"),
                PlanStep(order=3, title="Storage & Output Layer", description="Implement data persistence and output mechanisms", estimated_time="1 week"),
                PlanStep(order=4, title="Error Handling & Monitoring", description="Add robust error handling and logging", estimated_time="3-4 days"),
                PlanStep(order=5, title="CLI or API Interface", description="Create user interface for the tool", estimated_time="1 week")
            ]
        elif project_type == "content_creation":
            steps = [
                PlanStep(order=1, title="Content Strategy & Templates", description="Define content types and create templates", estimated_time="3-4 days"),
                PlanStep(order=2, title="Creation Workflow", description="Set up tools and processes for content production", estimated_time="1 week"),
                PlanStep(order=3, title="Organization System", description="Build categorization and tagging structure", estimated_time="3-4 days"),
                PlanStep(order=4, title="Distribution Channels", description="Set up publishing and distribution methods", estimated_time="1 week"),
                PlanStep(order=5, title="Analytics & Feedback", description="Implement tracking and audience feedback loops", estimated_time="3-4 days")
            ]
        else:
            # Generic but still avoiding phase-based structure
            steps = [
                PlanStep(order=1, title="Core Functionality", description="Define and build the main value-delivering features", estimated_time="2-3 weeks"),
                PlanStep(order=2, title="User Interface", description="Create the interface for user interaction", estimated_time="1-2 weeks"),
                PlanStep(order=3, title="Data Management", description="Set up data storage and retrieval systems", estimated_time="1 week"),
                PlanStep(order=4, title="Integration Points", description="Connect with necessary external services", estimated_time="1 week"),
                PlanStep(order=5, title="Deployment & Operations", description="Set up hosting and operational processes", estimated_time="3-4 days")
            ]
        
        return {
            "summary": f"Implementation breakdown for '{title}': {description[:100]}... This is a fallback plan that should be refined with more specific details based on your requirements.",
            "steps": steps,
            "resources": [
                PlanResource(title="Documentation Tool", type="tool", description="Use Notion, Obsidian, or similar for project documentation"),
                PlanResource(title="Version Control", type="tool", description="Git repository for tracking changes and collaboration")
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