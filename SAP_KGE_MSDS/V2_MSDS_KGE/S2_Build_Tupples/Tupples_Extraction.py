"""
Module 2: Tupple_Extraction - MSDS Data to RDF Converter
=======================================================

EXECUTION INSTRUCTIONS:
----------------------
1. Install required dependencies:
   pip install pandas rdflib openpyxl PyPDF2 pdfplumber regex

2. Execute the module:
   python Tupples_Extraction.py

3. Or import and use programmatically:
   processor = DataProcessor()
   processor.convert_data_to_rdf('path/to/data.pdf', 'pdf')
   processor.save_rdf_files()

INPUT REQUIREMENTS:
------------------
- PDF file (33.KGE-PDF/SAP_KGE_MSDS/V2_MSDS_KGE/S1_Design_Ontology/wd-40.pdf)
- Default input file: 33.KGE-PDF/SAP_KGE_MSDS/V2_MSDS_KGE/S1_Design_Ontology/wd-40.pdf

OUTPUT LOCATION:
---------------
- RDF files will be saved in the current working directory with the prefix 'rdf_output_'.
- The files will be named based on the input file name, e.g., 'rdf_output_wd-40.ttl'.
- The RDF files will be in Turtle format.
- The RDF files will contain triples extracted from the input data.

TRIPLE GENERATION:
-----------------
- The triples will be generated based on the data extracted from the input file.
- The triples will be stored in RDF format using the rdflib library.
- Uses the SAP KGE MSDS Ontology for structured data representation.

"""

import os
import re
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import uuid

# Third-party imports
import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, DCTERMS

try:
    import PyPDF2
    import pdfplumber
