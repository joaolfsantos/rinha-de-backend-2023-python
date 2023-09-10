from fastapi import HTTPException
from app.dto.pessoa_dto import Pessoa, PessoaCadastroRequest
from app.config.redis import redis_cache


class PessoaService:
    def __init__(self, db):
        self.db = db
        self.redis_cache = redis_cache

    async def buscar_pessoa_por_id(self, id_pessoa: str) -> Pessoa:
        response_redis = await self.redis_cache.get("id-{}".format(id_pessoa))
        if response_redis is not None:
            return Pessoa.from_json(response_redis)

        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    async def buscar_pessoa_por_apelido(self, apelido: str) -> Pessoa:
        response_redis = await self.redis_cache.get("apelido-{}".format(apelido))
        if response_redis is not None:
            return Pessoa.from_json(response_redis)

        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    async def buscar_pessoas_por_termo(self, termo: str) -> list[Pessoa]:
        pessoas = []
        async for pessoa in self.db.rinha_collection.find(
                {"$text": {"$search": termo.lower()}}
        ).limit(50):
            pessoas.append(Pessoa.from_db(pessoa))

        return pessoas

    async def cadastrar_pessoa(
            self, pessoa: PessoaCadastroRequest, novo_id: str
    ):
        pessoa_model = Pessoa(**pessoa.model_dump(), id=novo_id)
        await self.redis_cache.set(
            "id-{}".format(novo_id), pessoa_model.model_dump_json()
        )
        await self.redis_cache.set(
            "apelido-{}".format(pessoa.apelido), pessoa_model.model_dump_json()
        )

        await self.db.rinha_collection.insert_one(pessoa_model.model_dump_db())

    async def contagem_pessoas(self) -> int:
        return await self.db.rinha_collection.count_documents({})
