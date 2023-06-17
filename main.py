import os
import os

from web_spider import WebsiteSpider
from scrapy.crawler import CrawlerProcess


from langchain.llms import OpenAI
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.docstore.document import Document
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS


def web_scraper(start_url, domain, output_path):
    os.environ['SCRAPY_OUTPUT_PATH'] = output_path
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    })
    process.crawl(WebsiteSpider, start_url=start_url, domain=domain)
    process.start()





start_url = input("Enter the initial URL: ")
domain = input("Enter the domain: ")
output_path = input("Enter the output path: ")



web_scraper(start_url, domain, output_path)



pdf_loader = DirectoryLoader(output_path, glob="**/*.md")
loaders = [pdf_loader]
# documents = []

# for loader in loaders:
#     documents.extend(loader.load())

documents = pdf_loader.load()
print(f"Total number of documents: {len(documents)}")




def chunk_documents(documents):
    splitter = CharacterTextSplitter(separator=" ", chunk_size=1024, chunk_overlap=0)
    chunks = []
    for doc in documents:
        for chunk in splitter.split_text(doc.page_content):
            document = Document(page_content=chunk, metadata=doc.metadata)
            chunks.append(document)
    return chunks

chunked_documents = chunk_documents(documents)
vector_store = FAISS.from_documents(chunked_documents, OpenAIEmbeddings())

def qa_vector_store(chain, question, k=4):
    inputs = {
        "input_documents": vector_store.similarity_search(question, k=k),
        "question": question
    }
    response = chain(inputs, return_only_outputs=True)
    outputs = response["output_text"]
    return outputs


def ask_question(question):
    llm = OpenAI(temperature=0)
    chain = load_qa_with_sources_chain(llm)
    return qa_vector_store(chain, question)




question = input("Enter your question: ")
answer = ask_question(question)
print(answer)



