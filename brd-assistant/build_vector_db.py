# Step 3b: Load the BRD and split it into chunks (one per section)
import shutil
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter

# 1. Load the BRD file
BRD_PATH = Path(__file__).parent / "data" / "shopeasy-brd.md"
brd_text = BRD_PATH.read_text(encoding="utf-8")

# 2. Split by markdown headings: "#" = title, "##" = section (Login, Cart, ...)
splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "title"), ("##", "section")]
)
chunks = splitter.split_text(brd_text)

# 3. Show what we got
print(f"Total chunks: {len(chunks)}\n")
for i, chunk in enumerate(chunks, start=1):
    print(f"--- Chunk {i} ---")
    print("Section :", chunk.metadata.get("section"))
    print("Preview :", chunk.page_content[:80], "...")
    print()


    # 4. Embed the chunks and store them in ChromaDB
DB_DIR = Path(__file__).parent / "chroma_db"

if DB_DIR.exists():          # start fresh each run (avoids duplicate chunks)
    shutil.rmtree(DB_DIR)

embeddings = OllamaEmbeddings(model="nomic-embed-text")

vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=str(DB_DIR),
    collection_name="shopeasy_brd",
)
print(f"Stored {len(chunks)} chunks in ChromaDB at: {DB_DIR}\n")

# 5. Quick test: search by MEANING (not exact words)
question = "How long is a user blocked after too many wrong passwords?"
results = vector_db.similarity_search_with_score(question, k=2)

print("Question:", question)
for doc, score in results:
    print(f"  -> {doc.metadata['section']}  (distance: {score:.3f})")