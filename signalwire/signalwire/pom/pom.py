from typing import List, Optional, Union
import json
import yaml

class Section:
    """
    Represents a section in the Prompt Object Model.
    
    Each section contains a title, optional body text, optional bullet points,
    and can have any number of nested subsections.
    
    Attributes:
        title (str): The name of the section.
        body (str): A paragraph of text associated with the section.
        bullets (List[str]): Bullet-pointed items.
        subsections (List[Section]): Nested sections with the same structure.
        numbered (bool): Whether this section should be numbered.
        numberedBullets (bool): Whether bullets should be numbered instead of using bullet points.
    """
    def __init__(self, title: Optional[str] = None, *, body: str = '', bullets: Optional[List[str]] = None, 
                 numbered: Optional[bool] = None, numberedBullets: bool = False):
        self.title = title
        
        # Validate body is a string
        if not isinstance(body, str):
            raise TypeError(f"body must be a string, not {type(body).__name__}. "
                          f"If you meant to pass a list of bullet points, use bullets parameter instead.")
        self.body = body
        
        # Validate bullets is a list if provided
        if bullets is not None and not isinstance(bullets, list):
            raise TypeError(f"bullets must be a list or None, not {type(bullets).__name__}")
        self.bullets = bullets or []
        
        self.subsections: List['Section'] = []
        self.numbered = numbered
        self.numberedBullets = numberedBullets

    def add_body(self, body: str):
        """Add or replace the body text for this section."""
        if not isinstance(body, str):
            raise TypeError(f"body must be a string, not {type(body).__name__}")
        self.body = body

    def add_bullets(self, bullets: List[str]):
        """Add bullet points to this section."""
        if not isinstance(bullets, list):
            raise TypeError(f"bullets must be a list, not {type(bullets).__name__}")
        self.bullets.extend(bullets)

    def add_subsection(self, title: str, *, body: str = '', bullets: Optional[List[str]] = None,
                      numbered: bool = False, numberedBullets: bool = False) -> 'Section':
        """
        Add a subsection to this section.
        
        Args:
            title: The title of the subsection
            body: Optional body text for the subsection
            bullets: Optional list of bullet points
            numbered: Whether this section should be numbered
            numberedBullets: Whether bullets should be numbered
            
        Returns:
            The newly created Section object
            
        Raises:
            ValueError: If the title is None or if the section has neither a body nor bullets
        """
        # Validate that subsections must have a title
        if title is None:
            raise ValueError("Subsections must have a title")
            
        # Create the subsection (validation will happen when content is added)
        subsection = Section(title, body=body, bullets=bullets or [], 
                            numbered=numbered, numberedBullets=numberedBullets)
        self.subsections.append(subsection)
        return subsection

    def to_dict(self):
        """Convert the section to a dictionary representation."""
        data = {}
        
        # Add keys in specific order: title, body, bullets, subsections
        if self.title is not None:
            data["title"] = self.title
            
        if self.body:
            data["body"] = self.body
            
        if self.bullets:
            data["bullets"] = self.bullets
            
        if self.subsections:
            data["subsections"] = [s.to_dict() for s in self.subsections]
        
        # Add remaining attributes
        if self.numbered:
            data["numbered"] = self.numbered
        if self.numberedBullets:
            data["numberedBullets"] = self.numberedBullets
        return data

    def render_markdown(self, level: int = 2, section_number: Optional[List[int]] = None) -> str:
        """
        Render this section and all its subsections as markdown.
        
        Args:
            level: The heading level to start with (default: 2, which corresponds to ##)
            section_number: The current section number for numbered sections
            
        Returns:
            A string containing the markdown representation
        """
        md = []
        
        # Initialize section numbering if this is the top level call
        if section_number is None:
            section_number = []
        
        # Handle section title with optional numbering
        if self.title is not None:
            prefix = ""
            if section_number:  # If we have a section number, use it
                prefix = f"{'.'.join(map(str, section_number))}. "
            md.append(f"{'#' * level} {prefix}{self.title}\n")
        
        # Add body text
        if self.body:
            md.append(f"{self.body}\n")
        
        # Add bullets with optional numbering
        for i, bullet in enumerate(self.bullets, 1):
            if self.numberedBullets:
                md.append(f"{i}. {bullet}")
            else:
                md.append(f"- {bullet}")
        
        if self.bullets:
            md.append("")
        
        # Check if any subsection has numbered=True
        any_subsection_numbered = any(sub.numbered for sub in self.subsections)
        
        # Process subsections with proper numbering
        for i, subsection in enumerate(self.subsections, 1):
            # Only increment section number if this section has a title
            # or if we're not at the root level (section_number is not empty)
            if self.title is not None or section_number:
                # If any subsection is numbered, number all siblings unless explicitly false
                if any_subsection_numbered and subsection.numbered is not False:
                    new_section_number = section_number + [i]
                else:
                    new_section_number = section_number
                next_level = level + 1
            else:
                # We're at a root section with no title, don't increment numbering
                new_section_number = section_number
                next_level = level
                
            md.append(subsection.render_markdown(next_level, new_section_number))
        
        return "\n".join(md)

    def render_xml(self, indent: int = 0, section_number: Optional[List[int]] = None) -> str:
        """
        Render this section and all its subsections as XML.
        
        Args:
            indent: The indentation level to start with (default: 0)
            section_number: The current section number for numbered sections
            
        Returns:
            A string containing the XML representation
        """
        indent_str = "  " * indent
        xml = []
        
        # Initialize section numbering if this is the top level call
        if section_number is None:
            section_number = []
        
        # Start section tag
        xml.append(f'{indent_str}<section>')
        
        # Title if present, with optional numbering
        if self.title is not None:
            prefix = ""
            if section_number:  # If we have a section number, use it (regardless of self.numbered)
                prefix = f"{'.'.join(map(str, section_number))}. "
            xml.append(f'{indent_str}  <title>{prefix}{self.title}</title>')
        
        # Body content if present
        if self.body:
            xml.append(f'{indent_str}  <body>{self.body}</body>')
        
        # Bullets if present
        if self.bullets:
            xml.append(f'{indent_str}  <bullets>')
            for i, bullet in enumerate(self.bullets, 1):
                if self.numberedBullets:
                    xml.append(f'{indent_str}    <bullet id="{i}">{bullet}</bullet>')
                else:
                    xml.append(f'{indent_str}    <bullet>{bullet}</bullet>')
            xml.append(f'{indent_str}  </bullets>')
        
        # Subsections if present
        if self.subsections:
            xml.append(f'{indent_str}  <subsections>')
            # Check if any subsection has numbered=True
            any_subsection_numbered = any(sub.numbered for sub in self.subsections)
            
            for i, subsection in enumerate(self.subsections, 1):
                # Only increment section number if this section has a title
                # or if we're not at the root level (section_number is not empty)
                if self.title is not None or section_number:
                    # If any subsection is numbered, number all siblings unless explicitly false
                    if any_subsection_numbered and subsection.numbered is not False:
                        new_section_number = section_number + [i]
                    else:
                        new_section_number = section_number
                else:
                    # We're at a root section with no title, don't increment numbering
                    new_section_number = section_number
                
                xml.append(subsection.render_xml(indent + 2, new_section_number))
            xml.append(f'{indent_str}  </subsections>')
        
        # Closing tag
        xml.append(f'{indent_str}</section>')
        
        return "\n".join(xml)


