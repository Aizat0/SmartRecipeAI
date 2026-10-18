from pathlib import Path
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore

BASE_DIR = Path(__file__).resolve().parent.parent

loader = TextLoader(str(BASE_DIR / 'chain' / 'base_knowledge.txt'), encoding='utf-8')
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=100
)

chunks = text_splitter.split_documents(documents)

embeddings = OllamaEmbeddings(
    model='nomic-embed-text'
)

vectors_store = InMemoryVectorStore.from_documents(chunks, embeddings)

prompt = ChatPromptTemplate([
    (
        'system',
        "Ты умный кулинарный помощник SmartRecipe AI. "
        "Твоя задача — помогать пользователям выбирать рецепты и готовить блюда. "
        "Сначала изучи информацию из базы знаний: {base_knowledge}. "
        "Отвечай только на основании базы знаний. "
        "Если пользователь перечислил ингредиенты, найди подходящие рецепты. "
        "Если пользователь указал время приготовления, учитывай его. "
        "Предлагай максимум 3 рецепта. "
        "Для каждого рецепта укажи название, ингредиенты и время приготовления. "
        "Если каких-то ингредиентов не хватает, обязательно сообщи об этом. "
        "Если пользователь спрашивает, как приготовить блюдо, объясни пошагово. "
        "Если пользователь спрашивает о замене ингредиента, используй советы из базы знаний. "
        "Не придумывай новые рецепты и ингредиенты. "
        "Если подходящего рецепта нет, сообщи об этом. "
        "Отвечай на русском языке, понятно и вежливо."
    ),
    (
        'human',
        '{content}'
    )
])

model = ChatOllama(
    model='llama3.2:latest',
    temperature=0
)

chain = prompt | model | StrOutputParser()


def search_answer(question: str):
    if not question.strip():
        return 'Напишите ваш вопрос.'
    new_documents = vectors_store.similarity_search(question, k=5)
    base_knowledge = ''
    for document in new_documents:
        base_knowledge += document.page_content + '\n'
    final_answer = chain.invoke({
        'content': question,
        'base_knowledge': base_knowledge
    })
    return final_answer.strip()

def recommend_recipe(ingredients: str):
    if not ingredients.strip():
        return 'Укажите продукты, которые у вас есть.'

    question = 'Какие блюда можно приготовить из следующих ингредиентов: ' + ingredients

    return search_answer(question)
