"""Skill extractor module for taxonomy-based and fuzzy skill extraction with source tracking."""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Set
from rapidfuzz import fuzz
from config import SKILLS_FILE, FUZZY_SKILL_THRESHOLD


class SkillExtractor:
    def __init__(self, skills_path: Path = SKILLS_FILE):
        self.skills_path = skills_path
        self.taxonomy: Dict[str, Dict[str, Any]] = {}
        self.load_taxonomy()

    def load_taxonomy(self) -> None:
        """Load skill taxonomy from JSON file."""
        if self.skills_path.exists():
            with open(self.skills_path, "r", encoding="utf-8") as f:
                self.taxonomy = json.load(f)
        else:
            self.taxonomy = {}

    def extract_skills(self, full_text: str, sections: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Extract canonical skills from text with source tracking (Sections, Projects, Experience)."""
        extracted: Dict[str, Dict[str, Any]] = {}
        text_lower = full_text.lower()

        for canonical_name, data in self.taxonomy.items():
            category = data.get("category", "General")
            aliases = [canonical_name.lower()] + [a.lower() for a in data.get("aliases", [])]

            found_sources: Set[str] = set()
            total_count = 0

            for alias in aliases:
                # Use word-boundary regex for exact token matching
                # Special escape for symbols like c++, c#, .net
                pattern = r"(?<![a-zA-Z0-9])" + re.escape(alias) + r"(?![a-zA-Z0-9])"
                matches = list(re.finditer(pattern, text_lower))

                if matches:
                    total_count += len(matches)
                    # Check which sections contain the alias
                    for section_name, section_text in sections.items():
                        if re.search(pattern, section_text.lower()):
                            found_sources.add(section_name)

            # If not matched by exact word boundaries and alias length > 3, test fuzzy near-misses
            if total_count == 0:
                for alias in aliases:
                    if len(alias) >= 4 and " " in alias:
                        # For multi-word skills like "machine learning" or "rest api"
                        if fuzz.partial_ratio(alias, text_lower) >= FUZZY_SKILL_THRESHOLD:
                            total_count += 1
                            found_sources.add("Inferred")
                            break

            if total_count > 0:
                extracted[canonical_name] = {
                    "category": category,
                    "sources": sorted(list(found_sources)) if found_sources else ["General Text"],
                    "count": total_count,
                    "evidenced": bool(found_sources.intersection({"Projects", "Experience"}))
                }

        return extracted

