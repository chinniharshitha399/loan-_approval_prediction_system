"""
utils/chroma_kb.py — Build and query ChromaDB knowledge base
for the AI chatbot to answer loan / finance questions.
"""
import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

LOAN_KNOWLEDGE = [
    {
        "id": "loan_types",
        "text": (
            "Types of loans include personal loans, home loans (mortgages), "
            "auto loans, student loans, business loans, and payday loans. "
            "Personal loans are unsecured (no collateral), while home and auto "
            "loans are secured by the property or vehicle."
        ),
    },
    {
        "id": "credit_score",
        "text": (
            "A credit score is a number between 300 and 850 that represents "
            "your creditworthiness. Scores above 750 are excellent, 700–749 are good, "
            "650–699 are fair, and below 650 are poor. Lenders use credit scores "
            "to decide loan approval and interest rates."
        ),
    },
    {
        "id": "loan_approval_factors",
        "text": (
            "Key factors for loan approval: 1) Credit score — higher is better. "
            "2) Debt-to-income ratio (DTI) — lenders prefer below 36%. "
            "3) Employment stability — steady job history is preferred. "
            "4) Loan amount vs income — borrow only what you can repay. "
            "5) Collateral — assets that secure a loan reduce lender risk."
        ),
    },
    {
        "id": "interest_rates",
        "text": (
            "Interest rate is the cost of borrowing money, expressed as a percentage. "
            "Fixed rates stay the same over the loan term. Variable rates fluctuate "
            "with market conditions. Personal loans typically have higher rates "
            "(6–36%) than mortgages (3–7%)."
        ),
    },
    {
        "id": "loan_rejection",
        "text": (
            "Common reasons for loan rejection: low credit score, too much existing debt, "
            "unstable employment, insufficient income, incomplete application, "
            "or applying for too large an amount. To improve approval chances, "
            "pay off debt, improve credit score, and increase income."
        ),
    },
    {
        "id": "home_ownership",
        "text": (
            "Home ownership status affects loan applications. Homeowners may get "
            "better rates since they have an asset. Renters are considered higher risk. "
            "Mortgage holders show they can manage long-term debt responsibly."
        ),
    },
    {
        "id": "loan_grade",
        "text": (
            "Loan grades (A through G) represent the risk level of a loan. "
            "Grade A is the safest — lowest risk, lowest interest. "
            "Grade G is the riskiest — highest default chance, highest interest. "
            "Grades are assigned based on creditworthiness of the borrower."
        ),
    },
    {
        "id": "default",
        "text": (
            "A loan default occurs when a borrower fails to make required payments. "
            "Defaulting damages credit score severely, can result in legal action, "
            "wage garnishment, and asset repossession. It stays on credit report for 7 years."
        ),
    },
    {
        "id": "debt_to_income",
        "text": (
            "Debt-to-income (DTI) ratio = total monthly debt / gross monthly income. "
            "A DTI below 36% is ideal for loan approval. Above 43% is a red flag "
            "for most lenders. High DTI means you're over-leveraged."
        ),
    },
    {
        "id": "loan_intent",
        "text": (
            "Common loan purposes include: education (student loans), home improvement, "
            "medical expenses, debt consolidation, business startup, personal/venture. "
            "Lenders may offer different terms based on loan purpose."
        ),
    },
    {
        "id": "improving_approval_chances",
        "text": (
            "To improve loan approval chances: 1) Check and fix credit report errors. "
            "2) Pay down existing debts. 3) Save for a larger down payment. "
            "4) Get a co-signer with strong credit. 5) Apply for the right loan amount — "
            "not too large. 6) Maintain stable employment."
        ),
    },
    {
        "id": "ml_model_explanation",
        "text": (
            "This app uses machine learning — specifically Random Forest, XGBoost, "
            "and Gradient Boosting — to predict loan approval. The model was trained "
            "on 32,000+ real credit risk records. It evaluates 11 features including "
            "age, income, employment length, loan amount, credit history, and more."
        ),
    },
{
        "id": "bank_recommender_page",
        "text": (
            "The Bank Recommender page lets you enter your loan profile — amount, income, "
            "loan grade, risk score, prior default, and preferred tenure — and instantly "
            "see which Indian banks will approve your loan. It shows SBI, HDFC, ICICI, "
            "Axis Bank, Kotak, Bajaj Finserv, Tata Capital, Muthoot, and Manappuram. "
            "For each eligible bank it shows interest rate range, EMI estimate, processing "
            "fee, turnaround time, and a direct Apply button. A side-by-side comparison "
            "table and interest rate bar chart are also shown."
        ),
    },
    {
        "id": "finance_news_page",
        "text": (
            "The Finance News and Tips page has 4 tabs. Tab 1 AI Finance Tips lets you "
            "click topics like credit score tips, home loan guide, personal loan tips, "
            "and debt reduction to get instant Groq AI-powered advice. Tab 2 is a full "
            "EMI Calculator where you enter loan amount, interest rate, and tenure to get "
            "monthly EMI, total interest, amortization schedule, and tenure comparison chart. "
            "Tab 3 is a Credit Score Guide with score bands from 300 to 900, a credit score "
            "simulator where you check actions and see projected score changes, and a "
            "personalized 90-day improvement plan. Tab 4 is Ask Finance AI where you can "
            "type any finance question and get an instant AI answer."
        ),
    },
    {
        "id": "emi_calculator",
        "text": (
            "EMI stands for Equated Monthly Installment. It is calculated using the formula: "
            "EMI = P × r × (1+r)^n / ((1+r)^n - 1) where P is principal, r is monthly "
            "interest rate, and n is number of months. Lower tenure means higher EMI but "
            "less total interest. Higher tenure means lower EMI but more total interest paid."
        ),
    },
    {
        "id": "indian_banks",
        "text": (
            "Major Indian banks for personal loans: SBI offers 8.5-12% for government employees. "
            "HDFC Bank offers 9-14% with fast digital approval. ICICI Bank offers 9.5-15% "
            "good for self-employed. Axis Bank offers 10-15.5% with flexible repayment. "
            "Kotak Mahindra offers 10.5-17%. Bajaj Finserv NBFC offers 12-22% with 24hr disbursal. "
            "Tata Capital NBFC offers 13-24%. Muthoot Finance offers gold loans at 16-28%. "
            "Manappuram Finance is a last resort NBFC at 18-30%."
        ),
    },
]


