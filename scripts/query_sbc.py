import sys

from rag.sbc_rag import SBCRetriever


query = " ".join(sys.argv[1:]).strip()

if not query:
    raise SystemExit(
        'Usage: python scripts/query_sbc.py "your question"'
    )

retriever = SBCRetriever()
results = retriever.search(query)

if not results:
    print(
        "No SBC evidence available.\n"
        "Put official SBC files in data/sbc and run "
        "python scripts/build_sbc_index.py"
    )
    raise SystemExit(0)

for result in results:
    print("=" * 88)
    print("SOURCE:", result["source"])
    print("CHUNK:", result["chunk"])
    print("SCORE:", f"{result['score']:.4f}")
    print("-" * 88)
    print(result["text"])
