"""
msds_validator.py

MSDS document validation module to check if all 16 required sections are present.
"""

import re
from typing import Dict
from langchain_community.document_loaders import PyPDFLoader

class MSDSValidator:
    """Validates MSDS documents for completeness and structure."""
    
    # Standard 16 MSDS sections
    REQUIRED_SECTIONS = {
        1: "Identification",
        2: "Hazard(s) Identification", 
        3: "Composition/Information on Ingredients",
        4: "First-Aid Measures",
        5: "Fire-Fighting Measures", 
        6: "Accidental Release Measures",
        7: "Handling and Storage",
        8: "Exposure Controls/Personal Protection",
        9: "Physical and Chemical Properties",
        10: "Stability and Reactivity",
        11: "Toxicological Information",
        12: "Ecological Information", 
        13: "Disposal Considerations",
        14: "Transport Information",
        15: "Regulatory Information",
        16: "Other Information"
    }
    
    # Alternative section names and patterns
    SECTION_PATTERNS = {
        1: [
            r"section\s*1[:\.\-\s]*identification",
            r"product\s*identification",
            r"identification\s*of\s*the\s*substance",
            r"1\.\s*identification"
        ],
        2: [
            r"section\s*2[:\.\-\s]*hazard",
            r"hazard.*identification",
            r"classification.*hazard",
            r"2\.\s*hazard"
        ],
        3: [
            r"section\s*3[:\.\-\s]*composition",
            r"composition.*ingredients",
            r"information.*ingredients",
            r"3\.\s*composition"
        ],
        4: [
            r"section\s*4[:\.\-\s]*first.*aid",
            r"first.*aid.*measures",
            r"emergency.*first.*aid",
            r"4\.\s*first.*aid"
        ],
        5: [
            r"section\s*5[:\.\-\s]*fire",
            r"fire.*fighting.*measures",
            r"firefighting.*measures",
            r"5\.\s*fire"
        ],
        6: [
            r"section\s*6[:\.\-\s]*accidental",
            r"accidental.*release.*measures",
            r"spill.*cleanup",
            r"6\.\s*accidental"
        ],
        7: [
            r"section\s*7[:\.\-\s]*handling",
            r"handling.*storage",
            r"safe.*handling",
            r"7\.\s*handling"
        ],
        8: [
            r"section\s*8[:\.\-\s]*exposure",
            r"exposure.*controls",
            r"personal.*protection",
            r"8\.\s*exposure"
        ],
        9: [
            r"section\s*9[:\.\-\s]*physical",
            r"physical.*chemical.*properties",
            r"physicochemical.*properties",
            r"9\.\s*physical"
        ],
        10: [
            r"section\s*10[:\.\-\s]*stability",
            r"stability.*reactivity",
            r"chemical.*stability",
            r"10\.\s*stability"
        ],
        11: [
            r"section\s*11[:\.\-\s]*toxicological",
            r"toxicological.*information",
            r"health.*effects",
            r"11\.\s*toxicological"
        ],
        12: [
            r"section\s*12[:\.\-\s]*ecological",
            r"ecological.*information",
            r"environmental.*effects",
            r"12\.\s*ecological"
        ],
        13: [
            r"section\s*13[:\.\-\s]*disposal",
            r"disposal.*considerations",
            r"waste.*disposal",
            r"13\.\s*disposal"
        ],
        14: [
            r"section\s*14[:\.\-\s]*transport",
            r"transport.*information",
            r"shipping.*information",
            r"14\.\s*transport"
        ],
        15: [
            r"section\s*15[:\.\-\s]*regulatory",
            r"regulatory.*information",
            r"legal.*information",
            r"15\.\s*regulatory"
        ],
        16: [
            r"section\s*16[:\.\-\s]*other",
            r"other.*information",
            r"additional.*information",
            r"16\.\s*other"
        ]
    }
    
    def __init__(self):
        """Initialize the MSDS validator."""
        pass
    
    def validate_pdf(self, pdf_path: str) -> Dict:
        """
        Validate a PDF file for MSDS compliance.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            Dict: Validation results
        """
        try:
            # Load PDF content
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            
            # Combine all pages into single text
            full_text = ""
            for doc in docs:
                full_text += " " + doc.page_content
            
            # Validate sections
            validation_result = self._validate_sections(full_text)
            
            # Add document metadata
            validation_result.update({
                "document_pages": len(docs),
                "document_length": len(full_text),
                "is_pdf": True
            })
            
            return validation_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process PDF: {str(e)}",
                "is_valid_msds": False,
                "missing_sections": list(self.REQUIRED_SECTIONS.keys()),
                "found_sections": [],
                "validation_details": {}
            }
    
    def _validate_sections(self, text: str) -> Dict:
        """
        Validate if all required MSDS sections are present in the text.
        
        Args:
            text (str): Full document text
            
        Returns:
            Dict: Validation results
        """
        text_lower = text.lower()
        found_sections = {}
        validation_details = {}
        
        # Check each required section
        for section_num, section_name in self.REQUIRED_SECTIONS.items():
            patterns = self.SECTION_PATTERNS.get(section_num, [])
            section_found = False
            matched_pattern = None
            
            # Try each pattern for this section
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE):
                    section_found = True
                    matched_pattern = pattern
                    break
            
            if section_found:
                found_sections[section_num] = section_name
                validation_details[section_num] = {
                    "found": True,
                    "pattern_matched": matched_pattern,
                    "section_name": section_name
                }
            else:
                validation_details[section_num] = {
                    "found": False,
                    "section_name": section_name,
                    "patterns_tried": patterns
                }
        
        # Determine missing sections
        missing_sections = []
        for section_num in self.REQUIRED_SECTIONS.keys():
            if section_num not in found_sections:
                missing_sections.append({
                    "section_number": section_num,
                    "section_name": self.REQUIRED_SECTIONS[section_num]
                })
        
        # Calculate validation score
        found_count = len(found_sections)
        total_count = len(self.REQUIRED_SECTIONS)
        validation_score = (found_count / total_count) * 100
        
        # Determine if document is valid MSDS
        is_valid_msds = len(missing_sections) == 0
        
        return {
            "success": True,
            "is_valid_msds": is_valid_msds,
            "validation_score": validation_score,
            "found_sections": [
                {
                    "section_number": num,
                    "section_name": name
                }
                for num, name in found_sections.items()
            ],
            "missing_sections": missing_sections,
            "sections_found_count": found_count,
            "total_sections_required": total_count,
            "validation_details": validation_details
        }
    
    def get_section_requirements(self) -> Dict:
        """
        Get the list of required MSDS sections.
        
        Returns:
            Dict: Required sections information
        """
        return {
            "required_sections": [
                {
                    "section_number": num,
                    "section_name": name
                }
                for num, name in self.REQUIRED_SECTIONS.items()
            ],
            "total_sections": len(self.REQUIRED_SECTIONS)
        }
    
    def validate_text(self, text: str) -> Dict:
        """
        Validate text content for MSDS compliance.
        
        Args:
            text (str): Document text content
            
        Returns:
            Dict: Validation results
        """
        return self._validate_sections(text)


def validate_msds_file(file_path: str) -> Dict:
    """
    Convenience function to validate an MSDS file.
    
    Args:
        file_path (str): Path to the MSDS file
        
    Returns:
        Dict: Validation results
    """
    validator = MSDSValidator()
    return validator.validate_pdf(file_path)


# Example usage and testing
if __name__ == "__main__":
    # Test the validator
    validator = MSDSValidator()
    
    # Print required sections
    requirements = validator.get_section_requirements()
    print("Required MSDS Sections:")
    for section in requirements["required_sections"]:
        print(f"  {section['section_number']}. {section['section_name']}")
    
    # Test with sample text
    sample_text = """
    Section 1: Identification
    Product Name: Test Chemical
    
    Section 2: Hazard Identification
    Classification: Flammable liquid
    
    Section 3: Composition/Information on Ingredients
    Chemical Name: Test compound
    """
    
    result = validator.validate_text(sample_text)
    print(f"\nValidation Result: {result['validation_score']:.1f}% complete")
    print(f"Valid MSDS: {result['is_valid_msds']}")
    print(f"Sections found: {result['sections_found_count']}/{result['total_sections_required']}")