def get_chroma_client():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client


def build_knowledge_base():
    """Build the ChromaDB collection from LOAN_KNOWLEDGE. Run once."""
    client = get_chroma_client()

    ef = embedding_functions.DefaultEmbeddingFunction()

    collection = client.get_or_create_collection(
        name="loan_knowledge",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    existing_ids = collection.get()["ids"]

    docs_to_add = []
    ids_to_add  = []
    for item in LOAN_KNOWLEDGE:
        if item["id"] not in existing_ids:
            docs_to_add.append(item["text"])
            ids_to_add.append(item["id"])

    if docs_to_add:
        collection.add(documents=docs_to_add, ids=ids_to_add)
        print(f"✅ ChromaDB: Added {len(docs_to_add)} knowledge entries.")
    else:
        print("✅ ChromaDB: Knowledge base already up to date.")

    return collection


def query_knowledge(query: str, n_results: int = 3) -> str:
    """Return top-n relevant knowledge snippets for a query."""
    try:
        client = get_chroma_client()
        ef     = embedding_functions.DefaultEmbeddingFunction()
        collection = client.get_collection(
            name="loan_knowledge", embedding_function=ef
        )
        results = collection.query(query_texts=[query], n_results=n_results)
        docs = results["documents"][0]
        return "\n\n".join(docs)
    except Exception:
        return ""
