from PyPDF2 import PdfReader
from langchain.text_splitter import TokenTextSplitter
from langchain.schema import Document
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from langchain.document_loaders import PyPDFLoader

class cl_process_pdf:
    def __init__(self, file_path):
        self.file_path = file_path
        self.text = ""

    def load_documents(self):
        documents = []
        try:
            loader = PyPDFLoader(self.file_path)
            loaded_docs = loader.load()
            if loaded_docs:
                documents.extend(loaded_docs)
        except Exception as e:
            print(f"Error loading documents: {e}")
        return documents

    def extract_text(self):
        reader = PdfReader(self.file_path)
        for page in reader.pages:
            self.text += page.extract_text() + "\n"
        return self.sanitize_text(self.text)

    def sanitize_text(self, text):
        import re
        sanitized_text = re.sub(r'(?<!\d)0+(\d+)', r'\1', text)
        return sanitized_text

    def create_chunks(self, documents, chunk_size=500, chunk_overlap=50):
        text_splitter = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = []
        for doc in documents:
            doc_chunks = text_splitter.split_text(doc.page_content)
            for chunk in doc_chunks:
                chunks.append(Document(page_content=chunk, metadata=doc.metadata))
        return chunks

    def process_to_graph_documents(self, llm_transformer, chunks):
        """Processes documents into graph documents using the LLM transformer."""
        if not chunks:
            print("No documents to process.")
            return []

        graph_document_list = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(llm_transformer.convert_to_graph_documents, [chunk]) for chunk in chunks]

            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                try:
                    graph_document = future.result()
                    graph_document_list.extend(graph_document)
                    print(f"Chunk {i+1}/{len(chunks)} processed into graph document.")
                except Exception as e:
                    print(f"Error processing chunk {i+1}: {e}")
        return graph_document_list
