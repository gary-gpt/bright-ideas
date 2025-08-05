"""
AI service for handling OpenAI GPT interactions.
Provides brainstorming, idea refinement, and planning assistance.
"""
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
import openai
from openai import AsyncOpenAI
from config import settings


class AIService:
    """
    Service for AI-powered brainstorming and planning interactions.
    """
    
    def __init__(self):
        """Initialize the AI service with OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def refine_idea(
        self, 
        original_description: str, 
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Refine a vague idea into a structured concept.
        
        Args:
            original_description: The user's initial idea description
            conversation_history: Previous messages in the conversation
            
        Returns:
            Dict containing refined idea data and follow-up questions
        """
        system_prompt = """You are an expert brainstorming assistant. Your role is to help users transform vague ideas into clear, actionable concepts.

When a user presents an idea:
1. Ask clarifying questions to understand their vision
2. Help them identify the core problem being solved
3. Suggest target audiences and use cases
4. Provide implementation insights without writing code
5. Guide them toward a refined, structured idea

Be encouraging, ask thoughtful questions, and help them think through their concept systematically."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        else:
            # Initial refinement request
            user_message = f"I have this idea: {original_description}\n\nHelp me refine and clarify this concept. What questions should I consider?"
            messages.append({"role": "user", "content": user_message})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message.content
            
            # Generate follow-up questions
            questions = await self._generate_followup_questions(original_description, assistant_message)
            
            return {
                "response": assistant_message,
                "questions": questions,
                "refined_data": await self._extract_structured_data(original_description, assistant_message)
            }
            
        except Exception as e:
            raise Exception(f"AI refinement failed: {str(e)}")
    
    async def generate_build_plan(
        self, 
        idea_data: Dict[str, Any], 
        requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a structured build plan from a refined idea.
        
        Args:
            idea_data: Refined idea information
            requirements: Additional user requirements
            
        Returns:
            Structured build plan with components, phases, and tasks
        """
        system_prompt = """You are an expert project planner. Create detailed, actionable build plans for user projects.

Given a refined idea, create a structured plan that includes:
1. Project overview and objectives
2. Key components/features needed
3. Development phases with clear milestones
4. Specific tasks for each phase
5. Technical considerations and recommendations
6. Success criteria and testing approach

Focus on planning and documentation - do not generate actual code. Provide text-based deliverables and clear next steps."""
        
        idea_summary = f"""
Title: {idea_data.get('title', 'Untitled Idea')}
Description: {idea_data.get('refined_description', idea_data.get('original_description', ''))}
Problem Statement: {idea_data.get('problem_statement', 'Not specified')}
Target Audience: {idea_data.get('target_audience', 'Not specified')}
Implementation Notes: {idea_data.get('implementation_notes', {})}
"""
        
        user_message = f"Create a detailed build plan for this idea:\n\n{idea_summary}"
        if requirements:
            user_message += f"\n\nAdditional requirements: {requirements}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.6,
                max_tokens=2000
            )
            
            plan_content = response.choices[0].message.content
            
            # Structure the plan data
            structured_plan = await self._structure_build_plan(plan_content)
            
            return structured_plan
            
        except Exception as e:
            raise Exception(f"Build plan generation failed: {str(e)}")
    
    async def chat_response(
        self, 
        message: str, 
        context: Dict[str, Any],
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate a conversational response for build mode collaboration.
        
        Args:
            message: User's message
            context: Current project context
            conversation_history: Previous conversation messages
            
        Returns:
            AI assistant response
        """
        system_prompt = """You are a collaborative planning assistant working with a user on their project.

Current context:
- Mode: Build planning and collaboration
- Focus: Help refine implementation details, suggest improvements, answer questions
- Output: Provide helpful text-based planning insights, not code

Be conversational, helpful, and focused on planning and strategy discussions."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add context if available
        if context.get('idea'):
            context_msg = f"Project context: {context['idea'].get('title', 'Current Project')}"
            if context.get('build_plan'):
                context_msg += f"\nCurrent plan status: {len(context['build_plan'].get('phases', []))} phases defined"
            messages.append({"role": "system", "content": context_msg})
        
        # Add conversation history
        messages.extend(conversation_history[-10:])  # Keep last 10 messages for context
        messages.append({"role": "user", "content": message})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Chat response failed: {str(e)}")
    
    async def _generate_followup_questions(self, original_idea: str, response: str) -> List[str]:
        """Generate relevant follow-up questions for idea refinement."""
        prompt = f"""Based on this idea: "{original_idea}" and this response: "{response[:500]}..."

Generate 3-5 specific, thoughtful follow-up questions that would help clarify and improve the idea. Return as a simple list."""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=300
            )
            
            questions_text = response.choices[0].message.content
            # Parse questions from response (assuming each line is a question)
            questions = [q.strip().lstrip('•-123456789. ') for q in questions_text.split('\n') if q.strip()]
            return questions[:5]  # Limit to 5 questions
            
        except Exception:
            # Fallback questions if AI call fails
            return [
                "Who is your target audience for this idea?",
                "What problem does this solve?",
                "How would users interact with this?",
                "What makes this unique or valuable?",
                "What would success look like?"
            ]
    
    async def _extract_structured_data(self, original_idea: str, ai_response: str) -> Dict[str, Any]:
        """Extract structured data from AI refinement response."""
        # This is a simplified extraction - in production, you might use more sophisticated parsing
        return {
            "key_insights": [insight.strip() for insight in ai_response.split('.') if len(insight.strip()) > 20][:3],
            "suggested_focus_areas": [],
            "complexity_level": "medium",  # Could be determined by AI
            "estimated_effort": "moderate"  # Could be determined by AI
        }
    
    async def _structure_build_plan(self, plan_content: str) -> Dict[str, Any]:
        """Structure the AI-generated build plan into organized components."""
        # Parse the plan content into structured data
        # This is a simplified version - production would have more sophisticated parsing
        
        return {
            "overview": plan_content[:500] + "..." if len(plan_content) > 500 else plan_content,
            "components": [
                {"name": "Research & Planning", "description": "Initial research and detailed planning"},
                {"name": "Core Development", "description": "Build main functionality"},
                {"name": "Testing & Refinement", "description": "Test and refine the solution"},
                {"name": "Launch Preparation", "description": "Prepare for deployment/launch"}
            ],
            "phases": [
                {
                    "name": "Discovery",
                    "duration": "1-2 weeks",
                    "tasks": ["Market research", "User interviews", "Technical feasibility"],
                    "deliverables": ["Research report", "Technical specifications"]
                },
                {
                    "name": "Development",
                    "duration": "4-6 weeks", 
                    "tasks": ["Core feature development", "Integration work", "Initial testing"],
                    "deliverables": ["Working prototype", "Test results"]
                },
                {
                    "name": "Refinement",
                    "duration": "2-3 weeks",
                    "tasks": ["User feedback integration", "Performance optimization", "Documentation"],
                    "deliverables": ["Final product", "User documentation"]
                }
            ],
            "success_criteria": [
                "Clear problem-solution fit",
                "Positive user feedback",
                "Technical stability",
                "Meets original objectives"
            ],
            "full_content": plan_content
        }


# Global AI service instance
ai_service = AIService()