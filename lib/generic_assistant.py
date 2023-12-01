from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from dataclasses import dataclass, field
from typing_extensions import Optional, Literal, List

@dataclass
class Company:
    name: str
    type: str
    pronoun: Literal["M"] | Literal["F"]
    services: str

@dataclass
class Mood:
    friendly: Optional[bool] = None
    aggressive: Optional[bool] = None
    polite: Optional[bool] = None
    unpolite: Optional[bool] = None
    kind: Optional[bool] = None
    inclusive: Optional[bool] = None

@dataclass
class OutOfContext:
    allowed: Optional[bool] = None
    pushBack: Optional[bool] = None
    friendly: Optional[bool] = None

@dataclass
class AssistantParams:
    name: str
    company: Company
    playNames: Optional[List[str]] = None
    mood: Optional[Mood] = None
    conversationFlow: List[str] = field(default_factory=list)
    outOfContext: Optional[OutOfContext] = None

def generateNames() -> list:
    return ["João", "José", "Gabriel", "Lucas", "Felipe", "Paulo", "Pedro", "Maria", "Ana", "Luísa", "Alessandra", "Joana", "Cris", "Marcela"]

class GenericAssistant:
    _ready: bool = False
    _assistant = None
    _threads: dict = {}

    def __init__(self, params: AssistantParams | str):
        self._assistant = client.beta.assistants.create(
            model="gpt-3.5-turbo-1106",
            name=params.name,
            instructions=f"""Você é um agente de call center que trabalha em {params.company.type} que se chama {params.company.name} (referia-se sempre no {"masculino" if params.company.pronoun == "M" else "feminino"}) que possui o seguinte serviço: {params.company.services}.
                    Escolha aleatóriamente dentro da lista a seguir o seu nome: {", ".join(params.playNames if params.playNames and params.playNames.length > 0 else generateNames())}. Você usará este nome para se apresentar ao cliente.
                    Voce deve atender as pessoas de maneira {"neutra" if params.mood is None or not params.mood else f"{"cordial" if params.mood.friendly else "agressiva" if params.mood.aggressive else "seca"}, {"formal" if params.mood.polite else "muito informal" if params.mood.unpolite else "sem muita formalidade"}, tratando-as sempre de uma forma {"gentil" if params.mood.kind else "mesquinha"}{" e inclusiva" if params.mood.inclusive else ""}"}.
                    {"\n".join(params.conversationFlow)}
                    {f"Se a conversa parecer estar totalmente fora de contexto, {"continue conversando com o cliente dentro do assunto que o cliente está puxando." if params.outOfContext.allowed else f"expresse isso de forma {"amigável" if params.outOfContext.friendly else "ríspida"} explicando porque a conversa parece estar fora do contexto, {" e trazendo imediatamente de volta ao contexto inicial proposto." if params.outOfContext.pushBack else ""}"}" if params.outOfContext is not None else ""}""",
            tools=[{"type": "code_interpreter"}, {"type": "retrieval"}],
        ) if type(params) is AssistantParams else client.beta.assistants.retrieve(params)
        self._ready = True

    def startNewThread(self):
        if self._ready:
            newThread = client.beta.threads.create()
            self._threads[newThread.id] = newThread
            return newThread
        return None
    
    def addMessage(self, threadId: str, content: str):
        if self._ready:
            message = client.beta.threads.messages.create(threadId, role="user", content=content)
            return message
        return None
    
    def runThread(self, threadId: str):
        if self._ready:
            run = client.beta.threads.runs.create(threadId, assistant_id=self._assistant.id)
            retrieve = client.beta.threads.runs.retrieve(run.id, thread_id=threadId)
            return retrieve
        return None
    
    def getRun(self, threadId: str, runId: str):
        if self._ready:
            run = client.beta.threads.runs.retrieve(runId, thread_id=threadId)
            return run
        return None
    
    def getMessages(self, threadId: str):
        if self._ready:
            messages = client.beta.threads.messages.list(threadId)
            return messages.data
        return None
