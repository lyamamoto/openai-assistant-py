from lib.generic_assistant import Company, GenericAssistant, Mood, OutOfContext, ToolsFunction, getAssistant
from typing import List

import math
class Loan:
    notional: float
    interestRate: float
    installments: int

    @property
    def monthlyInterestRate(self):
        return math.pow(self.interestRate, 1 / 12)

    def __init__(self, notional: float, interest: float, installments: int):
        self.notional = notional
        self.interestRate = interest
        self.installments = installments

    def getInstallmentValue(self) -> float:
        return self.notional * self.monthlyInterestRate * math.pow(1 + self.monthlyInterestRate, self.installments) / (math.pow(1 + self.monthlyInterestRate, self.installments) - 1)

    def getTotalRepayment(self) -> float:
        return self.getInstallmentValue() * self.installments

    def getDuration(self) -> float:
        return math.log(self.getTotalRepayment() / self.notional) / math.log(1 + self.interestRate) * 12

class CreditAssistant(GenericAssistant):
    def __init__(self, name: str, companyName: str):
        assistant = getAssistant(
            name,
            company=Company(
                name=companyName,
                type="empresa de crédito online",
                pronoun="F",
                services="realizar empréstimos para pessoas de baixa renda"
            ),
            mood=Mood(
                friendly=True,
                polite=False,
                kind=True,
                inclusive=True
            ),
            conversationFlow=[
                "O fluxo de atendimento é:"
                f"1. Em uma ÚNICA mensagem, se apresente falando seu nome, dizendo que fala da {companyName}, que a {companyName} oferece empréstimo de até R$ 2500 e pergunte se o cliente gostaria da fazer uma cotação. Espere o cliente responder.",
                "2. Se o cliente disser que sim, pergunte o nome completo do cliente. Espere o cliente responder.",
                "3. Pergunte o e-mail do cliente. Espere o cliente responder.",
                "4. Pergunte o CPF do cliente. Espere o cliente responder.",
                "5. Confirme com o cliente se os dados informados (nome completo, e-mail e cpf) estão corretos. Espere o cliente responder.",
                "6. Se o cliente disser que sim, rode o motor de crédito para coletar o score de crédito do cliente e conseguir responder o cliente com as opçoes de valor do empréstimo aprovadas. Apresente as opções espaçadas por quebra de linha (cada oferta em uma linha) e no seguinte formato (exemplo): R$ 750 (em 6 parcelas de R$ 671,08).",
                "A cada interação com o cliente, espere o cliente responder antes de enviar a próxima mensagem e só mande UMA mensagem por vez."
            ],
            outOfContext=OutOfContext(
                allowed=False,
                pushBack=True,
                friendly=True
            ),
            functions=[
                ToolsFunction(
                    function={
                        "name": "getCreditScore",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Nome completo do cliente"
                                },
                                "email": {
                                    "type": "string",
                                    "description": "E-mail do cliente"
                                },
                                "cpf": {
                                    "type": "string",
                                    "description": "CPF do cliente"
                                }
                            },
                            "required": ["name", "email", "cpf"],
                            "description": "Dados do cliente para consulta de score de crédito"
                        }
                    },
                    resolver=self.getCreditScore
                )
            ]
        )
        GenericAssistant.__init__(self, assistant._assistant, assistant._toolResolvers)

    def getCreditScore(self, name: str, email: str, cpf: str) -> List[int]:
        notionals = [100, 150, 250, 500, 750, 1500, 2500]
        installments = [1, 1, 2, 4, 6, 6, 6]

        import random, math
        random.seed()
        last = math.ceil(random.random() * len(notionals))
        loans = [Loan(notionals[i], 0.199, installments[i]) for i in range(0, last)]

        return [{
            "notional": f"R${loan.notional}",
            "installments": loan.installments,
            "interestRate": f"{loan.interestRate * 100}%",
            "installmentValue": f"R${loan.getInstallmentValue()}",
            "totalRepayment": f"R${loan.getTotalRepayment()}",
            "duration": loan.getDuration()
        } for loan in loans]
    
    def getCounterOffer(self, bestLoan: Loan) -> Loan:
        return Loan(bestLoan.notional, bestLoan.interestRate + 0.01, bestLoan.installments)