except ImportError:
    print("Warning: PDF processing libraries not found. Install with: pip install PyPDF2 pdfplumber")
    PyPDF2 = None
    pdfplumber = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('msds_extraction.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MSDataProcessor:
    """
    Main processor class for converting MSDS PDF documents to RDF triples in TTL format.
    Uses the SAP KGE MSDS Ontology for structured representation.
    """
    
    def __init__(self):
        """Initialize the data processor with ontology namespaces and graph."""
        self.graph = Graph()
        self.setup_namespaces()
        self.setup_ontology_prefixes()
        self.extracted_data = {}
        self.current_document_uri = None
        
    def setup_namespaces(self):
        """Set up RDF namespaces for the MSDS ontology."""
        # Define namespaces
        self.MSDS = Namespace("http://sap.com/kge/msds#")
        self.BASE = Namespace("http://sap.com/kge/msds#MSDS_Ontology")
        
        # Bind namespaces to graph
        self.graph.bind("msds", self.MSDS)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
        self.graph.bind("dcterms", DCTERMS)
        
    def setup_ontology_prefixes(self):
        """Set up ontology class and property mappings."""
        # MSDS Section Classes
        self.section_classes = {
            'identification': self.MSDS.Identification,
            'hazards_identification': self.MSDS.Hazards_Identification,
            'composition': self.MSDS.Composition_Information_on_Ingredients,
            'first_aid': self.MSDS.First_Aid_Measures,
            'fire_fighting': self.MSDS.Fire_Fighting_Measures,
            'accidental_release': self.MSDS.Accidental_Release_Measures,
            'handling_storage': self.MSDS.Handling_and_Storage,
            'exposure_controls': self.MSDS.Exposure_Controls_Personal_Protection,
            'physical_chemical': self.MSDS.Physical_and_Chemical_Properties,
            'stability_reactivity': self.MSDS.Stability_and_Reactivity,
            'toxicological': self.MSDS.Toxicological_Information,
            'ecological': self.MSDS.Ecological_Information,
            'disposal': self.MSDS.Disposal_Considerations,
            'transportation': self.MSDS.Transportation_Information,
            'regulatory': self.MSDS.Regulatory_Information,
            'other': self.MSDS.Other_Information
        }
        
        # Property mappings for data extraction
        self.property_mappings = {
            'product_name': self.MSDS.productName,
            'product_code': self.MSDS.productCode,
            'product_type': self.MSDS.productType,
            'recommended_use': self.MSDS.recommendedUse,
            'restricted_use': self.MSDS.restrictedUse,
            'company_name': self.MSDS.companyName,
            'address': self.MSDS.address,
            'phone_number': self.MSDS.phoneNumber,
            'emergency_phone': self.MSDS.emergencyPhone,
            'website': self.MSDS.website,
            'cas_number': self.MSDS.casNumber,
            'ec_number': self.MSDS.ecNumber,
            'ingredient_name': self.MSDS.ingredientName,
            'weight_percent': self.MSDS.weightPercent,
            'concentration_range': self.MSDS.concentrationRange,
            'hazard_statement': self.MSDS.hazardStatement,
            'precautionary_statement': self.MSDS.precautionaryStatement,
            'signal_word': self.MSDS.signalWord,
            'hazard_code': self.MSDS.hazardCode,
            'physical_state': self.MSDS.physicalState,
            'color': self.MSDS.color,
            'odor': self.MSDS.odor,
            'ph': self.MSDS.pH,
            'boiling_point': self.MSDS.boilingPoint,
            'melting_point': self.MSDS.meltingPoint,
            'flash_point': self.MSDS.flashPoint,
            'density': self.MSDS.density,
            'solubility': self.MSDS.solubility,
            'vapor_pressure': self.MSDS.vaporPressure
        }
        
    def extract_pdf_content(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract content from PDF file using multiple extraction methods.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            Dict[str, Any]: Extracted content organized by sections
        """
        if not PyPDF2 or not pdfplumber:
            raise ImportError("PDF processing libraries not available. Install with: pip install PyPDF2 pdfplumber")
            
        logger.info(f"Extracting content from PDF: {pdf_path}")
        
        extracted_content = {
            'raw_text': '',
            'sections': {},
            'metadata': {}
        }
        
        try:
            # Method 1: Extract using pdfplumber (better for structured text)
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        full_text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                
                extracted_content['raw_text'] = full_text
                
            # Method 2: Extract metadata using PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                if pdf_reader.metadata:
                    extracted_content['metadata'] = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                        'modification_date': pdf_reader.metadata.get('/ModDate', '')
                    }
                    
            # Parse sections from extracted text
            extracted_content['sections'] = self.parse_msds_sections(full_text)
            
            logger.info(f"Successfully extracted content from {len(pdf.pages)} pages")
            return extracted_content
            
        except Exception as e:
            logger.error(f"Error extracting PDF content: {str(e)}")
            raise
            
    def parse_msds_sections(self, text: str) -> Dict[str, str]:
        """
        Parse MSDS sections from extracted text using pattern matching.
        
        Args:
            text (str): Raw text extracted from PDF
            
        Returns:
            Dict[str, str]: Parsed sections with content
        """
        sections = {}
        
        # Common MSDS section patterns
        section_patterns = {
            'identification': r'(?i)section\s*1[:\-\s]*(?:product\s*and\s*company\s*)?identification(.*?)(?=section\s*2|$)',
            'hazards_identification': r'(?i)section\s*2[:\-\s]*hazards?\s*identification(.*?)(?=section\s*3|$)',
            'composition': r'(?i)section\s*3[:\-\s]*composition.*?ingredients?(.*?)(?=section\s*4|$)',
            'first_aid': r'(?i)section\s*4[:\-\s]*first\s*aid\s*measures?(.*?)(?=section\s*5|$)',
            'fire_fighting': r'(?i)section\s*5[:\-\s]*fire.*?fighting\s*measures?(.*?)(?=section\s*6|$)',
            'accidental_release': r'(?i)section\s*6[:\-\s]*accidental\s*release\s*measures?(.*?)(?=section\s*7|$)',
            'handling_storage': r'(?i)section\s*7[:\-\s]*handling\s*and\s*storage(.*?)(?=section\s*8|$)',
            'exposure_controls': r'(?i)section\s*8[:\-\s]*exposure\s*controls?.*?personal\s*protection(.*?)(?=section\s*9|$)',
            'physical_chemical': r'(?i)section\s*9[:\-\s]*physical\s*and\s*chemical\s*properties(.*?)(?=section\s*10|$)',
            'stability_reactivity': r'(?i)section\s*10[:\-\s]*stability\s*and\s*reactivity(.*?)(?=section\s*11|$)',
            'toxicological': r'(?i)section\s*11[:\-\s]*toxicological\s*information(.*?)(?=section\s*12|$)',
            'ecological': r'(?i)section\s*12[:\-\s]*ecological\s*information(.*?)(?=section\s*13|$)',
            'disposal': r'(?i)section\s*13[:\-\s]*disposal\s*considerations?(.*?)(?=section\s*14|$)',
            'transportation': r'(?i)section\s*14[:\-\s]*transport.*?information(.*?)(?=section\s*15|$)',
            'regulatory': r'(?i)section\s*15[:\-\s]*regulatory\s*information(.*?)(?=section\s*16|$)',
            'other': r'(?i)section\s*16[:\-\s]*other\s*information(.*?)$'
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section_name] = match.group(1).strip()
                logger.debug(f"Found section: {section_name}")
                
        return sections
        
    def extract_structured_data(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract structured data from parsed sections.
        
        Args:
            sections (Dict[str, str]): Parsed MSDS sections
            
        Returns:
            Dict[str, Any]: Structured data for RDF conversion
        """
        structured_data = {
            'document': {},
            'product': {},
            'company': {},
            'ingredients': [],
            'hazards': [],
            'physical_properties': {},
            'sections_data': {}
        }
        
        # Extract product identification
        if 'identification' in sections:
            identification_text = sections['identification']
            structured_data['product'] = self.extract_product_info(identification_text)
            structured_data['company'] = self.extract_company_info(identification_text)
            
        # Extract composition information
        if 'composition' in sections:
            structured_data['ingredients'] = self.extract_ingredients(sections['composition'])
            
        # Extract hazard information
        if 'hazards_identification' in sections:
            structured_data['hazards'] = self.extract_hazards(sections['hazards_identification'])
            
        # Extract physical and chemical properties
        if 'physical_chemical' in sections:
            structured_data['physical_properties'] = self.extract_physical_properties(sections['physical_chemical'])
            
        # Store section data for additional processing
        structured_data['sections_data'] = sections
        
        return structured_data
        
    def extract_product_info(self, text: str) -> Dict[str, str]:
        """Extract product information from identification section."""
        product_info = {}
        
        # Product name patterns
        name_patterns = [
            r'(?i)product\s*name[:\-\s]*([^\n\r]+)',
            r'(?i)trade\s*name[:\-\s]*([^\n\r]+)',
            r'(?i)commercial\s*name[:\-\s]*([^\n\r]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                product_info['name'] = match.group(1).strip()
                break
                
        # Product code patterns
        code_patterns = [
            r'(?i)product\s*code[:\-\s]*([^\n\r]+)',
            r'(?i)item\s*number[:\-\s]*([^\n\r]+)',
            r'(?i)part\s*number[:\-\s]*([^\n\r]+)'
        ]
        
        for pattern in code_patterns:
            match = re.search(pattern, text)
            if match:
                product_info['code'] = match.group(1).strip()
                break
                
        # Recommended use
        use_pattern = r'(?i)recommended\s*use[:\-\s]*([^\n\r]+)'
        match = re.search(use_pattern, text)
        if match:
            product_info['recommended_use'] = match.group(1).strip()
            
        return product_info
        
    def extract_company_info(self, text: str) -> Dict[str, str]:
        """Extract company information from identification section."""
        company_info = {}
        
        # Company name patterns
        name_patterns = [
            r'(?i)company[:\-\s]*([^\n\r]+)',
            r'(?i)manufacturer[:\-\s]*([^\n\r]+)',
            r'(?i)supplier[:\-\s]*([^\n\r]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                company_info['name'] = match.group(1).strip()
                break
                
        # Address pattern
        address_pattern = r'(?i)address[:\-\s]*([^\n\r]+(?:\n[^\n\r]+)*?)(?=\n\s*(?:phone|tel|emergency|$))'
        match = re.search(address_pattern, text, re.MULTILINE)
        if match:
            company_info['address'] = match.group(1).strip()
            
        # Phone patterns
        phone_patterns = [
            r'(?i)phone[:\-\s]*([^\n\r]+)',
            r'(?i)tel[:\-\s]*([^\n\r]+)',
            r'(?i)telephone[:\-\s]*([^\n\r]+)'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                company_info['phone'] = match.group(1).strip()
                break
                
        # Emergency phone
        emergency_pattern = r'(?i)emergency[:\-\s]*(?:phone|tel|telephone)[:\-\s]*([^\n\r]+)'
        match = re.search(emergency_pattern, text)
        if match:
            company_info['emergency_phone'] = match.group(1).strip()
            
        return company_info
        
    def extract_ingredients(self, text: str) -> List[Dict[str, str]]:
        """Extract ingredient information from composition section."""
        ingredients = []
        
        # Look for ingredient tables or lists
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # CAS number pattern
            cas_match = re.search(r'(\d{1,7}-\d{2}-\d)', line)
            if cas_match:
                ingredient = {'cas_number': cas_match.group(1)}
                
                # Extract percentage
                percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%', line)
                if percent_match:
                    ingredient['weight_percent'] = float(percent_match.group(1))
                    
                # Extract name (usually before CAS number)
                name_part = line[:cas_match.start()].strip()
                if name_part:
                    ingredient['name'] = name_part
                    
                ingredients.append(ingredient)
                
        return ingredients
        
    def extract_hazards(self, text: str) -> List[Dict[str, str]]:
        """Extract hazard information from hazards identification section."""
        hazards = []
        
        # Signal word patterns
        signal_match = re.search(r'(?i)signal\s*word[:\-\s]*(danger|warning)', text)
        signal_word = signal_match.group(1) if signal_match else None
        
        # Hazard statements (H-codes)
        h_codes = re.findall(r'H\d{3}[:\-\s]*([^\n\r]+)', text, re.IGNORECASE)
        for h_code_text in h_codes:
            h_code_match = re.search(r'H\d{3}', h_code_text)
            hazard = {
                'type': 'hazard_statement',
                'code': h_code_match.group() if h_code_match else '',
                'statement': h_code_text.strip(),
                'signal_word': signal_word
            }
            hazards.append(hazard)
            
        # Precautionary statements (P-codes)
        p_codes = re.findall(r'P\d{3}[:\-\s]*([^\n\r]+)', text, re.IGNORECASE)
        for p_code_text in p_codes:
            p_code_match = re.search(r'P\d{3}', p_code_text)
            hazard = {
                'type': 'precautionary_statement',
                'code': p_code_match.group() if p_code_match else '',
                'statement': p_code_text.strip()
            }
            hazards.append(hazard)
            
        return hazards
        
    def extract_physical_properties(self, text: str) -> Dict[str, Any]:
        """Extract physical and chemical properties."""
        properties = {}
        
        # Physical state
        state_match = re.search(r'(?i)physical\s*state[:\-\s]*([^\n\r]+)', text)
        if state_match:
            properties['physical_state'] = state_match.group(1).strip()
            
        # Color
        color_match = re.search(r'(?i)colou?r[:\-\s]*([^\n\r]+)', text)
        if color_match:
            properties['color'] = color_match.group(1).strip()
            
        # Odor
        odor_match = re.search(r'(?i)odou?r[:\-\s]*([^\n\r]+)', text)
        if odor_match:
            properties['odor'] = odor_match.group(1).strip()
            
        # pH
        ph_match = re.search(r'(?i)ph[:\-\s]*(\d+(?:\.\d+)?)', text)
        if ph_match:
            properties['ph'] = float(ph_match.group(1))
            
        # Boiling point
        bp_match = re.search(r'(?i)boiling\s*point[:\-\s]*(\d+(?:\.\d+)?)', text)
        if bp_match:
            properties['boiling_point'] = float(bp_match.group(1))
            
        # Flash point
        fp_match = re.search(r'(?i)flash\s*point[:\-\s]*(\d+(?:\.\d+)?)', text)
        if fp_match:
            properties['flash_point'] = float(fp_match.group(1))
            
        # Density
        density_match = re.search(r'(?i)density[:\-\s]*(\d+(?:\.\d+)?)', text)
        if density_match:
            properties['density'] = float(density_match.group(1))
            
        return properties
        
    def convert_to_rdf_triples(self, structured_data: Dict[str, Any], document_name: str) -> None:
        """
        Convert structured data to RDF triples using the MSDS ontology.
        
        Args:
            structured_data (Dict[str, Any]): Structured data extracted from MSDS
            document_name (str): Name of the source document
        """
        logger.info("Converting structured data to RDF triples")
        
        # Create document URI
        doc_id = str(uuid.uuid4())
        self.current_document_uri = self.MSDS[f"document_{doc_id}"]
        
        # Add document triples
        self.graph.add((self.current_document_uri, RDF.type, self.MSDS.MSDS_Document))
        self.graph.add((self.current_document_uri, self.MSDS.documentId, Literal(doc_id)))
        self.graph.add((self.current_document_uri, DCTERMS.created, Literal(datetime.now(), datatype=XSD.dateTime)))
        self.graph.add((self.current_document_uri, DCTERMS.title, Literal(f"MSDS Document - {document_name}")))
        
        # Add product information
        if structured_data['product']:
            self.add_product_triples(structured_data['product'])
            
        # Add company information
        if structured_data['company']:
            self.add_company_triples(structured_data['company'])
            
        # Add ingredients
        for ingredient in structured_data['ingredients']:
            self.add_ingredient_triples(ingredient)
            
        # Add hazards
        for hazard in structured_data['hazards']:
            self.add_hazard_triples(hazard)
            
        # Add physical properties
        if structured_data['physical_properties']:
            self.add_physical_properties_triples(structured_data['physical_properties'])
            
        # Add sections
        self.add_section_triples(structured_data['sections_data'])
        
        logger.info(f"Generated {len(self.graph)} RDF triples")
        
    def add_product_triples(self, product_data: Dict[str, str]) -> None:
        """Add product-related triples to the graph."""
        if not self.current_document_uri:
            return
            
        product_uri = self.MSDS[f"product_{uuid.uuid4()}"]
        
        self.graph.add((product_uri, RDF.type, self.MSDS.Product))
        self.graph.add((self.current_document_uri, self.MSDS.hasProduct, product_uri))
        
        if 'name' in product_data:
            self.graph.add((product_uri, self.MSDS.productName, Literal(product_data['name'])))
            
        if 'code' in product_data:
            self.graph.add((product_uri, self.MSDS.productCode, Literal(product_data['code'])))
            
        if 'recommended_use' in product_data:
            self.graph.add((product_uri, self.MSDS.recommendedUse, Literal(product_data['recommended_use'])))
            
    def add_company_triples(self, company_data: Dict[str, str]) -> None:
        """Add company-related triples to the graph."""
        if not self.current_document_uri:
            return
            
        company_uri = self.MSDS[f"company_{uuid.uuid4()}"]
        
        self.graph.add((company_uri, RDF.type, self.MSDS.Company))
        self.graph.add((self.current_document_uri, self.MSDS.hasCompany, company_uri))
        
        if 'name' in company_data:
            self.graph.add((company_uri, self.MSDS.companyName, Literal(company_data['name'])))
            
        if 'address' in company_data:
            self.graph.add((company_uri, self.MSDS.address, Literal(company_data['address'])))
            
        if 'phone' in company_data:
            self.graph.add((company_uri, self.MSDS.phoneNumber, Literal(company_data['phone'])))
            
        if 'emergency_phone' in company_data:
            self.graph.add((company_uri, self.MSDS.emergencyPhone, Literal(company_data['emergency_phone'])))
            
    def add_ingredient_triples(self, ingredient_data: Dict[str, Any]) -> None:
        """Add ingredient-related triples to the graph."""
        ingredient_uri = self.MSDS[f"ingredient_{uuid.uuid4()}"]
        
        self.graph.add((ingredient_uri, RDF.type, self.MSDS.Ingredient))
        
        # Create composition section if not exists
        composition_uri = self.MSDS[f"composition_{uuid.uuid4()}"]
        self.graph.add((composition_uri, RDF.type, self.MSDS.Composition_Information_on_Ingredients))
        self.graph.add((self.current_document_uri, self.MSDS.hasSection, composition_uri))
        self.graph.add((composition_uri, self.MSDS.hasIngredient, ingredient_uri))
        
        if 'name' in ingredient_data:
            self.graph.add((ingredient_uri, self.MSDS.ingredientName, Literal(ingredient_data['name'])))
            
        if 'cas_number' in ingredient_data:
            self.graph.add((ingredient_uri, self.MSDS.casNumber, Literal(ingredient_data['cas_number'])))
            
        if 'weight_percent' in ingredient_data:
            self.graph.add((ingredient_uri, self.MSDS.weightPercent, Literal(ingredient_data['weight_percent'], datatype=XSD.decimal)))
            
    def add_hazard_triples(self, hazard_data: Dict[str, str]) -> None:
        """Add hazard-related triples to the graph."""
        hazard_uri = self.MSDS[f"hazard_{uuid.uuid4()}"]
        
        self.graph.add((hazard_uri, RDF.type, self.MSDS.Hazard))
        
        # Create hazards identification section if not exists
        hazards_section_uri = self.MSDS[f"hazards_identification_{uuid.uuid4()}"]
        self.graph.add((hazards_section_uri, RDF.type, self.MSDS.Hazards_Identification))
        self.graph.add((self.current_document_uri, self.MSDS.hasSection, hazards_section_uri))
        self.graph.add((hazards_section_uri, self.MSDS.hasHazard, hazard_uri))
        
        if 'code' in hazard_data:
            self.graph.add((hazard_uri, self.MSDS.hazardCode, Literal(hazard_data['code'])))
            
        if 'statement' in hazard_data:
            if hazard_data['type'] == 'hazard_statement':
                self.graph.add((hazard_uri, self.MSDS.hazardStatement, Literal(hazard_data['statement'])))
            elif hazard_data['type'] == 'precautionary_statement':
                self.graph.add((hazard_uri, self.MSDS.precautionaryStatement, Literal(hazard_data['statement'])))
                
        if 'signal_word' in hazard_data and hazard_data['signal_word']:
            self.graph.add((hazard_uri, self.MSDS.signalWord, Literal(hazard_data['signal_word'])))
            
    def add_physical_properties_triples(self, properties_data: Dict[str, Any]) -> None:
        """Add physical and chemical properties triples to the graph."""
        properties_section_uri = self.MSDS[f"physical_chemical_{uuid.uuid4()}"]
        self.graph.add((properties_section_uri, RDF.type, self.MSDS.Physical_and_Chemical_Properties))
        self.graph.add((self.current_document_uri, self.MSDS.hasSection, properties_section_uri))
        
        property_uri = self.MSDS[f"property_{uuid.uuid4()}"]
        self.graph.add((property_uri, RDF.type, self.MSDS.PhysicalChemicalProperty))
        self.graph.add((properties_section_uri, self.MSDS.hasPhysicalChemicalProperty, property_uri))
        
        for prop_name, prop_value in properties_data.items():
            if prop_name in self.property_mappings:
                prop_predicate = self.property_mappings[prop_name]
                if isinstance(prop_value, (int, float)):
                    self.graph.add((property_uri, prop_predicate, Literal(prop_value, datatype=XSD.decimal)))
                else:
                    self.graph.add((property_uri, prop_predicate, Literal(str(prop_value))))
                    
    def add_section_triples(self, sections_data: Dict[str, str]) -> None:
        """Add section-related triples to the graph."""
        for section_name, section_content in sections_data.items():
            if section_name in self.section_classes:
                section_uri = self.MSDS[f"{section_name}_{uuid.uuid4()}"]
                section_class = self.section_classes[section_name]
                
                self.graph.add((section_uri, RDF.type, section_class))
                self.graph.add((self.current_document_uri, self.MSDS.hasSection, section_uri))
                self.graph.add((section_uri, self.MSDS.sectionText, Literal(section_content)))
                
    def convert_data_to_rdf(self, file_path: str, file_type: str = 'pdf') -> None:
        """
        Main method to convert data to RDF format.
        
        Args:
            file_path (str): Path to the input file
            file_type (str): Type of input file ('pdf', 'csv', 'excel')
        """
        logger.info(f"Starting conversion of {file_type} file: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")
            
        try:
            if file_type.lower() == 'pdf':
                # Extract content from PDF
                extracted_content = self.extract_pdf_content(file_path)
                
                # Extract structured data
                structured_data = self.extract_structured_data(extracted_content['sections'])
                
                # Convert to RDF triples
                document_name = Path(file_path).stem
                self.convert_to_rdf_triples(structured_data, document_name)
                
                # Store extracted data for reference
                self.extracted_data = {
                    'file_path': file_path,
                    'file_type': file_type,
                    'extracted_content': extracted_content,
                    'structured_data': structured_data,
                    'processing_timestamp': datetime.now().isoformat()
                }
                
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
            logger.info("Data conversion completed successfully")
            
        except Exception as e:
            logger.error(f"Error during data conversion: {str(e)}")
            raise
            
    def save_rdf_files(self, output_dir: str = None, format: str = 'turtle') -> List[str]:
        """
        Save RDF graph to files in specified format.
        
        Args:
            output_dir (str): Output directory (default: current directory)
            format (str): RDF serialization format ('turtle', 'xml', 'n3', 'nt')
            
        Returns:
            List[str]: List of created file paths
        """
        if not self.graph:
            raise ValueError("No RDF data to save. Run convert_data_to_rdf() first.")
            
        if output_dir is None:
            output_dir = os.getcwd()
            
        os.makedirs(output_dir, exist_ok=True)
        
        # Determine file extension based on format
        format_extensions = {
            'turtle': '.ttl',
            'xml': '.rdf',
            'n3': '.n3',
            'nt': '.nt'
        }
        
        extension = format_extensions.get(format.lower(), '.ttl')
        
        # Generate output filename
        if self.extracted_data and 'file_path' in self.extracted_data:
            base_name = Path(self.extracted_data['file_path']).stem
        else:
            base_name = 'msds_output'
            
        output_filename = f"rdf_output_{base_name}{extension}"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            # Serialize and save the graph
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self.graph.serialize(format=format))
                
            logger.info(f"RDF data saved to: {output_path}")
            logger.info(f"Total triples: {len(self.graph)}")
            
            return [output_path]
            
        except Exception as e:
            logger.error(f"Error saving RDF file: {str(e)}")
            raise
            
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the extracted data and RDF graph.
        
        Returns:
            Dict[str, Any]: Statistics dictionary
        """
        stats = {
            'total_triples': len(self.graph),
            'namespaces': dict(self.graph.namespaces()),
            'extraction_timestamp': self.extracted_data.get('processing_timestamp', 'N/A')
        }
        
        if self.extracted_data and 'structured_data' in self.extracted_data:
            structured_data = self.extracted_data['structured_data']
            stats.update({
                'products_found': 1 if structured_data.get('product') else 0,
                'companies_found': 1 if structured_data.get('company') else 0,
                'ingredients_found': len(structured_data.get('ingredients', [])),
                'hazards_found': len(structured_data.get('hazards', [])),
                'sections_found': len(structured_data.get('sections_data', {}))
            })
            
        return stats
        
    def query_rdf(self, sparql_query: str) -> List[Dict[str, Any]]:
        """
        Execute SPARQL query on the RDF graph.
        
        Args:
            sparql_query (str): SPARQL query string
            
        Returns:
            List[Dict[str, Any]]: Query results
        """
        if not self.graph:
            raise ValueError("No RDF data available. Run convert_data_to_rdf() first.")
            
        try:
            results = self.graph.query(sparql_query)
            return [dict(row.asdict()) for row in results]
        except Exception as e:
            logger.error(f"Error executing SPARQL query: {str(e)}")
            raise


# Compatibility class for backward compatibility
class DataProcessor(MSDataProcessor):
    """Backward compatibility class."""
    pass


def main():
    """
    Main execution function for command-line usage.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract tuples from MSDS PDF documents and convert to TTL format')
    parser.add_argument('input_file', nargs='?', 
                       default='../S1_Design_Ontology/wd-40.pdf',
                       help='Path to input PDF file')
    parser.add_argument('--output-dir', '-o', default=None,
                       help='Output directory for RDF files')
    parser.add_argument('--format', '-f', default='turtle',
                       choices=['turtle', 'xml', 'n3', 'nt'],
                       help='RDF serialization format')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    try:
        # Initialize processor
        processor = MSDataProcessor()
        
        # Convert data to RDF
        processor.convert_data_to_rdf(args.input_file, 'pdf')
        
        # Save RDF files
        output_files = processor.save_rdf_files(args.output_dir, args.format)
        
        # Print statistics
        stats = processor.get_statistics()
        print("\n=== Extraction Statistics ===")
        for key, value in stats.items():
            print(f"{key}: {value}")
            
        print(f"\nOutput files created:")
        for file_path in output_files:
            print(f"  - {file_path}")
            
        print("\n=== Sample SPARQL Queries ===")
        print("# Get all products:")
        print("SELECT ?product ?name WHERE { ?product a msds:Product ; msds:productName ?name . }")
        print("\n# Get all hazards:")
        print("SELECT ?hazard ?statement WHERE { ?hazard a msds:Hazard ; msds:hazardStatement ?statement . }")
        print("\n# Get all ingredients:")
        print("SELECT ?ingredient ?name ?cas WHERE { ?ingredient a msds:Ingredient ; msds:ingredientName ?name ; msds:casNumber ?cas . }")
        
    except Exception as e:
        logger.error(f"Execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
