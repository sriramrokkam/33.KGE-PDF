# SAP KGE MSDS - Knowledge Graph Extraction from MSDS Documents

This project implements a 4-step approach for building Knowledge Graphs from Material Safety Data Sheets (MSDS) documents using OWL ontologies and RDF triple extraction.

## Project Overview

The project processes MSDS documents (specifically WD-40 Multi-Use Product Aerosol) to create structured knowledge graphs that can be used for RAG (Retrieval-Augmented Generation) applications.

## Project Structure

```
V2_MSDS_KGE/
├── S1_Ontology_Generation/          # Step 1: OWL Ontology Design
│   ├── 01_Ontology_Design.py        # Main ontology generation script
│   ├── msds_ontology.owl            # Generated OWL ontology file
│   └── wd-40.pdf                    # Source MSDS document
├── S2_Tupple_Generation/            # Step 2: RDF Triple Extraction
│   ├── 02_Tuple_Extraction.py       # Basic tuple extraction
│   ├── 03_Enhanced_Tuple_Extraction.py  # Enhanced extraction with better parsing
│   ├── wd-40.rdf                    # Basic RDF triples (XML format)
│   ├── wd-40.ttl                    # Basic RDF triples (Turtle format)
│   ├── wd-40_enhanced.rdf           # Enhanced RDF triples (XML format)
│   └── wd-40_enhanced.ttl           # Enhanced RDF triples (Turtle format)
├── S3_Data_Ingestion/               # Step 3: Database Integration (Future)
├── S4_Lets_Chat/                    # Step 4: RAG Chat Interface (Future)
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Completed Tasks

### ✅ Task 1: OWL Ontology Generation

**File**: `S1_Ontology_Generation/01_Ontology_Design.py`

**Features**:
- Comprehensive OWL ontology for MSDS documents
- 16 main section classes representing standard MSDS sections:
  1. Identification
  2. Hazards Identification
  3. Composition/Information on Ingredients
  4. First Aid Measures
  5. Fire Fighting Measures
  6. Accidental Release Measures
  7. Handling and Storage
  8. Exposure Controls/Personal Protection
  9. Physical and Chemical Properties
  10. Stability and Reactivity
  11. Toxicological Information
  12. Ecological Information
  13. Disposal Considerations
  14. Transportation Information
  15. Regulatory Information
  16. Other Information

**Object Properties**:
- `hasSection`, `hasIngredient`, `hasHazard`, `hasFirstAid`
- `hasFireFightingMeasure`, `hasAccidentalReleaseMeasure`
- `hasStorageCondition`, `hasExposureControl`
- `hasPhysicalChemicalProperty`, `hasStabilityReactivity`
- `hasToxicologicalInfo`, `hasEcologicalInfo`
- `hasTransportationInfo`, `hasOtherInfo`

**Data Properties**:
- Basic properties: `sectionTitle`, `sectionText`
- Ingredient properties: `ingredientName`, `casNumber`, `weightPercent`
- Hazard properties: `hazardStatement`, `hazardCategory`
- First aid properties: `firstAidType`, `firstAidInstruction`
- Physical properties: `physicalState`, `color`, `odor`
- And many more specialized properties

**Usage**:
```bash
cd S1_Ontology_Generation
python 01_Ontology_Design.py
```

**Output**: `msds_ontology.owl` - Complete OWL ontology file

### ✅ Task 2: Tuple Extraction

**Files**: 
- `S2_Tupple_Generation/02_Tuple_Extraction.py` (Basic version)
- `S2_Tupple_Generation/03_Enhanced_Tuple_Extraction.py` (Enhanced version)

**Basic Extraction Features**:
- PDF text extraction using PyPDF2
- Section-based parsing using regex patterns
- Basic RDF triple generation
- Support for ingredients, hazards, and first aid measures

**Enhanced Extraction Features**:
- Improved section parsing with better regex patterns
- Structured data extraction for:
  - **Ingredients**: Name, CAS number, weight percentage, classification
  - **Hazards**: Hazard statements, categories (GHS classifications)
  - **First Aid Measures**: Type-specific instructions
  - **Physical Properties**: State, color, odor, flash point, etc.
- More comprehensive RDF triple generation
- Better error handling and logging
- Output in both RDF/XML and Turtle formats

**Usage**:
```bash
cd S2_Tupple_Generation

# Basic extraction
python 02_Tuple_Extraction.py

# Enhanced extraction (recommended)
python 03_Enhanced_Tuple_Extraction.py
```

**Outputs**:
- `wd-40.rdf` / `wd-40.ttl` - Basic RDF triples
- `wd-40_enhanced.rdf` / `wd-40_enhanced.ttl` - Enhanced RDF triples

## Installation & Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Required Python Packages**:
- `rdflib` - RDF graph manipulation
- `PyPDF2` - PDF text extraction
- `hdbcli` - SAP HANA database connectivity (for future steps)
- `tabulate` - Table formatting
- `colorama` - Colored terminal output
- `python-dotenv` - Environment variable management

## Data Extraction Results

### Enhanced Extraction Statistics:
- **Total Sections**: 16 (all MSDS sections)
- **Hazards Identified**: 7 hazard statements
- **First Aid Measures**: 6 different types
- **Physical Properties**: 3 key properties extracted
- **Total RDF Triples**: 126 triples generated

### Key Extracted Information:

**Hazards**:
- Aerosol Category 1
- Aspiration Toxicity Category 1
- Specific Target Organ Toxicity Single Exposure Category 3
- Extremely Flammable Aerosol
- DANGER warnings

**First Aid Measures**:
- Ingestion procedures
- Eye contact treatment
- Skin contact treatment
- Inhalation response
- Signs and symptoms
- Medical attention requirements

**Physical Properties**:
- Physical state: Liquid packaged as aerosol
- Color: Light green to amber
- Odor: Mild petroleum odor

## Ontology Namespace

All RDF resources use the namespace: `http://sap.com/kge/msds#`

## Future Development (Steps 3 & 4)

### Step 3: Data Ingestion
- Integration with SAP HANA database
- Bulk RDF data loading
- SPARQL endpoint setup

### Step 4: RAG Chat Interface
- Question-answering system over the knowledge graph
- SPARQL query generation from natural language
- Integration with SAP AI Core for enhanced responses

## File Formats

- **OWL**: Web Ontology Language for semantic definitions
- **RDF/XML**: RDF serialization in XML format
- **Turtle (TTL)**: Human-readable RDF serialization
- **PDF**: Source MSDS document format

## Technical Notes

- The ontology follows OWL 2 standards
- RDF triples use typed literals with XSD datatypes
- Section parsing handles various MSDS document formats
- Enhanced extraction includes regex-based pattern matching for structured data

## Usage Examples

### Query the Knowledge Graph (using rdflib):

```python
from rdflib import Graph

# Load the enhanced RDF data
g = Graph()
g.parse("S2_Tupple_Generation/wd-40_enhanced.ttl", format="turtle")

# Query for all hazards
query = """
PREFIX msds: <http://sap.com/kge/msds#>
SELECT ?hazard ?statement WHERE {
    ?hazard a msds:Hazard .
    ?hazard msds:hazardStatement ?statement .
}
"""

results = g.query(query)
for row in results:
    print(f"Hazard: {row.statement}")
```

## Contributing

When extending this project:
1. Follow the existing naming conventions
2. Update the ontology if new concepts are added
3. Ensure RDF triples are properly typed
4. Add appropriate documentation

## License

This project is part of SAP's innovation initiatives for Knowledge Graph Extraction from enterprise documents.
