from trifecta_guard.middleware import GuardViolationError, ToolExecutionContext, TrifectaMiddleware
from trifecta_guard.models import Capability, GuardAction, ToolSpec
from trifecta_guard.taint_engine import TaintEngine


def test_engine_blocks_on_third_capability() -> None:
    engine = TaintEngine()
    session_id = "s1"

    first = ToolSpec(name="private", capabilities={Capability.READS_PRIVATE_DATA})
    second = ToolSpec(name="web", capabilities={Capability.SEES_UNTRUSTED_CONTENT})
    third = ToolSpec(name="send", capabilities={Capability.CAN_EXFILTRATE})

    assert engine.evaluate_tool_call(session_id, first).action == GuardAction.ALLOW
    engine.commit_tool_call(session_id, first)
    assert engine.evaluate_tool_call(session_id, second).action == GuardAction.ALLOW
    engine.commit_tool_call(session_id, second)
    assert engine.evaluate_tool_call(session_id, third).action == GuardAction.BLOCK


def test_middleware_raises_on_violation() -> None:
    middleware = TrifectaMiddleware(engine=TaintEngine())
    session_id = "s2"
    executor = lambda _ctx: "ok"

    middleware.run_guarded(
        ToolExecutionContext(
            session_id=session_id,
            tool=ToolSpec(name="private", capabilities={Capability.READS_PRIVATE_DATA}),
            args={},
        ),
        executor,
    )
    middleware.run_guarded(
        ToolExecutionContext(
            session_id=session_id,
            tool=ToolSpec(name="web", capabilities={Capability.SEES_UNTRUSTED_CONTENT}),
            args={},
        ),
        executor,
    )

    try:
        middleware.run_guarded(
            ToolExecutionContext(
                session_id=session_id,
                tool=ToolSpec(name="send", capabilities={Capability.CAN_EXFILTRATE}),
                args={},
            ),
            executor,
        )
    except GuardViolationError:
        return
    raise AssertionError("Expected GuardViolationError")


def test_run_guarded_commits_each_tool_once() -> None:
    engine = TaintEngine()
    middleware = TrifectaMiddleware(engine=engine)
    session_id = "s3"
    executor = lambda _ctx: "ok"

    middleware.run_guarded(
        ToolExecutionContext(
            session_id=session_id,
            tool=ToolSpec(name="private", capabilities={Capability.READS_PRIVATE_DATA}),
            args={},
        ),
        executor,
    )
    middleware.run_guarded(
        ToolExecutionContext(
            session_id=session_id,
            tool=ToolSpec(name="web", capabilities={Capability.SEES_UNTRUSTED_CONTENT}),
            args={},
        ),
        executor,
    )

    state = engine.get_state(session_id)
    assert len(state.trace) == 2
    assert [call.tool_name for call in state.trace] == ["private", "web"]
