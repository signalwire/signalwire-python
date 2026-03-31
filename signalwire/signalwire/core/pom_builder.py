"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
PomBuilder for creating structured POM prompts for SignalWire AI Agents
"""

try:
    from signalwire_pom.pom import PromptObjectModel, Section
except ImportError:
    raise ImportError(
        "signalwire-pom package is required. "
        "Install it with: pip install signalwire-pom"
    )

from typing import List, Dict, Any, Optional, Union


class PomBuilder:
    """
    Builder class for creating structured prompts using the Prompt Object Model.
    
    This class is a flexible wrapper around the POM API that allows for:
    - Dynamic creation of sections on demand
    - Adding content to existing sections
    - Nesting subsections
    - Rendering to markdown or XML
    
    Unlike previous implementations, there are no predefined section types -
    you can create any section structure that fits your needs.
    """
    
    def __init__(self):
        """Initialize a new POM builder with an empty POM"""
        self.pom = PromptObjectModel()
        self._sections: Dict[str, Section] = {}
    
    def add_section(self, title: str, body: str = "", bullets: Optional[List[str]] = None, 
                    numbered: bool = False, numbered_bullets: bool = False, 
                    subsections: Optional[List[Dict[str, Any]]] = None) -> 'PomBuilder':
        """
        Add a new section to the POM
        
        Args:
            title: Section title
            body: Optional body text
            bullets: Optional list of bullet points
            numbered: Whether to number this section
            numbered_bullets: Whether to number bullet points
            subsections: Optional list of subsection objects
            
        Returns:
            Self for method chaining
        """
        section = self.pom.add_section(
            title=title, 
            body=body, 
            bullets=bullets or [],
            numbered=numbered,
            numberedBullets=numbered_bullets
        )
        self._sections[title] = section
        
        # Process subsections if provided
        if subsections:
            for subsection_data in subsections:
                if 'title' in subsection_data:
                    subsection_title = subsection_data['title']
                    subsection_body = subsection_data.get('body', '')
                    subsection_bullets = subsection_data.get('bullets', [])
                    
                    section.add_subsection(
                        title=subsection_title,
                        body=subsection_body,
                        bullets=subsection_bullets or []
                    )
        
        return self
    
    def add_to_section(self, title: str, body: Optional[str] = None, bullet: Optional[str] = None, bullets: Optional[List[str]] = None) -> 'PomBuilder':
        """
        Add content to an existing section
        
        Args:
            title: Section title
            body: Text to append to the section body
            bullet: Single bullet to add
            bullets: List of bullets to add
            
        Returns:
            Self for method chaining
        """
        # Create section if it doesn't exist - auto-vivification
        if title not in self._sections:
            self.add_section(title)
            
        section = self._sections[title]
        
        # Add body text if provided
        if body:
            if hasattr(section, 'body') and section.body:
                section.body = f"{section.body}\n\n{body}"
            else:
                section.body = body
                
        # Process bullets
        if bullet:
            section.bullets.append(bullet)
                
        if bullets:
            section.bullets.extend(bullets)
                
        return self
    
    def add_subsection(self, parent_title: str, title: str, body: str = "", 
                       bullets: Optional[List[str]] = None) -> 'PomBuilder':
        """
        Add a subsection to an existing section, creating the parent if needed
        
        Args:
            parent_title: Title of the parent section
            title: Title for the new subsection
            body: Optional body text
            bullets: Optional list of bullet points
            
        Returns:
            Self for method chaining
        """
        # Create parent section if it doesn't exist - auto-vivification
        if parent_title not in self._sections:
            self.add_section(parent_title)
            
        parent = self._sections[parent_title]
        subsection = parent.add_subsection(
            title=title,
            body=body,
            bullets=bullets or []
        )
        return self
    
    def has_section(self, title: str) -> bool:
        """
        Check if a section with the given title exists
        
        Args:
            title: Section title to check
            
        Returns:
            True if the section exists, False otherwise
        """
        return title in self._sections
    
    def get_section(self, title: str) -> Optional[Section]:
        """
        Get a section by title
        
        Args:
            title: Section title
            
        Returns:
            Section object or None if not found
        """
        return self._sections.get(title)
    
    def render_markdown(self) -> str:
        """Render the POM as markdown"""
        return self.pom.render_markdown()
    
    def render_xml(self) -> str:
        """Render the POM as XML"""
        return self.pom.render_xml()
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert the POM to a list of section dictionaries"""
        return self.pom.to_dict()
        
    def to_json(self) -> str:
        """Convert the POM to a JSON string"""
        return self.pom.to_json()
    
    @classmethod
    def from_sections(cls, sections: List[Dict[str, Any]]) -> 'PomBuilder':
        """
        Create a PomBuilder from a list of section dictionaries
        
        Args:
            sections: List of section definition dictionaries
            
        Returns:
            A new PomBuilder instance with the sections added
        """
        builder = cls()
        builder.pom = PromptObjectModel.from_json(sections)
        # Rebuild the sections dict
        for section in builder.pom.sections:
            if section.title:
                builder._sections[section.title] = section
        return builder
