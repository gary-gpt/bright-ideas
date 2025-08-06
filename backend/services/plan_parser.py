"""
Plan parsing utilities for converting markdown/text into structured plan data
"""
import re
from typing import List, Dict, Any, Tuple
from schemas import PlanStep, PlanResource


def parse_markdown_plan(content: str) -> Dict[str, Any]:
    """
    Parse markdown/text content into structured plan data
    
    Expected format:
    # Title
    
    ## Summary
    Text summary here...
    
    ## Steps / Implementation / Plan
    1. Step title - description (time: X hours)
    2. Another step - description
    
    ## Resources / Tools
    - Tool name - description
    - [Tool name](url) - description
    """
    lines = content.strip().split('\n')
    
    summary = ""
    steps = []
    resources = []
    
    current_section = None
    current_content = []
    step_order = 1
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect section headers
        if line.startswith('##'):
            # Process previous section
            if current_section and current_content:
                if current_section == 'summary':
                    summary = '\n'.join(current_content).strip()
                elif current_section == 'steps':
                    steps.extend(_parse_steps('\n'.join(current_content), step_order))
                    step_order += len(steps)
                elif current_section == 'resources':
                    resources.extend(_parse_resources('\n'.join(current_content)))
            
            # Start new section
            current_content = []
            section_header = line.lower()
            if 'summary' in section_header:
                current_section = 'summary'
            elif any(word in section_header for word in ['step', 'implementation', 'plan', 'breakdown']):
                current_section = 'steps'
            elif any(word in section_header for word in ['resource', 'tool', 'reference', 'link']):
                current_section = 'resources'
            else:
                current_section = None
                
        elif line.startswith('#'):
            # Skip main title, but could extract it later
            continue
        else:
            # Add to current section content
            if current_section:
                current_content.append(line)
    
    # Process final section
    if current_section and current_content:
        if current_section == 'summary':
            summary = '\n'.join(current_content).strip()
        elif current_section == 'steps':
            steps.extend(_parse_steps('\n'.join(current_content), step_order))
        elif current_section == 'resources':
            resources.extend(_parse_resources('\n'.join(current_content)))
    
    # If no explicit sections found, try to parse the whole content
    if not summary and not steps and not resources:
        return _parse_unstructured_content(content)
    
    # Generate summary if missing
    if not summary:
        summary = _generate_default_summary(content, steps)
    
    return {
        "summary": summary,
        "steps": steps,
        "resources": resources
    }


def _parse_steps(content: str, start_order: int = 1) -> List[PlanStep]:
    """Parse steps from content"""
    steps = []
    order = start_order
    
    # Look for numbered lists, bullet points, or markdown headers
    step_patterns = [
        r'^(\d+)\.\s*(.+)',  # 1. Step title
        r'^[-*]\s*(.+)',     # - Step title or * Step title  
        r'^#{1,4}\s*(.+)',   # ### Step title
    ]
    
    lines = content.split('\n')
    current_step = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a step header
        step_match = None
        for pattern in step_patterns:
            match = re.match(pattern, line)
            if match:
                step_match = match
                break
        
        if step_match:
            # Save previous step
            if current_step:
                steps.append(current_step)
            
            # Extract step info
            if pattern.startswith(r'^(\d+)'):
                # Numbered list - use the number
                step_title = step_match.group(2)
                order = int(step_match.group(1))
            else:
                # Bullet or header - use sequential order
                step_title = step_match.group(1)
            
            # Parse title and description
            title, description, time_estimate = _parse_step_details(step_title)
            
            current_step = PlanStep(
                order=order,
                title=title,
                description=description,
                estimated_time=time_estimate
            )
            order += 1
        else:
            # This is additional description for current step
            if current_step and line:
                # Append to description
                if current_step.description:
                    current_step.description += " " + line
                else:
                    current_step.description = line
    
    # Add final step
    if current_step:
        steps.append(current_step)
    
    return steps


def _parse_step_details(step_text: str) -> Tuple[str, str, str]:
    """Parse step text to extract title, description, and time estimate"""
    # Look for time estimates in parentheses
    time_pattern = r'\((?:time:|duration:|estimate:)?\s*([^)]+)\)'
    time_match = re.search(time_pattern, step_text, re.IGNORECASE)
    time_estimate = None
    
    if time_match:
        time_estimate = time_match.group(1).strip()
        step_text = re.sub(time_pattern, '', step_text, flags=re.IGNORECASE).strip()
    
    # Split title and description by common separators
    separators = [' - ', ': ', ' – ', ' — ']
    title = step_text
    description = ""
    
    for sep in separators:
        if sep in step_text:
            parts = step_text.split(sep, 1)
            title = parts[0].strip()
            description = parts[1].strip()
            break
    
    # Clean up title
    title = re.sub(r'^[*#-]\s*', '', title).strip()
    
    return title, description, time_estimate


def _parse_resources(content: str) -> List[PlanResource]:
    """Parse resources from content"""
    resources = []
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Remove bullet points
        line = re.sub(r'^[-*]\s*', '', line)
        
        # Look for markdown links [title](url)
        link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)
        if link_match:
            title = link_match.group(1)
            url = link_match.group(2)
            # Remove the link from description
            description = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', '', line).strip()
            description = re.sub(r'^\s*-\s*', '', description).strip()
        else:
            # No link, parse title - description format
            url = None
            parts = line.split(' - ', 1)
            title = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else ""
        
        if title:
            # Detect resource type based on title/description
            resource_type = _detect_resource_type(title, description)
            
            resources.append(PlanResource(
                title=title,
                url=url,
                type=resource_type,
                description=description
            ))
    
    return resources


def _detect_resource_type(title: str, description: str) -> str:
    """Detect resource type from title and description"""
    combined = f"{title} {description}".lower()
    
    if any(word in combined for word in ['api', 'service', 'platform', 'subscription']):
        return "service"
    elif any(word in combined for word in ['library', 'framework', 'tool', 'software', 'cli', 'package']):
        return "tool"
    elif any(word in combined for word in ['article', 'blog', 'tutorial', 'guide', 'documentation', 'docs']):
        return "article"
    elif any(word in combined for word in ['github', 'repo', 'repository', 'code']):
        return "repository"
    else:
        return "tool"  # Default


def _parse_unstructured_content(content: str) -> Dict[str, Any]:
    """Parse content that doesn't have clear sections"""
    # Try to extract summary from first paragraph
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    summary = paragraphs[0] if paragraphs else "Uploaded implementation plan"
    
    # Look for any numbered or bulleted items as steps
    steps = _parse_steps(content)
    
    # If no structured steps found, create a single step with all content
    if not steps:
        steps = [PlanStep(
            order=1,
            title="Implementation Plan",
            description=content[:500] + "..." if len(content) > 500 else content,
            estimated_time=None
        )]
    
    return {
        "summary": summary,
        "steps": steps,
        "resources": []
    }


def _generate_default_summary(content: str, steps: List[PlanStep]) -> str:
    """Generate a default summary if none was provided"""
    if steps:
        step_count = len(steps)
        return f"Implementation plan with {step_count} steps. {content[:100]}..."
    else:
        return f"Implementation plan: {content[:150]}..."