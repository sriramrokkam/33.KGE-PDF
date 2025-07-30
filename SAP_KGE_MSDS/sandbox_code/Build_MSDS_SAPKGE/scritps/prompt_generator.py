import re


class cl_msds_Ontology_PromptGenerator:
    """
    OOP class for generating a structured prompt for MSDS RDF extraction using the provided ontology file.
    Reads the ontology, extracts section names and allowed attributes, and builds a prompt template for LLMs.
    """

    def __init__(self, ontology_path):
        self.ontology_path = ontology_path
        self.sections = []
        self.attributes = []
        self._parse_ontology()

    def _parse_ontology(self):
        with open(self.ontology_path, 'r') as f:
            ttl = f.read()
        # Extract section classes (top-level SDS sections)
        self.sections = re.findall(r'sds:([A-Za-z0-9]+) a rdfs:Class ;', ttl)
        # Extract all property labels as allowed attributes
        self.attributes = re.findall(r'rdfs:label "([^"]+)" ;', ttl)

    def get_sections(self):
        """Returns the list of SDS section names."""
        return self.sections

    def get_allowed_attributes(self):
        """Returns the list of allowed attribute labels."""
        return self.attributes

    def generate_prompt(self, msds_text):
        """
        Returns a prompt string for LLM extraction, using the ontology sections and allowed attributes.
        Args:
            msds_text (str): The input MSDS document text.
        Returns:
            str: The formatted prompt for LLM.
        """
        prompt = (
            "# Knowledge Graph Extraction Instructions for MSDS\n\n"
            "## 1. Overview\n"
            "You are an expert system for extracting RDF triples from Material Safety Data Sheets (MSDS) using the provided ontology. Strictly follow the ontology structure and allowed attributes.\n\n"
            "## 2. SDS Sections\n"
            "Extract information for each of the following 16 SDS sections:\n" + ', '.join(self.sections) + "\n\n"
            "## 3. Allowed Attributes\n"
            "Only extract properties that match the following allowed attributes (case-insensitive, partial match allowed):\n" + ', '.join(self.attributes) + "\n\n"
            "## 4. Output Format\n"
            "- Output RDF triples in the format: (Subject, Predicate, Object)\n"
            "- Use the provided section and attribute names for consistency.\n"
            "- Do not create nodes for numbers or dates; attach them as attributes.\n"
            "- Ignore any information not matching the allowed attributes or sections.\n\n"
            "## 5. Example\n"
            "MSDS Text:\n" + '"""\n' + msds_text + '\n"""\n' +
            "Output:\n"
            "(Subject, Predicate, Object)\n"
            "... (repeat for all extracted triples)\n"
        )
        return prompt

# Example usage:
# prompt_gen = MSDSOntologyPromptGenerator("path/to/ontology_file.ttl")
# prompt = prompt_gen.generate_prompt(pdf_text)
# print(prompt)
