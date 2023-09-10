from fastapi import FastAPI, Response, Request, status, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.dto.pessoa_dto import PessoaCadastroRequest, PessoaCadastroResponse, Pessoa
from app.service.pessoa_service import PessoaService
from app.config.db import get_db
import uuid
import uvicorn
from fastapi import BackgroundTasks

app = FastAPI(title="FastAPI Rinha de Backend 2023", version="0.0.1")


@app.on_event("startup")
async def startup_event():
    db = await get_db()
    app.state.pessoa_service = PessoaService(db)
    # TODO: carregar dados do banco de dados para a memória (cache)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exec_errors = exc.errors()
    type_erros = list(
        filter(
            lambda x: (x["type"] == "string_type" or x["type"] == "list_type")
                      and x["input"] is not None,
            exec_errors,
        )
    )

    if len(type_erros) > 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({"detail": "Invalid type", "body": exc.body}),
        )

    msg_erros = list(map(lambda x: x["msg"], exec_errors))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": msg_erros, "body": exc.body}),
    )


@app.get("/")
async def status_api():
    return {"status": "ok"}


@app.get("/pessoas/{id_pessoa}")
async def buscar_pessoa_por_id(
        id_pessoa: str,
) -> Pessoa:
    return await app.state.pessoa_service.buscar_pessoa_por_id(id_pessoa)


@app.get("/pessoas")
async def buscar_pessoas_por_termo(t: Optional[str] = None) -> list[Pessoa]:
    if t is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O parâmetro 't' é obrigatório",
        )
    return await app.state.pessoa_service.buscar_pessoas_por_termo(t)


@app.post("/pessoas")
async def cadastrar_pessoa(
        pessoa: PessoaCadastroRequest,
        response: Response,
        background_tasks: BackgroundTasks,
) -> PessoaCadastroResponse:
    pessoa_existe = False
    try:
        await app.state.pessoa_service.buscar_pessoa_por_apelido(pessoa.apelido)
        pessoa_existe = True
    except Exception as _ex:
        pass

    if pessoa_existe:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Já existe uma pessoa com esse apelido",
        )

    novo_id = str(uuid.uuid4())
    response.headers["Location"] = f"/pessoas/{novo_id}"
    response.status_code = status.HTTP_201_CREATED
    background_tasks.add_task(
        app.state.pessoa_service.cadastrar_pessoa, pessoa, novo_id
    )
    return PessoaCadastroResponse(status="ok")


@app.get("/contagem-pessoas")
async def contagem_pessoas() -> str:
    total = await app.state.pessoa_service.contagem_pessoas()
    return f"{total}"


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