class PromptObjectModel:
    """
    A structured data format for composing, organizing, and rendering prompt 
    instructions for large language models.
    
    The Prompt Object Model provides a tree-based representation of a prompt
    document composed of nested sections, each of which can include a title,
    body text, bullet points, and arbitrarily nested subsections.
    
    This class supports both machine-readability (via JSON/YAML) and structured 
    rendering (via Markdown/XML), making it ideal for prompt templating, modular
    editing, and traceable documentation.
    """
    @staticmethod
    def from_json(json_data: Union[str, dict]) -> 'PromptObjectModel':
        """
        Create a PromptObjectModel instance from JSON data.
        
        Args:
            json_data: Either a JSON string or a parsed dictionary
            
        Returns:
            A new PromptObjectModel populated with the data from the JSON
            
        Raises:
            ValueError: If the JSON is not properly formatted
        """
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        return PromptObjectModel._from_dict(data)
    
    @staticmethod
    def from_yaml(yaml_data: Union[str, dict]) -> 'PromptObjectModel':
        """
        Create a PromptObjectModel instance from YAML data.
        
        Args:
            yaml_data: Either a YAML string or a parsed dictionary
            
        Returns:
            A new PromptObjectModel populated with the data from the YAML
            
        Raises:
            ValueError: If the YAML is not properly formatted
        """
        if isinstance(yaml_data, str):
            data = yaml.safe_load(yaml_data)
        else:
            data = yaml_data
        
        return PromptObjectModel._from_dict(data)
    
    @staticmethod
    def _from_dict(data: dict) -> 'PromptObjectModel':
        """
        Internal method to create a PromptObjectModel from a dictionary.
        Used by both from_json and from_yaml.
        
        Args:
            data: A dictionary containing the POM structure
            
        Returns:
            A new PromptObjectModel populated with the data
            
        Raises:
            ValueError: If the data is not properly formatted
        """
        def build_section(d: dict, is_subsection: bool = False) -> Section:
            if not isinstance(d, dict):
                raise ValueError("Each section must be a dictionary.")
            if 'title' in d and not isinstance(d['title'], str):
                raise ValueError("'title' must be a string if present.")
            if 'subsections' in d and not isinstance(d['subsections'], list):
                raise ValueError("'subsections' must be a list if provided.")
            if 'bullets' in d and not isinstance(d['bullets'], list):
                raise ValueError("'bullets' must be a list if provided.")
            if 'numbered' in d and not isinstance(d['numbered'], bool):
                raise ValueError("'numbered' must be a boolean if provided.")
            if 'numberedBullets' in d and not isinstance(d['numberedBullets'], bool):
                raise ValueError("'numberedBullets' must be a boolean if provided.")
                
            # Validate that all sections must have either a body, bullets, or subsections
            has_body = 'body' in d and d.get('body')
            has_bullets = 'bullets' in d and d.get('bullets')
            has_subsections = 'subsections' in d and d.get('subsections')
            if not has_body and not has_bullets and not has_subsections:
                raise ValueError("All sections must have either a non-empty body, non-empty bullets, or subsections")
                
            # Validate that all subsections must have a title
            if is_subsection and 'title' not in d:
                raise ValueError("All subsections must have a title")

            # Only pass numbered/numberedBullets if they're explicitly in the dict
            kwargs = {
                'title': d.get('title'),
                'body': d.get('body', ''),
                'bullets': d.get('bullets', [])
            }
            
            if 'numbered' in d:
                kwargs['numbered'] = d['numbered']
            if 'numberedBullets' in d:
                kwargs['numberedBullets'] = d['numberedBullets']
                
            section = Section(**kwargs)
            
            # Process subsections
            for i, sub in enumerate(d.get('subsections', [])):
                section.subsections.append(build_section(sub, is_subsection=True))
                
            return section

        pom = PromptObjectModel()
        
        # Validate that only the first section can have no title
        for i, sec in enumerate(data):
            if i > 0 and 'title' not in sec:
                sec['title'] = "Untitled Section"
            pom.sections.append(build_section(sec))
            
        return pom

    def __init__(self, debug: bool = False):
        self.sections: List[Section] = []
        self.debug = debug

    def add_section(self, title: Optional[str] = None, *, body: str = '', bullets: Optional[Union[List[str], str]] = None,
                   numbered: Optional[bool] = None, numberedBullets: bool = False) -> Section:
        """
        Add a top-level section to the model.
        
        Args:
            title: The title of the section
            body: Optional body text for the section
            bullets: Optional list of bullet points or a single string
            numbered: Whether this section should be numbered
            numberedBullets: Whether bullets should be numbered
            
        Returns:
            The newly created Section object
            
        Raises:
            ValueError: If a section without a title is added after the first section
        """
        # Validate that only the first section can have no title
        if title is None and len(self.sections) > 0:
            raise ValueError("Only the first section can have no title")
        
        # Convert bullets to a list if it's a string
        if isinstance(bullets, str):
            bullets_list = [bullets]
        else:
            bullets_list = bullets or []
        
        # Create the section (validation will happen when content is added)
        section = Section(title, body=body, bullets=bullets_list, 
                         numbered=numbered, numberedBullets=numberedBullets)
        self.sections.append(section)
        return section

    def find_section(self, title: str) -> Optional[Section]:
        """
        Find a section by its title.
        
        Performs a recursive search through all sections and subsections.
        
        Args:
            title: The title to search for
            
        Returns:
            The Section object if found, None otherwise
        """
        def recurse(sections: List[Section]) -> Optional[Section]:
            for section in sections:
                if section.title == title:
                    return section
                found = recurse(section.subsections)
                if found:
                    return found
            return None
        return recurse(self.sections)

    def to_json(self) -> str:
        """
        Convert the entire model to a JSON string.
        
        Returns:
            A JSON string representation of the model
        """
        return json.dumps([s.to_dict() for s in self.sections], indent=2)
    
    def to_yaml(self) -> str:
        """
        Convert the entire model to a YAML string.
        
        Returns:
            A YAML string representation of the model
        """
        return yaml.dump([s.to_dict() for s in self.sections], 
                         default_flow_style=False, 
                         sort_keys=False)
    
    def to_dict(self) -> List[dict]:
        """
        Convert the entire model to a list of dictionaries.
        
        Returns:
            A list of dictionaries representing the model
        """
        return [s.to_dict() for s in self.sections]

    def render_markdown(self) -> str:
        """
        Render the entire model as markdown.
        
        Returns:
            A string containing the markdown representation
        """
        # Check if any top-level section has numbered=True
        any_section_numbered = any(section.numbered for section in self.sections)
        
        # Debug output if enabled
        if self.debug:
            print(f"Any section numbered: {any_section_numbered}")
            for i, section in enumerate(self.sections):
                print(f"Section {i+1}: {section.title}, numbered={section.numbered}")
        
        md = []
        section_counter = 0
        for i, section in enumerate(self.sections):
            # Only increment the section counter for sections with titles
            if section.title is not None:
                section_counter += 1
                # If any section is numbered, number ALL siblings unless explicitly false
                if any_section_numbered and section.numbered != False:
                    section_number = [section_counter]
                else:
                    section_number = []
            else:
                # For sections without titles, don't use numbering at this level
                section_number = []
            
            # Debug output if enabled
            if self.debug:
                print(f"Rendering section {i}: {section.title} with section_number={section_number}")
            
            section_md = section.render_markdown(section_number=section_number)
            md.append(section_md)
        
        return "\n".join(md)

    def render_xml(self) -> str:
        """
        Render the entire model as XML.
        
        Returns:
            A string containing the XML representation
        """
        xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<prompt>']
        
        # Check if any top-level section has numbered=True
        any_section_numbered = any(section.numbered for section in self.sections)
        
        section_counter = 0
        for i, section in enumerate(self.sections, 1):
            # Only increment the section counter for sections with titles
            if section.title is not None:
                section_counter += 1
                # If any section is numbered, number all siblings unless explicitly false
                if any_section_numbered and section.numbered is not False:
                    section_number = [section_counter]
                else:
                    section_number = []
            else:
                # For sections without titles, don't use numbering at this level
                section_number = []
                
            xml.append(section.render_xml(indent=1, section_number=section_number))
        
        xml.append('</prompt>')
        return "\n".join(xml)

    def add_pom_as_subsection(self, target: Union[str, Section], pom_to_add: 'PromptObjectModel'):
        """
        Add another PromptObjectModel as a subsection to a section with the given title or section object.
        
        Args:
            target: The title of the section or the Section object to which the POM should be added as a subsection.
            pom_to_add: The PromptObjectModel to add as a subsection.
        
        Raises:
            ValueError: If no section with the target title is found (when target is a string).
        """
        if isinstance(target, str):
            target_section = self.find_section(target)
            if not target_section:
                raise ValueError(f"No section with title '{target}' found.")
        elif isinstance(target, Section):
            target_section = target
        else:
            raise TypeError("Target must be a string or a Section object.")
        
        for section in pom_to_add.sections:
            target_section.subsections.append(section) 