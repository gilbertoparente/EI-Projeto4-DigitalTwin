from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base, SimulationRun, TickResult

DATABASE_URL = "sqlite:///./digital_twin.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_run(db: Session, config: dict) -> int:
    defense = config.get("defense", {})
    attack  = config.get("attack", {})
    org     = config.get("organization", {})
    n_agents = sum(
        len(dept.get("agents", []))
        for dept in org.get("departments", [])
    )
    run = SimulationRun(
        attack_type=attack.get("type", "Phishing"),
        mfa_enabled=defense.get("mfa", False),
        training_level=defense.get("training", 0.0),
        segmentation=defense.get("segmentation", 0.5),
        n_agents=n_agents,
        config=config,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run.id


def save_tick(db: Session, run_id: int, result: dict):
    tick_result = TickResult(
        run_id=run_id,
        tick=result["tick"],
        opened=result["result"].get("opened", 0),
        clicked=result["result"].get("clicked", 0),
        infected=result["result"].get("infected", 0),
        total_compromised=result.get("total_compromised", 0),
        total_agents=result.get("total_agents", 0),
    )
    db.add(tick_result)
    db.commit()


def get_run_history(db: Session, run_id: int) -> list:
    return (
        db.query(TickResult)
        .filter(TickResult.run_id == run_id)
        .order_by(TickResult.tick)
        .all()
    )
