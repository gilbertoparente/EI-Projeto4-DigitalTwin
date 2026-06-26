from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id                = Column(Integer, primary_key=True, autoincrement=True)
    timestamp         = Column(DateTime, default=datetime.utcnow)
    experiment_label  = Column(String(120), default="Live System Run")
    attack_type       = Column(String(60))
    total_compromised = Column(Integer, default=0)
    num_agents        = Column(Integer, default=0)
    mfa_enabled       = Column(Boolean, default=False)
    training_level    = Column(Float, default=0.0)
    segmentation_level= Column(Float, default=0.5)

    config  = relationship("SimulationConfig",  back_populates="run", uselist=False, cascade="all, delete-orphan")
    graph   = relationship("SimulationGraph",   back_populates="run", uselist=False, cascade="all, delete-orphan")
    steps   = relationship("SimulationStep",    back_populates="run", cascade="all, delete-orphan")


class SimulationConfig(Base):
    __tablename__ = "simulation_configs"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    run_id     = Column(Integer, ForeignKey("simulation_runs.id"), unique=True)
    config_json= Column(Text)

    run = relationship("SimulationRun", back_populates="config")


class SimulationGraph(Base):
    __tablename__ = "simulation_graphs"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    run_id     = Column(Integer, ForeignKey("simulation_runs.id"), unique=True)
    graph_json = Column(Text)

    run = relationship("SimulationRun", back_populates="graph")


class SimulationStep(Base):
    __tablename__ = "simulation_steps"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    run_id   = Column(Integer, ForeignKey("simulation_runs.id"))
    tick     = Column(Integer)
    opened   = Column(Integer, default=0)
    clicked  = Column(Integer, default=0)
    infected = Column(Integer, default=0)
    total_compromised = Column(Integer, default=0)

    run = relationship("SimulationRun", back_populates="steps")
