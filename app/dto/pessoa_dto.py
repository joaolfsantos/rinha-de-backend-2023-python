import json
from pydantic import BaseModel, Field, constr
from typing import Optional, List


class PessoaCadastroRequest(BaseModel):
    apelido: str = Field(max_length=32)
    nome: str = Field(max_length=100)
    nascimento: str = Field(max_length=10, pattern="^\d{4}-\d{2}-\d{2}$")
    stack: Optional[List[constr(max_length=32)]]


class PessoaCadastroResponse(BaseModel):
    status: str = Field(default="ok")


class Pessoa(BaseModel):
    id: str
    apelido: str = Field(max_length=32)
    nome: str = Field(max_length=100)
    nascimento: str = Field(max_length=10, pattern="^\d{4}-\d{2}-\d{2}$")
    stack: Optional[List[constr(max_length=32)]]

    @staticmethod
    def from_json(json_data: str):
        return Pessoa(**json.loads(json_data))

    def model_dump_db(self):
        return {
            "_id": self.id,
            "apelido": self.apelido,
            "nome": self.nome,
            "nascimento": self.nascimento,
            "stack": self.stack,
            "buscar_like": f"{self.apelido.lower()} {self.nome.lower()} {' '.join(list(map(lambda x: x.lower(), self.stack))) if self.stack else ''}",
        }

    @staticmethod
    def from_db(db_data: dict):
        return Pessoa(
            id=str(db_data["_id"]),
            apelido=db_data["apelido"],
            nome=db_data["nome"],
            nascimento=db_data["nascimento"],
            stack=db_data.get("stack", None),
        )
