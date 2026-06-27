from trifecta_guard.adapters.langgraph import LangGraphGuardMiddleware
from trifecta_guard.middleware import GuardViolationError, TrifectaMiddleware
from trifecta_guard.models import Capability, ToolSpec
from trifecta_guard.taint_engine import TaintEngine


def main() -> None:
    tools = {
        "gmail_read": ToolSpec(name="gmail_read", capabilities={Capability.READS_PRIVATE_DATA}),
        "web_fetch": ToolSpec(name="web_fetch", capabilities={Capability.SEES_UNTRUSTED_CONTENT}),
        "http_post": ToolSpec(name="http_post", capabilities={Capability.CAN_EXFILTRATE}),
    }
    engine = TaintEngine()
    middleware = TrifectaMiddleware(engine=engine)
    adapter = LangGraphGuardMiddleware(middleware=middleware, tool_specs=tools)

    session_id = "demo-session"
    adapter.before_tool(session_id, "gmail_read", {})
    adapter.after_tool(session_id, "gmail_read", {})
    adapter.before_tool(session_id, "web_fetch", {})
    adapter.after_tool(session_id, "web_fetch", {})

    try:
        adapter.before_tool(session_id, "http_post", {"body": "leak"})
        adapter.after_tool(session_id, "http_post", {"body": "leak"})
    except GuardViolationError as exc:
        print(f"blocked: {exc}")


if __name__ == "__main__":
    main()
