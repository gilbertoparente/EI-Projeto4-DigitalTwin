from sqlalchemy import Column, Integer, Float, String, Boolean, JSON, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    attack_type    = Column(String)
    mfa_enabled    = Column(Boolean)
    training_level = Column(Float)
    segmentation   = Column(Float)
    n_agents       = Column(Integer)
    config         = Column(JSON)   # config completo para reprodutibilidade


class TickResult(Base):
    __tablename__ = "tick_results"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    run_id           = Column(Integer, index=True)
    tick             = Column(Integer)
    opened           = Column(Integer, default=0)
    clicked          = Column(Integer, default=0)
    infected         = Column(Integer, default=0)
    total_compromised = Column(Integer, default=0)
    total_agents     = Column(Integer, default=0)
    created_at       = Column(DateTime, default=datetime.utcnow)
