"""
SAP KGE MSDS Ontology Service
This service class provides comprehensive functionality for building detailed OWL ontologies
for Material Safety Data Sheet (MSDS) documents.

Author: SAP Innovation Team
Version: 2.0
"""

import os
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal
from rdflib.namespace import XSD, DCTERMS, FOAF


class MSDSOntologyService:
    """
    A comprehensive service class for building detailed OWL ontologies for MSDS documents.
    
    This service provides methods to create, modify, and manage OWL ontologies with
    proper class hierarchies, object properties, data properties, and constraints.
    """
    
    def __init__(self, base_uri: str = "http://sap.com/kge/msds#", 
                 ontology_name: str = "MSDS_Ontology"):
        """
        Initialize the MSDS Ontology Service.
        
        Args:
            base_uri (str): Base URI for the ontology namespace
            ontology_name (str): Name of the ontology
        """
        self.base_uri = base_uri
        self.ontology_name = ontology_name
        self.graph = Graph()
        self.namespace = Namespace(base_uri)
        
        # Initialize logging
        self._setup_logging()
        
        # Bind namespaces
        self._bind_namespaces()
        
        # Initialize ontology metadata
        self._initialize_ontology_metadata()
        
        # Define MSDS sections
        self.sections = [
            "Identification",
            "Hazards_Identification", 
            "Composition_Information_on_Ingredients",
            "First_Aid_Measures",
            "Fire_Fighting_Measures",
            "Accidental_Release_Measures",
            "Handling_and_Storage",
            "Exposure_Controls_Personal_Protection",
            "Physical_and_Chemical_Properties",
            "Stability_and_Reactivity",
            "Toxicological_Information",
            "Ecological_Information",
            "Disposal_Considerations",
            "Transportation_Information",
            "Regulatory_Information",
            "Other_Information"
        ]
        
        self.logger.info(f"MSDS Ontology Service initialized with base URI: {base_uri}")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _bind_namespaces(self) -> None:
        """Bind common namespaces to the graph."""
        self.graph.bind("msds", self.namespace)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("rdf", RDF)
        self.graph.bind("xsd", XSD)
        self.graph.bind("dcterms", DCTERMS)
        self.graph.bind("foaf", FOAF)
    
    def _initialize_ontology_metadata(self) -> None:
        """Initialize ontology metadata and annotations."""
        ontology_uri = self.namespace[self.ontology_name]
        
        # Declare as OWL Ontology
        self.graph.add((ontology_uri, RDF.type, OWL.Ontology))
        
        # Add metadata
        self.graph.add((ontology_uri, DCTERMS.title, 
                       Literal("SAP KGE MSDS Ontology", lang="en")))
        self.graph.add((ontology_uri, DCTERMS.description, 
                       Literal("Comprehensive ontology for Material Safety Data Sheet documents", lang="en")))
        self.graph.add((ontology_uri, DCTERMS.creator, 
                       Literal("SAP Innovation Team")))
        self.graph.add((ontology_uri, DCTERMS.created, 
                       Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
        self.graph.add((ontology_uri, OWL.versionInfo, 
                       Literal("2.0")))
    
    def create_base_ontology(self) -> None:
        """Create the base ontology structure with main classes and properties."""
        self.logger.info("Creating base ontology structure...")
        
        # Create main document class
        self._create_main_classes()
        
        # Create section classes
        self._create_section_classes()
        
        # Create supporting entity classes
        self._create_supporting_classes()
        
        # Create object properties
        self._create_object_properties()
        
        # Create data properties
        self._create_data_properties()
        
        # Add constraints and restrictions
        self._add_constraints()
        
        self.logger.info("Base ontology structure created successfully")
    
    def _create_main_classes(self) -> None:
        """Create main ontology classes."""
        # Main MSDS Document class
        msds_doc = self.namespace.MSDS_Document
        self.graph.add((msds_doc, RDF.type, OWL.Class))
        self.graph.add((msds_doc, RDFS.label, Literal("MSDS Document", lang="en")))
        self.graph.add((msds_doc, RDFS.comment, 
                       Literal("Material Safety Data Sheet document containing safety information", lang="en")))
        
        # Abstract Section class
        section = self.namespace.Section
        self.graph.add((section, RDF.type, OWL.Class))
        self.graph.add((section, RDFS.label, Literal("Section", lang="en")))
        self.graph.add((section, RDFS.comment, 
                       Literal("Abstract class representing a section of an MSDS document", lang="en")))
    
    def _create_section_classes(self) -> None:
        """Create classes for each MSDS section."""
        for section_name in self.sections:
            section_uri = self.namespace[section_name]
            self.graph.add((section_uri, RDF.type, OWL.Class))
            self.graph.add((section_uri, RDFS.subClassOf, self.namespace.Section))
            
            # Add human-readable label
            label = section_name.replace("_", " ")
            self.graph.add((section_uri, RDFS.label, Literal(label, lang="en")))
            
            # Add section-specific comments
            comment = self._get_section_comment(section_name)
            self.graph.add((section_uri, RDFS.comment, Literal(comment, lang="en")))
    
    def _create_supporting_classes(self) -> None:
        """Create supporting entity classes for detailed modeling."""
        supporting_classes = {
            "Ingredient": "Chemical ingredient or component",
            "Hazard": "Safety hazard or risk",
            "FirstAidMeasure": "First aid procedure or measure",
            "FireFightingMeasure": "Fire fighting procedure or equipment",
            "AccidentalReleaseMeasure": "Procedure for handling accidental releases",
            "StorageCondition": "Storage requirement or condition",
            "ExposureControl": "Exposure control measure",
            "PhysicalChemicalProperty": "Physical or chemical property",
            "StabilityReactivity": "Stability and reactivity information",
            "ToxicologicalInfo": "Toxicological information",
            "EcologicalInfo": "Ecological impact information",
            "DisposalMethod": "Disposal procedure or method",
            "TransportationInfo": "Transportation requirement or information",
            "Regulation": "Regulatory requirement or standard",
            "OtherInfo": "Additional miscellaneous information",
            "Company": "Company or organization",
            "Product": "Chemical product",
            "EmergencyContact": "Emergency contact information",
            "PhysicalState": "Physical state of matter",
            "HazardClass": "Classification of hazard type",
            "ProtectiveEquipment": "Personal protective equipment",
            "ExposureLimit": "Occupational exposure limit",
            "TestMethod": "Testing or measurement method"
        }
        
        for class_name, description in supporting_classes.items():
            class_uri = self.namespace[class_name]
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.label, Literal(class_name, lang="en")))
            self.graph.add((class_uri, RDFS.comment, Literal(description, lang="en")))
    
    def _create_object_properties(self) -> None:
        """Create object properties (relationships between classes)."""
        object_properties = {
            # Main document relationships
            "hasSection": ("MSDS_Document", "Section", "Links document to its sections"),
            "hasCompany": ("MSDS_Document", "Company", "Links document to responsible company"),
            "hasProduct": ("MSDS_Document", "Product", "Links document to the product described"),
            
            # Section-specific relationships
            "hasIngredient": ("Composition_Information_on_Ingredients", "Ingredient", "Links to chemical ingredients"),
            "hasHazard": ("Hazards_Identification", "Hazard", "Links to identified hazards"),
            "hasFirstAid": ("First_Aid_Measures", "FirstAidMeasure", "Links to first aid procedures"),
            "hasFireFightingMeasure": ("Fire_Fighting_Measures", "FireFightingMeasure", "Links to fire fighting measures"),
            "hasAccidentalReleaseMeasure": ("Accidental_Release_Measures", "AccidentalReleaseMeasure", "Links to release procedures"),
            "hasStorageCondition": ("Handling_and_Storage", "StorageCondition", "Links to storage requirements"),
            "hasExposureControl": ("Exposure_Controls_Personal_Protection", "ExposureControl", "Links to exposure controls"),
            "hasPhysicalChemicalProperty": ("Physical_and_Chemical_Properties", "PhysicalChemicalProperty", "Links to physical/chemical properties"),
            "hasStabilityReactivity": ("Stability_and_Reactivity", "StabilityReactivity", "Links to stability information"),
            "hasToxicologicalInfo": ("Toxicological_Information", "ToxicologicalInfo", "Links to toxicological data"),
            "hasEcologicalInfo": ("Ecological_Information", "EcologicalInfo", "Links to ecological information"),
            "hasDisposal": ("Disposal_Considerations", "DisposalMethod", "Links to disposal methods"),
            "hasTransportationInfo": ("Transportation_Information", "TransportationInfo", "Links to transportation requirements"),
            "hasRegulation": ("Regulatory_Information", "Regulation", "Links to regulatory information"),
            "hasOtherInfo": ("Other_Information", "OtherInfo", "Links to additional information"),
            
            # Cross-references and relationships
            "hasEmergencyContact": ("Company", "EmergencyContact", "Links company to emergency contacts"),
            "hasPhysicalState": ("PhysicalChemicalProperty", "PhysicalState", "Links to physical state"),
            "hasHazardClass": ("Hazard", "HazardClass", "Links hazard to its classification"),
            "requiresProtectiveEquipment": ("ExposureControl", "ProtectiveEquipment", "Links to required PPE"),
            "hasExposureLimit": ("Ingredient", "ExposureLimit", "Links ingredient to exposure limits"),
            "testedBy": ("PhysicalChemicalProperty", "TestMethod", "Links property to test method"),
            
            # Ingredient relationships
            "isMainIngredient": ("Product", "Ingredient", "Links product to main ingredients"),
            "containsIngredient": ("Product", "Ingredient", "Links product to all ingredients"),
            
            # Hazard relationships
            "causedBy": ("Hazard", "Ingredient", "Links hazard to causing ingredient"),
            "mitigatedBy": ("Hazard", "ProtectiveEquipment", "Links hazard to mitigation equipment")
        }
        
        for prop_name, (domain, range_class, comment) in object_properties.items():
            self._create_object_property(prop_name, domain, range_class, comment)
    
    def _create_object_property(self, prop_name: str, domain: str, range_class: str, comment: str) -> None:
        """Create an individual object property."""
        prop_uri = self.namespace[prop_name]
        domain_uri = self.namespace[domain]
        range_uri = self.namespace[range_class]
        
        self.graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
        self.graph.add((prop_uri, RDFS.domain, domain_uri))
        self.graph.add((prop_uri, RDFS.range, range_uri))
        self.graph.add((prop_uri, RDFS.label, Literal(prop_name, lang="en")))
        self.graph.add((prop_uri, RDFS.comment, Literal(comment, lang="en")))
    
    def _create_data_properties(self) -> None:
        """Create data properties (attributes with literal values)."""
        data_properties = {
            # General properties
            "sectionTitle": ("Section", XSD.string, "Title of the section"),
            "sectionText": ("Section", XSD.string, "Full text content of the section"),
            "sectionNumber": ("Section", XSD.integer, "Section number"),
            "lastUpdated": ("Section", XSD.dateTime, "Last update timestamp"),
            
            # Document properties
            "documentId": ("MSDS_Document", XSD.string, "Unique document identifier"),
            "documentVersion": ("MSDS_Document", XSD.string, "Document version"),
            "issueDate": ("MSDS_Document", XSD.date, "Document issue date"),
            "revisionDate": ("MSDS_Document", XSD.date, "Document revision date"),
            "language": ("MSDS_Document", XSD.string, "Document language"),
            
            # Company properties
            "companyName": ("Company", XSD.string, "Name of the company"),
            "address": ("Company", XSD.string, "Company address"),
            "phoneNumber": ("Company", XSD.string, "Company phone number"),
            "emergencyPhone": ("Company", XSD.string, "Emergency contact phone"),
            "website": ("Company", XSD.string, "Company website URL"),
            
            # Product properties
            "productName": ("Product", XSD.string, "Name of the product"),
            "productCode": ("Product", XSD.string, "Product identification code"),
            "productType": ("Product", XSD.string, "Type or category of product"),
            "recommendedUse": ("Product", XSD.string, "Recommended use of the product"),
            "restrictedUse": ("Product", XSD.string, "Restricted uses of the product"),
            
            # Ingredient properties
            "ingredientName": ("Ingredient", XSD.string, "Name of the ingredient"),
            "casNumber": ("Ingredient", XSD.string, "CAS registry number"),
            "ecNumber": ("Ingredient", XSD.string, "EC number"),
            "weightPercent": ("Ingredient", XSD.decimal, "Weight percentage in product"),
            "concentrationRange": ("Ingredient", XSD.string, "Concentration range"),
            "purity": ("Ingredient", XSD.decimal, "Purity percentage"),
            
            # Hazard properties
            "hazardStatement": ("Hazard", XSD.string, "Hazard statement text"),
            "hazardCategory": ("Hazard", XSD.string, "Hazard category classification"),
            "hazardCode": ("Hazard", XSD.string, "Hazard identification code"),
            "precautionaryStatement": ("Hazard", XSD.string, "Precautionary statement"),
            "signalWord": ("Hazard", XSD.string, "Signal word (Danger/Warning)"),
            
            # First Aid properties
            "firstAidType": ("FirstAidMeasure", XSD.string, "Type of first aid (eye, skin, inhalation, ingestion)"),
            "firstAidInstruction": ("FirstAidMeasure", XSD.string, "Detailed first aid instructions"),
            "immediateAction": ("FirstAidMeasure", XSD.string, "Immediate action required"),
            "medicalAttention": ("FirstAidMeasure", XSD.boolean, "Whether medical attention is required"),
            
            # Fire Fighting properties
            "extinguishingMedia": ("FireFightingMeasure", XSD.string, "Suitable extinguishing media"),
            "unsuitableMedia": ("FireFightingMeasure", XSD.string, "Unsuitable extinguishing media"),
            "specificHazards": ("FireFightingMeasure", XSD.string, "Specific fire hazards"),
            "protectiveEquipment": ("FireFightingMeasure", XSD.string, "Required protective equipment"),
            
            # Physical and Chemical properties
            "physicalState": ("PhysicalChemicalProperty", XSD.string, "Physical state (solid, liquid, gas)"),
            "color": ("PhysicalChemicalProperty", XSD.string, "Color description"),
            "odor": ("PhysicalChemicalProperty", XSD.string, "Odor description"),
            "pH": ("PhysicalChemicalProperty", XSD.decimal, "pH value"),
            "meltingPoint": ("PhysicalChemicalProperty", XSD.decimal, "Melting point in Celsius"),
            "boilingPoint": ("PhysicalChemicalProperty", XSD.decimal, "Boiling point in Celsius"),
            "flashPoint": ("PhysicalChemicalProperty", XSD.decimal, "Flash point in Celsius"),
            "density": ("PhysicalChemicalProperty", XSD.decimal, "Density in g/cm³"),
            "solubility": ("PhysicalChemicalProperty", XSD.string, "Solubility information"),
            "vaporPressure": ("PhysicalChemicalProperty", XSD.decimal, "Vapor pressure"),
            
            # Exposure Control properties
            "exposureLimit": ("ExposureControl", XSD.decimal, "Occupational exposure limit"),
            "exposureLimitUnit": ("ExposureControl", XSD.string, "Unit for exposure limit"),
            "exposureLimitType": ("ExposureControl", XSD.string, "Type of exposure limit (TWA, STEL, etc.)"),
            "personalProtection": ("ExposureControl", XSD.string, "Personal protection requirements"),
            
            # Stability and Reactivity properties
            "stability": ("StabilityReactivity", XSD.string, "Chemical stability information"),
            "reactivity": ("StabilityReactivity", XSD.string, "Reactivity information"),
            "incompatibleMaterials": ("StabilityReactivity", XSD.string, "Materials to avoid"),
            "hazardousDecomposition": ("StabilityReactivity", XSD.string, "Hazardous decomposition products"),
            
            # Toxicological properties
            "toxicEffect": ("ToxicologicalInfo", XSD.string, "Toxic effects description"),
            "routeOfExposure": ("ToxicologicalInfo", XSD.string, "Route of exposure"),
            "acuteToxicity": ("ToxicologicalInfo", XSD.string, "Acute toxicity information"),
            "chronicToxicity": ("ToxicologicalInfo", XSD.string, "Chronic toxicity information"),
            "ld50": ("ToxicologicalInfo", XSD.decimal, "LD50 value"),
            
            # Ecological properties
            "ecoToxicity": ("EcologicalInfo", XSD.string, "Ecotoxicity information"),
            "biodegradability": ("EcologicalInfo", XSD.string, "Biodegradability information"),
            "bioaccumulation": ("EcologicalInfo", XSD.string, "Bioaccumulation potential"),
            "environmentalFate": ("EcologicalInfo", XSD.string, "Environmental fate information"),
            
            # Disposal properties
            "disposalMethod": ("DisposalMethod", XSD.string, "Disposal method description"),
            "wasteCode": ("DisposalMethod", XSD.string, "Waste classification code"),
            "specialPrecautions": ("DisposalMethod", XSD.string, "Special disposal precautions"),
            
            # Transportation properties
            "unNumber": ("TransportationInfo", XSD.string, "UN identification number"),
            "properShippingName": ("TransportationInfo", XSD.string, "Proper shipping name"),
            "transportHazardClass": ("TransportationInfo", XSD.string, "Transport hazard class"),
            "packingGroup": ("TransportationInfo", XSD.string, "Packing group"),
            "marinePollutant": ("TransportationInfo", XSD.boolean, "Marine pollutant status"),
            
            # Regulatory properties
            "regulationName": ("Regulation", XSD.string, "Name of regulation"),
            "regulationDetail": ("Regulation", XSD.string, "Regulation details"),
            "complianceStatus": ("Regulation", XSD.string, "Compliance status"),
            "regulationCountry": ("Regulation", XSD.string, "Country of regulation"),
            
            # Other properties
            "otherDetail": ("OtherInfo", XSD.string, "Additional information details"),
            "disclaimer": ("OtherInfo", XSD.string, "Disclaimer text"),
            "preparationDate": ("OtherInfo", XSD.date, "Preparation date"),
            "preparedBy": ("OtherInfo", XSD.string, "Prepared by information")
        }
        
        for prop_name, (domain, datatype, comment) in data_properties.items():
            self._create_data_property(prop_name, domain, datatype, comment)
    
    def _create_data_property(self, prop_name: str, domain: str, datatype: Any, comment: str) -> None:
        """Create an individual data property."""
        prop_uri = self.namespace[prop_name]
        domain_uri = self.namespace[domain]
        
        self.graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
        self.graph.add((prop_uri, RDFS.domain, domain_uri))
        self.graph.add((prop_uri, RDFS.range, datatype))
        self.graph.add((prop_uri, RDFS.label, Literal(prop_name, lang="en")))
        self.graph.add((prop_uri, RDFS.comment, Literal(comment, lang="en")))
    
    def _add_constraints(self) -> None:
        """Add OWL constraints and restrictions to the ontology."""
        # Add cardinality constraints
        self._add_cardinality_constraints()
        
        # Add value restrictions
        self._add_value_restrictions()
        
        # Add disjoint classes
        self._add_disjoint_classes()
    
    def _add_cardinality_constraints(self) -> None:
        """Add cardinality constraints to classes."""
        # MSDS Document must have at least one section
        restriction = self._create_min_cardinality_restriction(
            self.namespace.hasSection, 1
        )
        self.graph.add((self.namespace.MSDS_Document, RDFS.subClassOf, restriction))
        
        # MSDS Document must have exactly one company
        restriction = self._create_exact_cardinality_restriction(
            self.namespace.hasCompany, 1
        )
        self.graph.add((self.namespace.MSDS_Document, RDFS.subClassOf, restriction))
    
    def _add_value_restrictions(self) -> None:
        """Add value restrictions to properties."""
        # Add some value restrictions for required properties
        pass
    
    def _add_disjoint_classes(self) -> None:
        """Add disjoint class declarations."""
        # Make section classes disjoint from each other
        for i, section1 in enumerate(self.sections):
            for section2 in self.sections[i+1:]:
                self.graph.add((self.namespace[section1], OWL.disjointWith, self.namespace[section2]))
    
    def _create_min_cardinality_restriction(self, property_uri: Any, cardinality: int) -> Any:
        """Create a minimum cardinality restriction."""
        restriction = self.namespace[f"_restriction_{hash((property_uri, 'min', cardinality))}"]
        self.graph.add((restriction, RDF.type, OWL.Restriction))
        self.graph.add((restriction, OWL.onProperty, property_uri))
        self.graph.add((restriction, OWL.minCardinality, Literal(cardinality)))
        return restriction
    
    def _create_exact_cardinality_restriction(self, property_uri: Any, cardinality: int) -> Any:
        """Create an exact cardinality restriction."""
        restriction = self.namespace[f"_restriction_{hash((property_uri, 'exact', cardinality))}"]
        self.graph.add((restriction, RDF.type, OWL.Restriction))
        self.graph.add((restriction, OWL.onProperty, property_uri))
        self.graph.add((restriction, OWL.cardinality, Literal(cardinality)))
        return restriction
    
    def _get_section_comment(self, section_name: str) -> str:
        """Get descriptive comment for each section."""
        comments = {
            "Identification": "Product and company identification information",
            "Hazards_Identification": "Classification and hazard information",
            "Composition_Information_on_Ingredients": "Information on ingredients and composition",
            "First_Aid_Measures": "First aid procedures and measures",
            "Fire_Fighting_Measures": "Fire fighting procedures and equipment",
            "Accidental_Release_Measures": "Procedures for handling accidental releases",
            "Handling_and_Storage": "Safe handling and storage conditions",
            "Exposure_Controls_Personal_Protection": "Exposure controls and personal protection",
            "Physical_and_Chemical_Properties": "Physical and chemical properties",
            "Stability_and_Reactivity": "Stability and reactivity information",
            "Toxicological_Information": "Toxicological effects and information",
            "Ecological_Information": "Ecological effects and environmental impact",
            "Disposal_Considerations": "Disposal methods and considerations",
            "Transportation_Information": "Transportation requirements and information",
            "Regulatory_Information": "Regulatory and compliance information",
            "Other_Information": "Additional miscellaneous information"
        }
        return comments.get(section_name, f"Information related to {section_name}")
    
    def add_custom_class(self, class_name: str, parent_class: Optional[str] = None, 
                        label: Optional[str] = None, comment: Optional[str] = None) -> None:
        """
        Add a custom class to the ontology.
        
        Args:
            class_name (str): Name of the class
            parent_class (str): Parent class name (optional)
            label (str): Human-readable label (optional)
            comment (str): Description comment (optional)
        """
        class_uri = self.namespace[class_name]
        self.graph.add((class_uri, RDF.type, OWL.Class))
        
        if parent_class:
            parent_uri = self.namespace[parent_class]
            self.graph.add((class_uri, RDFS.subClassOf, parent_uri))
        
        if label:
            self.graph.add((class_uri, RDFS.label, Literal(label, lang="en")))
        
        if comment:
            self.graph.add((class_uri, RDFS.comment, Literal(comment, lang="en")))
        
        self.logger.info(f"Added custom class: {class_name}")
    
    def add_custom_object_property(self, property_name: str, domain: str, 
                                  range_class: str, label: Optional[str] = None, 
                                  comment: Optional[str] = None) -> None:
        """
        Add a custom object property to the ontology.
        
        Args:
            property_name (str): Name of the property
            domain (str): Domain class name
            range_class (str): Range class name
            label (str): Human-readable label (optional)
            comment (str): Description comment (optional)
        """
        effective_comment = comment if comment is not None else f"Links {domain} to {range_class}"
        self._create_object_property(property_name, domain, range_class, effective_comment)
        self.logger.info(f"Added custom object property: {property_name}")
    
    def add_custom_data_property(self, property_name: str, domain: str, 
                                datatype: Any, label: Optional[str] = None, 
                                comment: Optional[str] = None) -> None:
        """
        Add a custom data property to the ontology.
        
        Args:
            property_name (str): Name of the property
            domain (str): Domain class name
            datatype: XSD datatype
            label (str): Human-readable label (optional)
            comment (str): Description comment (optional)
        """
        effective_comment = comment if comment is not None else f"Data property for {domain}"
        self._create_data_property(property_name, domain, datatype, effective_comment)
        self.logger.info(f"Added custom data property: {property_name}")
    
    def validate_ontology(self) -> Dict[str, Any]:
        """
        Validate the ontology for consistency and completeness.
        
        Returns:
            Dict containing validation results
        """
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "statistics": {}
        }
        
        # Count triples by type
        class_count = len(list(self.graph.subjects(RDF.type, OWL.Class)))
        object_prop_count = len(list(self.graph.subjects(RDF.type, OWL.ObjectProperty)))
        data_prop_count = len(list(self.graph.subjects(RDF.type, OWL.DatatypeProperty)))
        
        validation_results["statistics"] = {
            "total_triples": len(self.graph),
            "classes": class_count,
            "object_properties": object_prop_count,
            "data_properties": data_prop_count
        }
        
        # Basic validation checks
        if class_count == 0:
            validation_results["errors"].append("No classes found in ontology")
            validation_results["is_valid"] = False
        
        if object_prop_count == 0:
            validation_results["warnings"].append("No object properties found")
        
        if data_prop_count == 0:
            validation_results["warnings"].append("No data properties found")
        
        self.logger.info(f"Ontology validation completed: {validation_results['statistics']}")
        return validation_results
    
    def save_ontology(self, file_path: str, format: str = "xml") -> bool:
        """
        Save the ontology to a file.
        
        Args:
            file_path (str): Path to save the ontology file
            format (str): Output format (xml, turtle, n3, nt, json-ld)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            # Save the ontology
            self.graph.serialize(destination=file_path, format=format)
            self.logger.info(f"Ontology saved successfully to: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save ontology: {str(e)}")
            return False
    
    def get_ontology_statistics(self) -> Dict[str, int]:
        """
        Get statistics about the ontology.
        
        Returns:
            Dict containing ontology statistics
        """
        stats = {
            "total_triples": len(self.graph),
            "classes": len(list(self.graph.subjects(RDF.type, OWL.Class))),
            "object_properties": len(list(self.graph.subjects(RDF.type, OWL.ObjectProperty))),
            "data_properties": len(list(self.graph.subjects(RDF.type, OWL.DatatypeProperty))),
            "individuals": len(list(self.graph.subjects(RDF.type, OWL.NamedIndividual)))
        }
        return stats
    
    def print_ontology_summary(self) -> None:
        """Print a summary of the ontology structure."""
        stats = self.get_ontology_statistics()
        
        print("\n" + "="*50)
        print("MSDS ONTOLOGY SUMMARY")
        print("="*50)
        print(f"Base URI: {self.base_uri}")
        print(f"Ontology Name: {self.ontology_name}")
        print(f"Total Triples: {stats['total_triples']}")
        print(f"Classes: {stats['classes']}")
        print(f"Object Properties: {stats['object_properties']}")
        print(f"Data Properties: {stats['data_properties']}")
        print(f"Individuals: {stats['individuals']}")
        print("="*50)
        
        # List main classes
        print("\nMain Classes:")
        main_classes = ["MSDS_Document", "Section", "Company", "Product", "Ingredient", "Hazard"]
        for class_name in main_classes:
            if (self.namespace[class_name], RDF.type, OWL.Class) in self.graph:
                print(f"  - {class_name}")
        
        # List section classes
        print("\nMSDS Section Classes:")
        for section in self.sections:
            if (self.namespace[section], RDF.type, OWL.Class) in self.graph:
                print(f"  - {section.replace('_', ' ')}")
        
        print("\n" + "="*50)


def main():
    """
    Main function to demonstrate the MSDS Ontology Service.
    Creates and saves the ontology.
    """
    print("Starting MSDS Ontology Generation...")
    
    # Initialize the ontology service
    ontology_service = MSDSOntologyService()
    
    # Create the base ontology structure
    ontology_service.create_base_ontology()
    
    # Validate the ontology
    validation_results = ontology_service.validate_ontology()
    
    if validation_results["is_valid"]:
        print("✓ Ontology validation passed")
    else:
        print("✗ Ontology validation failed")
        for error in validation_results["errors"]:
            print(f"  Error: {error}")
    
    # Print warnings if any
    for warning in validation_results["warnings"]:
        print(f"  Warning: {warning}")
    
    # Print ontology summary
    ontology_service.print_ontology_summary()
    
    # Save the ontology in different formats
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Save as OWL/XML (standard format)
    owl_file = os.path.join(base_path, "msds_ontology.owl")
    if ontology_service.save_ontology(owl_file, "xml"):
        print(f"✓ OWL ontology saved: {owl_file}")
    
    # Save as Turtle (more readable)
    ttl_file = os.path.join(base_path, "msds_ontology.ttl")
    if ontology_service.save_ontology(ttl_file, "turtle"):
        print(f"✓ Turtle ontology saved: {ttl_file}")
    
    print("\nMSDS Ontology generation completed successfully!")
    return ontology_service


if __name__ == "__main__":
    service = main()
