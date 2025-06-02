"""
AkashicRecords-specific MCP Server Integration

Custom MCP tools that understand AkashicRecords directory rules and structure.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json


class AkashicMCPTools:
    """
    AkashicRecords-specific MCP tools that understand directory rules and structure.
    
    These tools provide higher-level operations that respect README.md/Rule.md files
    and maintain AkashicRecords knowledge base integrity.
    """
    
    def __init__(self, project_root: str):
        """
        Initialize AkashicRecords MCP tools.
        
        Args:
            project_root: Root directory of the AkashicRecords project
        """
        self.project_root = Path(project_root)
        self._directory_rules_cache = {}
    
    async def read_directory_rules(self, directory_path: str) -> Dict[str, Any]:
        """
        Read and parse directory rules from README.md or Rule.md files.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            Dict[str, Any]: Parsed directory rules and metadata
        """
        dir_path = Path(directory_path)
        
        # Check cache first
        cache_key = str(dir_path.resolve())
        if cache_key in self._directory_rules_cache:
            return self._directory_rules_cache[cache_key]
        
        rules = {
            "path": str(dir_path),
            "has_readme": False,
            "has_rules": False,
            "purpose": "",
            "rules": [],
            "file_types": [],
            "inheritance": True
        }
        
        # Check for README.md
        readme_path = dir_path / "README.md"
        if readme_path.exists():
            rules["has_readme"] = True
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    rules["purpose"] = self._extract_purpose(content)
                    rules["rules"].extend(self._extract_rules(content))
            except Exception as e:
                print(f"Warning: Could not read README.md in {dir_path}: {e}")
        
        # Check for Rule.md
        rule_path = dir_path / "Rule.md"
        if rule_path.exists():
            rules["has_rules"] = True
            try:
                with open(rule_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    rules["rules"].extend(self._extract_rules(content))
            except Exception as e:
                print(f"Warning: Could not read Rule.md in {dir_path}: {e}")
        
        # Cache the result
        self._directory_rules_cache[cache_key] = rules
        return rules
    
    async def validate_file_placement(self, file_path: str, content_type: str) -> Dict[str, Any]:
        """
        Validate if a file placement follows directory rules.
        
        Args:
            file_path: Proposed file path
            content_type: Type of content (e.g., 'meeting_minutes', 'design_doc')
            
        Returns:
            Dict[str, Any]: Validation result with suggestions
        """
        file_path = Path(file_path)
        directory = file_path.parent
        
        # Get directory rules
        rules = await self.read_directory_rules(str(directory))
        
        validation = {
            "valid": True,
            "confidence": 1.0,
            "issues": [],
            "suggestions": [],
            "alternative_locations": []
        }
        
        # Check if directory has explicit rules about file types
        if rules["file_types"] and content_type not in rules["file_types"]:
            validation["valid"] = False
            validation["confidence"] = 0.3
            validation["issues"].append(
                f"Content type '{content_type}' not typically allowed in {directory}"
            )
        
        # Check naming conventions (basic implementation)
        if content_type == "meeting_minutes":
            if not self._follows_meeting_naming_convention(file_path.name):
                validation["issues"].append(
                    "Meeting minutes should follow YYYY-MM-DD_ProjectName_MeetingType.md format"
                )
                validation["confidence"] *= 0.8
        
        # Suggest alternative locations if current is not ideal
        if validation["confidence"] < 0.7:
            alternatives = await self._suggest_alternative_locations(content_type)
            validation["alternative_locations"] = alternatives
        
        return validation
    
    async def update_readme_after_file_operation(
        self, 
        directory_path: str, 
        operation: str, 
        file_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update README.md file after a file operation.
        
        Args:
            directory_path: Path to the directory
            operation: Type of operation ('create', 'delete', 'move')
            file_info: Information about the file affected
            
        Returns:
            Dict[str, Any]: Update result
        """
        dir_path = Path(directory_path)
        readme_path = dir_path / "README.md"
        
        result = {
            "updated": False,
            "created_readme": False,
            "changes": []
        }
        
        # Create README.md if it doesn't exist and we're adding a file
        if not readme_path.exists() and operation == "create":
            await self._create_default_readme(dir_path, file_info)
            result["created_readme"] = True
            result["updated"] = True
            result["changes"].append("Created new README.md")
            return result
        
        if not readme_path.exists():
            return result
        
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update content based on operation
            if operation == "create":
                content = self._add_file_to_readme(content, file_info)
                result["changes"].append(f"Added {file_info['name']} to file list")
            elif operation == "delete":
                content = self._remove_file_from_readme(content, file_info)
                result["changes"].append(f"Removed {file_info['name']} from file list")
            elif operation == "move":
                content = self._update_file_in_readme(content, file_info)
                result["changes"].append(f"Updated {file_info['name']} information")
            
            # Write back the updated content
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result["updated"] = True
            
            # Clear cache for this directory
            cache_key = str(dir_path.resolve())
            if cache_key in self._directory_rules_cache:
                del self._directory_rules_cache[cache_key]
                
        except Exception as e:
            print(f"Warning: Could not update README.md in {dir_path}: {e}")
        
        return result
    
    def _extract_purpose(self, content: str) -> str:
        """Extract directory purpose from README content."""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('# '):
                # Next few lines might contain purpose
                purpose_lines = []
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        purpose_lines.append(lines[j].strip())
                    elif lines[j].startswith('#'):
                        break
                return ' '.join(purpose_lines)[:200]
        return ""
    
    def _extract_rules(self, content: str) -> List[str]:
        """Extract rules from README or Rule content."""
        rules = []
        lines = content.split('\n')
        in_rules_section = False
        
        for line in lines:
            line = line.strip()
            if 'rule' in line.lower() or 'guideline' in line.lower():
                in_rules_section = True
            elif line.startswith('#') and in_rules_section:
                in_rules_section = False
            elif in_rules_section and (line.startswith('-') or line.startswith('*')):
                rules.append(line[1:].strip())
        
        return rules
    
    def _follows_meeting_naming_convention(self, filename: str) -> bool:
        """Check if filename follows meeting minutes naming convention."""
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}_.*\.md$'
        return bool(re.match(pattern, filename))
    
    async def _suggest_alternative_locations(self, content_type: str) -> List[str]:
        """Suggest alternative locations for a content type."""
        # Simple implementation - could be enhanced with ML
        type_mapping = {
            "meeting_minutes": ["Meetings", "會議記錄", "討論紀錄"],
            "design_doc": ["Design", "Documentation", "Architecture"],
            "requirements": ["Requirements", "Specs", "Specifications"],
            "test_case": ["Testing", "Tests", "QA"]
        }
        
        suggestions = type_mapping.get(content_type, [])
        
        # Find existing directories that match
        existing_suggestions = []
        for suggestion in suggestions:
            potential_path = self.project_root / suggestion
            if potential_path.exists() and potential_path.is_dir():
                existing_suggestions.append(str(potential_path))
        
        return existing_suggestions
    
    async def _create_default_readme(self, directory: Path, file_info: Dict[str, Any]) -> None:
        """Create a default README.md for a directory."""
        content = f"""# {directory.name}

## Purpose
This directory contains {file_info.get('type', 'files')} for the project.

## Contents
- `{file_info['name']}`: {file_info.get('description', 'Added file')}

## Rules
- Follow project naming conventions
- Update this README when adding new files
- Maintain consistent organization

---
*This README was automatically generated by AkashicRecords*
"""
        readme_path = directory / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _add_file_to_readme(self, content: str, file_info: Dict[str, Any]) -> str:
        """Add file information to README content."""
        # Simple implementation - look for ## Contents section
        lines = content.split('\n')
        contents_index = -1
        
        for i, line in enumerate(lines):
            if line.strip().lower().startswith('## contents'):
                contents_index = i
                break
        
        if contents_index >= 0:
            # Insert after the Contents header
            new_line = f"- `{file_info['name']}`: {file_info.get('description', 'Added file')}"
            lines.insert(contents_index + 1, new_line)
        else:
            # Add Contents section if it doesn't exist
            lines.append("\n## Contents")
            lines.append(f"- `{file_info['name']}`: {file_info.get('description', 'Added file')}")
        
        return '\n'.join(lines)
    
    def _remove_file_from_readme(self, content: str, file_info: Dict[str, Any]) -> str:
        """Remove file information from README content."""
        lines = content.split('\n')
        filename = file_info['name']
        
        # Remove lines that reference this file
        filtered_lines = []
        for line in lines:
            if f"`{filename}`" not in line:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _update_file_in_readme(self, content: str, file_info: Dict[str, Any]) -> str:
        """Update file information in README content."""
        # For moves, remove old and add new
        self._remove_file_from_readme(content, file_info)
        return self._add_file_to_readme(content, file_info)