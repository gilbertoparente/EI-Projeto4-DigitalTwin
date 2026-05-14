from pydantic import BaseModel, Field

class SimulacaoRequest(BaseModel):
    n_agentes: int = Field(default=150, ge=10, le=500)
    prob_formacao: float = Field(default=0.0, ge=0.0, le=1.0) # 0 a 100%
    mfa_ativo: bool = Field(default=False)
    tipo_ataque: str = Field(default="massivo") # "massivo" ou "spear"