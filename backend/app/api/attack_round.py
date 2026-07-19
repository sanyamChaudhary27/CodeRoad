"""HTTP endpoints for the Adversarial Test Arena."""

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.concurrency import run_in_threadpool

from ..core.security import get_current_player
from ..schemas.attack_round_schema import AttackProblem, AttackRoundRequest, AttackRoundResponse
from ..services.attack_problem_registry import PROBLEMS
from ..services.attack_round_service import AttackRoundService
from ..services.judge_service import CodeExecutionUnavailable

router = APIRouter()


@router.get("/problems", response_model=list[AttackProblem])
async def list_attack_problems(
    current_user: dict = Depends(get_current_player),
):
    del current_user
    return [contract.public for contract in PROBLEMS.values()]


@router.post("/analyze", response_model=AttackRoundResponse)
async def analyze_attack_round(
    request: AttackRoundRequest,
    current_user: dict = Depends(get_current_player),
):
    del current_user
    try:
        return await run_in_threadpool(AttackRoundService().analyze, request)
    except CodeExecutionUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
