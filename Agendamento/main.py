from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker


# =========================
# APP
# =========================
app = FastAPI()

# =========================
# CORS (frontend liberado)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# DATABASE
# =========================
engine = create_engine(
    "sqlite:///agendamento.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# =========================
# MODELS
# =========================
class BarbeiroDB(Base):
    __tablename__ = "barbeiros"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)


class ServiceDB(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    duracao_minutos = Column(Integer, nullable=False)

    barbeiro_id = Column(Integer, ForeignKey("barbeiros.id"))


class AgendamentoDB(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String, nullable=False)

    barbeiro_id = Column(Integer, ForeignKey("barbeiros.id"))
    service_id = Column(Integer, ForeignKey("services.id"))

    starts_at = Column(String, nullable=False)
    ends_at = Column(String, nullable=False)

    status = Column(String, nullable=False, default="SCHEDULED")


Base.metadata.create_all(bind=engine)


# =========================
# SCHEMAS
# =========================
class NovoBarbeiro(BaseModel):
    nome: str


class NovoServico(BaseModel):
    nome: str
    duracao_minutos: int
    barbeiro_id: int


class NovoAgendamento(BaseModel):
    cliente: str
    horario: datetime
    service_id: int


# =========================
# ROTAS
# =========================
@app.get("/")
def home():
    return {"mensagem": "Sistema Barbearia rodando 💈"}


# -------------------------
# BARBEIROS
# -------------------------
@app.post("/barbeiros")
def criar_barbeiro(dados: NovoBarbeiro):
    db = SessionLocal()

    novo = BarbeiroDB(nome=dados.nome)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    db.close()

    return {"ok": True, "barbeiro": {"id": novo.id, "nome": novo.nome}}


@app.get("/barbeiros")
def listar_barbeiros():
    db = SessionLocal()
    dados = db.query(BarbeiroDB).all()
    db.close()

    return [{"id": b.id, "nome": b.nome} for b in dados]


@app.delete("/barbeiros/{barbeiro_id}")
def excluir_barbeiro(barbeiro_id: int):
    db = SessionLocal()

    barbeiro = db.query(BarbeiroDB).filter(BarbeiroDB.id == barbeiro_id).first()

    if not barbeiro:
        db.close()
        raise HTTPException(status_code=404, detail="Barbeiro não encontrado")

    # Não deixar excluir se tiver agendamentos
    existe_agendamento = db.query(AgendamentoDB).filter(
        AgendamentoDB.barbeiro_id == barbeiro_id
    ).first()

    if existe_agendamento:
        db.close()
        return {"erro": "Não pode excluir barbeiro com agendamentos ativos ❌"}

    db.delete(barbeiro)
    db.commit()
    db.close()

    return {"ok": True, "mensagem": "Barbeiro excluído com sucesso ✅"}


# -------------------------
# SERVIÇOS
# -------------------------
@app.post("/services")
def criar_servico(dados: NovoServico):
    db = SessionLocal()

    barbeiro = db.query(BarbeiroDB).filter(BarbeiroDB.id == dados.barbeiro_id).first()
    if not barbeiro:
        db.close()
        raise HTTPException(status_code=404, detail="Barbeiro não encontrado")

    novo = ServiceDB(
        nome=dados.nome,
        duracao_minutos=dados.duracao_minutos,
        barbeiro_id=dados.barbeiro_id
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)
    db.close()

    return {"ok": True, "service": {"id": novo.id, "nome": novo.nome}}


@app.get("/services")
def listar_servicos():
    db = SessionLocal()
    dados = db.query(ServiceDB).all()
    db.close()

    return [
        {
            "id": s.id,
            "nome": s.nome,
            "duracao_minutos": s.duracao_minutos,
            "barbeiro_id": s.barbeiro_id
        }
        for s in dados
    ]


# -------------------------
# AGENDAMENTOS
# -------------------------
@app.post("/agendar")
def criar_agendamento(dados: NovoAgendamento):
    db = SessionLocal()

    servico = db.query(ServiceDB).filter(ServiceDB.id == dados.service_id).first()
    if not servico:
        db.close()
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    barbeiro_id = servico.barbeiro_id

    inicio = dados.horario
    fim = inicio + timedelta(minutes=servico.duracao_minutos)

    ativos = db.query(AgendamentoDB).filter(
        AgendamentoDB.status == "SCHEDULED",
        AgendamentoDB.barbeiro_id == barbeiro_id
    ).all()

    for a in ativos:
        existente_inicio = datetime.fromisoformat(a.starts_at)
        existente_fim = datetime.fromisoformat(a.ends_at)

        if (inicio < existente_fim) and (fim > existente_inicio):
            db.close()
            return {"erro": "Esse barbeiro já tem cliente nesse horário 😢"}

    novo = AgendamentoDB(
        cliente=dados.cliente,
        barbeiro_id=barbeiro_id,
        service_id=servico.id,
        starts_at=inicio.isoformat(),
        ends_at=fim.isoformat(),
        status="SCHEDULED"
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)
    db.close()

    return {"ok": True, "agendado": {"id": novo.id, "cliente": novo.cliente}}


@app.get("/agendamentos")
def listar_agendamentos():
    db = SessionLocal()
    dados = db.query(AgendamentoDB).all()
    db.close()

    return [
        {
            "id": a.id,
            "cliente": a.cliente,
            "barbeiro_id": a.barbeiro_id,
            "service_id": a.service_id,
            "starts_at": a.starts_at,
            "ends_at": a.ends_at,
            "status": a.status
        }
        for a in dados
    ]


@app.delete("/agendamentos/{agendamento_id}")
def excluir_agendamento(agendamento_id: int):
    db = SessionLocal()

    ag = db.query(AgendamentoDB).filter(AgendamentoDB.id == agendamento_id).first()

    if not ag:
        db.close()
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    db.delete(ag)
    db.commit()
    db.close()

    return {"ok": True, "mensagem": "Agendamento excluído com sucesso ✅"}
