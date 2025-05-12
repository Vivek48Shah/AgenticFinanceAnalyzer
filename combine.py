
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

def combine_outputs(summaries):
    # Organize by agent type
    section_map = {
        "financial": None,
        "sentiment": None,
        "valuation": None,
        "catalyst": [],
        "risk": None
    }

    for s in summaries:
        t = s.get("type", "unknown")
        if t == "catalyst":
        # Support both direct list or {"events": [...], "warnings": [...]}
            summary = s.get("summary")
            if isinstance(summary, dict):
                section_map["catalyst"] = summary
            elif isinstance(summary, list):
                section_map["catalyst"] = {"events": summary, "warnings": []}
            else:
                section_map["catalyst"] = {"events": [], "warnings": []}
        elif t in section_map:

            summary = s.get("summary", {})
            if t == "financial" and isinstance(summary, dict) and "financials" in summary:
                section_map[t] = summary["financials"]  # unpack financials key
            else:
                section_map[t] = summary

    # Markdown builder
    lines = []
    lines.append(f"## Investment Memo - AI Generated")

    #  Catalysts
    if section_map["catalyst"]:
        lines.append("\n### Catalysts")
        catalyst_data = section_map.get("catalyst", {})
        events = catalyst_data.get("events", [])
        for cat in events: 
            event = cat.get("event", "Unnamed event")
            date = cat.get("date", "unknown")
            lines.append(f"- [ ] {event} ({date})\n")
        warnings = catalyst_data.get("warnings", [])
        if warnings:
            lines.append( "\n### ⚠️ Warnings\n")
            for warn in warnings:
                lines.append( f"- {warn}\n")

    #  Financial Summary
    if section_map["financial"]:
        lines.append("\n### Financial Snapshot")
        try:
            fin = eval(section_map["financial"]) if isinstance(section_map["financial"], str) else section_map["financial"]
            if isinstance(fin, dict):
                if "revenue" in fin:
                    rev = fin["revenue"]
                    lines.append(f"- **Revenue**: ${rev.get('value')}B ({rev.get('period')}, Source: {rev.get('source')})")
                if "net_income" in fin:
                    ni = fin["net_income"]
                    lines.append(f"- **Net Income**: ${ni.get('value')}B (Margin: {ni.get('margin')})")
                if "eps" in fin:
                    eps = fin["eps"]
                    lines.append(f"- **EPS**: Basic ${eps.get('basic')}, Diluted ${eps.get('diluted')}")
                if "p_e_ratio" in fin:
                    lines.append(f"- **P/E Ratio**: {fin['p_e_ratio'].get('value')}")
                if "ev_ebitda" in fin:
                    lines.append(f"- **EV/EBITDA**: {fin['ev_ebitda'].get('value')}")
        except:
            lines.append(f"- {section_map['financial']}")

    #  Valuation
    if section_map["valuation"]:
        lines.append("\n### Valuation Overview")
        lines.append(section_map["valuation"])

    #  Sentiment
    if section_map["sentiment"]:
        lines.append("\n### Sentiment Summary")
        try:
            sent = eval(section_map["sentiment"]) if isinstance(section_map["sentiment"], str) else section_map["sentiment"]
            lines.append(f"- **Sentiment**: {sent.get('sentiment', 'Unknown')}")
            lines.append(f"- {sent.get('summary', '')}")
        except:
            lines.append(f"- {section_map['sentiment']}")

    #  Risks
    if section_map["risk"]:
        lines.append("\n### Risks")
        lines.append(section_map["risk"])

    return "\n".join(lines)


def combine_node(state):
    summaries = state.get("summaries", [])
    print("[Combine] Received summaries:", summaries)
    report = combine_outputs(summaries)
    return {"report": report}
