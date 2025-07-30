
from langchain_community.graphs.networkx_graph import KG_TRIPLE_DELIMITER
from langchain_core.prompts.prompt import PromptTemplate

MSDS_KNOWLEDGE_TRIPLE_EXTRACTION_TEMPLATE = (  
    f"""## CRITICAL INSTRUCTION: Extract Knowledge Graph Triples in EXACT Subject-Predicate-Object Order

You MUST extract triples in this EXACT format: (Subject, Predicate, Object)

## WRONG FORMAT EXAMPLES (DO NOT DO THIS):
- (WD-40 Multi-Use Product Aerosol, Chemical, is a) ❌ WRONG
- (WD-40 Multi-Use Product Aerosol, WD-40 Company, is manufactured by) ❌ WRONG
- (WD-40 Multi-Use Product Aerosol, Lubricant, has) ❌ WRONG

## CORRECT FORMAT EXAMPLES (DO THIS):
- (WD-40 Multi-Use Product Aerosol, is a, Chemical) ✅ CORRECT
- (WD-40 Multi-Use Product Aerosol, is manufactured by, WD-40 Company) ✅ CORRECT
- (WD-40 Multi-Use Product Aerosol, has, Lubricant) ✅ CORRECT

## MANDATORY RULES:
1. **Subject**: Always the main entity being described
2. **Predicate**: Always the relationship/action word (is a, has, includes, is manufactured by, etc.)
3. **Object**: Always the target entity or value

## Allowed Predicates (MIDDLE position only):
- is a
- has
- includes
- is classified as
- is manufactured by
- is located at
- is regulated by
- is exposed to
- is protected by
- is described by
- is recommended for

## Node Types for Objects:
Chemical, Hazard, Manufacturer, ExposureLimit, PhysicalProperty, ProtectiveMeasure, Regulation, Location, Contact

## EXAMPLE - Study this carefully:
Text: "WD-40 Multi-Use Product Aerosol contains LVP Aliphatic Hydrocarbon (CAS# 64742-47-8) with 45-50% weight. It is classified as Aspiration Toxicity Category 1."

CORRECT Output:
(WD-40 Multi-Use Product Aerosol, is a, Chemical){KG_TRIPLE_DELIMITER}
(WD-40 Multi-Use Product Aerosol, includes, LVP Aliphatic Hydrocarbon){KG_TRIPLE_DELIMITER}
(LVP Aliphatic Hydrocarbon, has, CAS# 64742-47-8){KG_TRIPLE_DELIMITER}
(LVP Aliphatic Hydrocarbon, has, 45-50% weight){KG_TRIPLE_DELIMITER}
(LVP Aliphatic Hydrocarbon, is classified as, Aspiration Toxicity Category 1){KG_TRIPLE_DELIMITER}

## Your Task:
Extract triples from the following MSDS text. Remember: Subject-Predicate-Object order is MANDATORY.

Text: {{text}}

Output:
"""
)


KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["text"],
    template=MSDS_KNOWLEDGE_TRIPLE_EXTRACTION_TEMPLATE,
)


MSDS_KNOWLEDGE_TRIPLE_EXTRACTION_TEMPLATE_KG_RAG = (
    f"""## CRITICAL INSTRUCTION: Extract Knowledge Graph Triples in EXACT Subject-Predicate-Object Order (Ontology-Aware)

You MUST extract triples in this EXACT format: (Subject, Predicate, Object)

## WRONG FORMAT EXAMPLES (DO NOT DO THIS):
- (WD-40, Product, is a) ❌ WRONG
- (WD-40, LVP Aliphatic Hydrocarbon, includes) ❌ WRONG
- (LVP Aliphatic Hydrocarbon, CAS# 64742-47-8, has) ❌ WRONG

## CORRECT FORMAT EXAMPLES (DO THIS):
- (WD-40, is a, Product) ✅ CORRECT
- (WD-40, includes, LVP Aliphatic Hydrocarbon) ✅ CORRECT
- (LVP Aliphatic Hydrocarbon, has, CAS# 64742-47-8) ✅ CORRECT

## MANDATORY RULES:
1. **Subject**: Always the main entity being described
2. **Predicate**: Always the relationship/action word (is a, has, includes, is manufactured by, etc.)
3. **Object**: Always the target entity or value

## Allowed Predicates (MIDDLE position only):
- is a
- has
- includes
- is classified as
- is manufactured by
- is located at
- is regulated by
- is exposed to
- is protected by
- is described by
- is recommended for

## Attribute Filtering (Data Properties)
- **IMPORTANT**: Extract ONLY information that corresponds exactly or closely matches the allowed attributes list below:
  {{allowedAttributes}}
- If a property, standard, or compliance from the text matches any of the allowed attributes (case insensitive, partial matching allowed), extract it.
- Ignore all other attributes or properties.

## Node Types for Objects:
Product, Chemical, Hazard, Manufacturer, ExposureLimit, PhysicalProperty, ProtectiveMeasure, Regulation, Location, Contact

## EXAMPLE - Study this carefully:
Text: "WD-40 contains LVP Aliphatic Hydrocarbon (CAS# 64742-47-8) with 45–50% weight. It is classified as Aspiration Toxicity Category 1."

CORRECT Output:
(WD-40, is a, Product){KG_TRIPLE_DELIMITER}
(WD-40, includes, LVP Aliphatic Hydrocarbon){KG_TRIPLE_DELIMITER}
(LVP Aliphatic Hydrocarbon, has, CAS# 64742-47-8){KG_TRIPLE_DELIMITER}
(LVP Aliphatic Hydrocarbon, has, 45–50% weight){KG_TRIPLE_DELIMITER}
(LVP Aliphatic Hydrocarbon, is classified as, Aspiration Toxicity Category 1){KG_TRIPLE_DELIMITER}

## Your Task:
Extract triples from the following MSDS text. Remember: Subject-Predicate-Object order is MANDATORY.
Only extract information matching the allowed attributes: {{allowedAttributes}}

Text: {{text}}

Output:
"""
)

KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT_KG_RAG = PromptTemplate(
    input_variables=["text", "allowedAttributes"],
    template=MSDS_KNOWLEDGE_TRIPLE_EXTRACTION_TEMPLATE_KG_RAG,
)
