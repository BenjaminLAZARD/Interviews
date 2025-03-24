from langchain_community.document_transformers import (
    LongContextReorder,
)
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain_core.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain

class shortSummarizer():

    QUERY = "Write a concise summary of the following retranscription of a videocall, in fewer than 60 words  in French"
    STUFF_PROMPT_OVERRIDE = """Given this text extracts:
        -----
        {context}
        -----
        Please answer the following question in French in less than 60 words (hard requirement)
        {query}"""
    
    def __init__(self, docs, api_key) -> None:
        ########################## Extract the appropriate number of tokens from the text
        # As the context is too long for this model (but not to much, we used up to 21k tokens instead
        # of max 16k that's 1.3 times the maximum amount of token, so it's only a 30% overflow)
        # so we need to suppress some items
        retriever = Chroma.from_documents(
            docs, embedding=OpenAIEmbeddings(api_key=api_key)
        ).as_retriever(search_kwargs={"k": 65})

        # Get relevant documents ordered by relevance score
        docs2 = retriever.invoke(shortSummarizer.QUERY)
        reordering = LongContextReorder()

        self.reordered_docs = reordering.transform_documents(docs2)
        
        ########################## Define the chain
        ### Basic chain

        prompt = PromptTemplate(
            template=shortSummarizer.STUFF_PROMPT_OVERRIDE, input_variables=["context", "query"]
        )

        llm = ChatOpenAI(
            openai_api_key=api_key, model_name="gpt-3.5-turbo-16k"
        )  # temperature could be set to 0 for reproductibility
        llm_chain = LLMChain(llm=llm, prompt=prompt)

        ### Stuff Chain on top
        # Exploiting metadata
        document_prompt = PromptTemplate(
            input_variables=["page_content", "metadata"],
            template="""- {speaker}: {page_content}""",
        )

        self.chain = StuffDocumentsChain(
            llm_chain=llm_chain,
            document_prompt=document_prompt,
            document_variable_name="context",
        )

    def run(self)->str:
        return self.chain.run(input_documents=self.reordered_docs, query=shortSummarizer.QUERY)
    

class advancedSummarizer():

    QUERY = "Write a concise summary of the following retranscription of a videocall, in fewer than 60 words  in French"
    STUFF_PROMPT_OVERRIDE = """Given this text extracts:
        -----
        {context}
        -----
        Please answer the following question in French in less than 60 words (hard requirement)
        {query}"""
    
    def __init__(self, docs, api_key, target_len:int=300) -> None:
        self.docs = docs
        prompt_template = """Act as a professional technical meeting minutes writer. 
            Tone: formal
            Format: Technical meeting summary
            Length:  300
            Tasks:
            - highlight action items and owners
            - highlight the agreements
            - Use bullet points (maximum 20)
            {text}
            CONCISE SUMMARY IN FRENCH:"""
        prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
        refine_template = (
            "Your job is to produce a final summary\n"
            "We have provided an existing summary up to a certain point: {existing_answer}\n"
            "We have the opportunity to refine the existing summary"
            "(only if needed) with some more context below.\n"
            "------------\n"
            "{text}\n"
            "------------\n"
            f"Given the new context, refine the original summary in French within {target_len} words: following the format"
            "Title: <title of the meeting>"
            "Participants: <participants>"
            "Discussed: <Discussed-items-with-bullet-points>"
            "Follow-up actions: <a-list-of-follow-up-actions-with-owner-names>"
            f"Conclusion: <a-global-summary-with-maximum-60-words-and-much-less-if-possible>"
            "------------\n"
            "If the context isn't useful, return the original summary. Highlight agreements and follow-up actions and owners in the answer."
            "if there are any participants that correpond to generic speakers such as spk0, spk1, spk2 do not include them in the list of participnts"
            f"The final summary must not exceed 60 words."
        )
        refine_prompt = PromptTemplate(
            input_variables=["existing_answer", "text"],
            template=refine_template,
        )
        llm = ChatOpenAI(
            openai_api_key=api_key, model_name="gpt-3.5-turbo-16k"
        )  # temperature could be set to 0 for reproductibility
        self.chain = load_summarize_chain(
            llm,
            chain_type="refine",
            return_intermediate_steps=True,
            question_prompt=prompt,
            refine_prompt=refine_prompt,
        )

    def run(self)->str:
        return self.chain({"input_documents": self.docs}, return_only_outputs=True)["output_text"]
