"""
Automation Machine Command Center
==================================
Streamlit dashboard for monitoring sprints, costs, video pipeline, and domains.

Run:  streamlit run dashboard/app.py
"""

import json
import re
import shutil
import urllib.request
from datetime import datetime
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yaml

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_PATH = Path(__file__).parent.parent
REGISTRY_PATH = BASE_PATH / "projects" / "registry.json"
USAGE_LOG_PATH = BASE_PATH / "usage_log.json"
VIDEO_STATE_PATH = BASE_PATH / "video-production" / "state" / "generation_progress.json"
CONFIG_PATH = BASE_PATH / "config.yaml"
COMFYUI_URL = "http://100.64.130.71:8188"
OLLAMA_URL = "http://localhost:11434"

st.set_page_config(
    page_title="Automation Machine",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Mobile-friendly CSS -- stack columns on small screens, improve touch targets
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* Stack columns vertically on screens narrower than 768px */
    @media (max-width: 768px) {
        /* Force Streamlit column containers to wrap */
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            width: 100% !important;
            flex: 0 0 100% !important;
            min-width: 100% !important;
        }

        /* Reduce padding for tighter mobile layout */
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }

        /* Make expanders easier to tap */
        [data-testid="stExpander"] summary {
            padding: 0.75rem 0 !important;
        }

        /* Ensure charts don't overflow */
        [data-testid="stPlotlyChart"] {
            max-width: 100% !important;
            overflow-x: auto !important;
        }

        /* Sidebar collapses by default on mobile (Streamlit handles this) */
    }

    /* Tablet: allow 2 columns on medium screens */
    @media (min-width: 769px) and (max-width: 1024px) {
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            flex: 0 0 48% !important;
            min-width: 48% !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Data loaders (safe with fallbacks)
# ---------------------------------------------------------------------------


def load_json(path: Path) -> dict | None:
    """Load a JSON file, return None on any failure."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_yaml(path: Path) -> dict | None:
    """Load a YAML file, return None on any failure."""
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None


registry = load_json(REGISTRY_PATH)
usage_log = load_json(USAGE_LOG_PATH)
video_state = load_json(VIDEO_STATE_PATH)
config = load_yaml(CONFIG_PATH)


# ---------------------------------------------------------------------------
# Health check helpers (cached 60s to avoid blocking on every reload)
# ---------------------------------------------------------------------------


@st.cache_data(ttl=60)
def check_service(url: str, timeout: float = 2.0) -> dict:
    """Ping a service URL. Returns {"ok": bool, "data": dict|None, "error": str|None}."""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                data = None
            return {"ok": True, "data": data, "error": None}
    except Exception as exc:
        return {"ok": False, "data": None, "error": str(exc)}


@st.cache_data(ttl=60)
def get_disk_usage(path_str: str) -> dict | None:
    """Return disk usage for a path: {total_gb, used_gb, free_gb, pct_used}."""
    try:
        usage = shutil.disk_usage(path_str)
        gb = 1024**3
        return {
            "total_gb": usage.total / gb,
            "used_gb": usage.used / gb,
            "free_gb": usage.free / gb,
            "pct_used": usage.used / usage.total * 100,
        }
    except Exception:
        return None

# ---------------------------------------------------------------------------
# Sidebar -- Quick Actions & Refresh
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Quick Actions")

    if st.button("Refresh Data"):
        st.rerun()

    st.divider()

    st.subheader("ComfyUI")
    st.markdown("[Open ComfyUI](http://100.64.130.71:8188)")
    st.caption("The Machine -- RTX 5060 Ti 16GB")

    st.divider()

    st.subheader("Command Cheat Sheet")
    commands = {
        "Auto-routed query": "python automation_brain.py \"question\"",
        "Verbose mode": "python automation_brain.py -v \"question\"",
        "View costs": "python automation_brain.py --stats",
        "List tools": "python automation_brain.py --tools",
        "Current sprint": "python automation_brain.py --sprint",
        "Standup report": "python automation_brain.py --standup",
        "Resume video gen": "python video-production/scripts/generate_comfyui_assets.py --resume-status",
    }
    for label, cmd in commands.items():
        st.caption(label)
        st.code(cmd, language="bash")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("Automation Machine -- Command Center")
st.caption(f"Last loaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ====================================================================
# SECTION 0 -- System Health
# ====================================================================

st.header("System Health")

# Ping services
comfyui_health = check_service(f"{COMFYUI_URL}/system_stats")
ollama_health = check_service(f"{OLLAMA_URL}/api/tags")

# Disk usage for local drive and project directory
local_disk = get_disk_usage("C:\\")

health_col1, health_col2, health_col3 = st.columns(3)

with health_col1:
    st.subheader("ComfyUI")
    if comfyui_health["ok"]:
        st.markdown(":green[ONLINE]")
        stats = comfyui_health.get("data") or {}
        # ComfyUI /system_stats returns {"system": {"...": ...}, "devices": [...]}
        devices = stats.get("devices", [])
        if devices:
            gpu = devices[0]
            gpu_name = gpu.get("name", "Unknown GPU")
            vram_total = gpu.get("vram_total", 0)
            vram_free = gpu.get("vram_free", 0)
            vram_used = vram_total - vram_free
            vram_total_gb = vram_total / (1024**3) if vram_total else 0
            vram_used_gb = vram_used / (1024**3) if vram_used else 0
            vram_pct = (vram_used / vram_total * 100) if vram_total else 0

            st.caption(gpu_name)
            st.progress(
                min(vram_pct / 100, 1.0),
                text=f"VRAM: {vram_used_gb:.1f} / {vram_total_gb:.1f} GB ({vram_pct:.0f}%)",
            )
        else:
            st.caption("No GPU info returned")
        sys_info = stats.get("system", {})
        if sys_info:
            os_name = sys_info.get("os", "")
            py_ver = sys_info.get("python_version", "")
            if os_name:
                st.caption(f"OS: {os_name}")
            if py_ver:
                st.caption(f"Python: {py_ver}")
    else:
        st.markdown(":red[OFFLINE]")
        st.caption(f"Error: {comfyui_health['error'][:80]}" if comfyui_health["error"] else "Cannot reach service")
    st.caption(f"Endpoint: {COMFYUI_URL}")

with health_col2:
    st.subheader("Ollama")
    if ollama_health["ok"]:
        st.markdown(":green[ONLINE]")
        tags_data = ollama_health.get("data") or {}
        models = tags_data.get("models", [])
        if models:
            model_names = [m.get("name", "?") for m in models]
            st.caption(f"{len(models)} models available")
            # Show first few models
            for name in model_names[:6]:
                st.caption(f"  {name}")
            if len(model_names) > 6:
                st.caption(f"  ... +{len(model_names) - 6} more")
        else:
            st.caption("No models loaded")
    else:
        st.markdown(":red[OFFLINE]")
        st.caption(f"Error: {ollama_health['error'][:80]}" if ollama_health["error"] else "Cannot reach service")
    st.caption(f"Endpoint: {OLLAMA_URL}")

with health_col3:
    st.subheader("Disk (C:)")
    if local_disk:
        pct = local_disk["pct_used"]
        if pct > 90:
            st.markdown(":red[LOW SPACE]")
        elif pct > 75:
            st.markdown(":orange[WATCH]")
        else:
            st.markdown(":green[HEALTHY]")
        st.progress(
            min(pct / 100, 1.0),
            text=f"{local_disk['used_gb']:.0f} / {local_disk['total_gb']:.0f} GB ({pct:.0f}%)",
        )
        st.caption(f"Free: {local_disk['free_gb']:.1f} GB")
    else:
        st.markdown(":gray[UNAVAILABLE]")

st.divider()

# ====================================================================
# SECTION 1 -- Sprint Board
# ====================================================================

st.header("Sprint Board")

if registry and registry.get("sprints"):
    # Find the active sprint (or fall back to the last one)
    active_sprint = None
    for sprint in registry["sprints"]:
        if sprint.get("status") == "active":
            active_sprint = sprint
            break
    if active_sprint is None:
        active_sprint = registry["sprints"][-1]

    # Sprint metadata
    col_name, col_dates, col_status = st.columns([3, 2, 1])
    with col_name:
        st.subheader(f"{active_sprint['name']}  ({active_sprint['id']})")
    with col_dates:
        st.metric("Window", f"{active_sprint['start']}  to  {active_sprint['end']}")
    with col_status:
        st.metric("Status", active_sprint["status"].replace("_", " ").title())

    # Goals
    if active_sprint.get("goals"):
        st.markdown("**Goals:** " + " | ".join(active_sprint["goals"]))

    # Tasks
    tasks = active_sprint.get("tasks", [])
    if tasks:
        completed_count = sum(1 for t in tasks if t["status"] == "completed")
        total_count = len(tasks)
        pct = int((completed_count / total_count) * 100) if total_count else 0

        st.progress(pct / 100, text=f"{completed_count}/{total_count} tasks complete ({pct}%)")

        STATUS_COLORS = {
            "completed": ":green[completed]",
            "in_progress": ":blue[in progress]",
            "pending": ":gray[pending]",
            "blocked": ":red[blocked]",
        }

        cols = st.columns(min(len(tasks), 5))
        for idx, task in enumerate(tasks):
            with cols[idx % len(cols)]:
                badge = STATUS_COLORS.get(task["status"], task["status"])
                st.markdown(f"**{task['name']}**")
                st.markdown(badge)
                if task.get("assignee"):
                    st.caption(f"Team: {task['assignee']}")
                if task.get("blocked_by"):
                    st.caption(f"Blocked by: {', '.join(task['blocked_by'])}")
    else:
        st.info("No tasks defined for this sprint.")
else:
    st.warning("Sprint data not available. Check projects/registry.json.")

st.divider()

# ====================================================================
# SECTION 2 -- Domain Map & Certification Roadmap
# ====================================================================

st.header("Domain Map")

if registry and registry.get("domains"):
    domains = registry["domains"]

    DOMAIN_STATUS_COLORS = {
        "active": "green",
        "learning": "blue",
        "planned": "gray",
        "hobby": "purple",
    }

    # Render domain cards in rows of 4
    row_size = 4
    for row_start in range(0, len(domains), row_size):
        row_domains = domains[row_start : row_start + row_size]
        cols = st.columns(row_size)
        for idx, domain in enumerate(row_domains):
            with cols[idx]:
                color = DOMAIN_STATUS_COLORS.get(domain["status"], "gray")
                st.markdown(
                    f"**{domain['id']}** &nbsp; :{color}[{domain['status']}]"
                )
                st.caption(domain.get("description", ""))
                if domain.get("certs"):
                    st.caption("Certs: " + ", ".join(domain["certs"]))

    # Certification roadmap progress
    st.subheader("Certification Roadmap")
    certs = registry.get("certifications", {}).get("roadmap", [])
    if certs:
        completed_certs = sum(1 for c in certs if c.get("status") == "completed")
        total_certs = len(certs)
        cert_pct = int((completed_certs / total_certs) * 100) if total_certs else 0
        st.progress(cert_pct / 100, text=f"{completed_certs}/{total_certs} certifications earned ({cert_pct}%)")

        cert_cols = st.columns(min(len(certs), 5))
        for idx, cert in enumerate(certs):
            with cert_cols[idx % len(cert_cols)]:
                status_badge = ":green[done]" if cert["status"] == "completed" else ":gray[planned]"
                st.markdown(f"**{cert['name']}**")
                st.caption(f"Domain: {cert['domain']} | {status_badge}")
    else:
        st.info("No certifications in roadmap.")
else:
    st.warning("Domain data not available. Check projects/registry.json.")

st.divider()

# ====================================================================
# SECTION 3 -- Cost Tracker
# ====================================================================

st.header("Cost Tracker")

if usage_log and usage_log.get("summary"):
    summary = usage_log["summary"]
    monthly_budget = 50.00
    daily_budget = 5.00

    if config and config.get("cost_tracking"):
        monthly_budget = config["cost_tracking"].get("monthly_budget", 50.00)
        daily_budget = config["cost_tracking"].get("daily_budget", 5.00)

    # Determine current month key (e.g., "2026-02")
    current_month_key = datetime.now().strftime("%Y-%m")
    monthly_data = summary.get("monthly", {})
    current_month = monthly_data.get(current_month_key, {"queries": 0, "cost_usd": 0.0})
    month_spend = current_month.get("cost_usd", 0.0)

    # Today's date key
    today_key = datetime.now().strftime("%Y-%m-%d")
    daily_data = summary.get("daily", {})
    today_data = daily_data.get(today_key, {"queries": 0, "cost_usd": 0.0})
    today_spend = today_data.get("cost_usd", 0.0)

    # KPI row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Queries", summary.get("total_queries", 0))
    with kpi2:
        st.metric("Total Spend", f"${summary.get('total_cost_usd', 0.0):.4f}")
    with kpi3:
        st.metric("Month Spend", f"${month_spend:.4f}")
    with kpi4:
        st.metric("Today Spend", f"${today_spend:.4f}")

    # Monthly budget bar
    budget_pct = min(month_spend / monthly_budget, 1.0) if monthly_budget > 0 else 0
    if month_spend > 30:
        budget_label = f"${month_spend:.2f} / ${monthly_budget:.2f} -- OVER $30"
    elif month_spend > 10:
        budget_label = f"${month_spend:.2f} / ${monthly_budget:.2f} -- watch spending"
    else:
        budget_label = f"${month_spend:.2f} / ${monthly_budget:.2f} -- healthy"
    st.progress(budget_pct, text=f"Monthly Budget: {budget_label}")

    # Row 1: Daily spend + cumulative trend
    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.subheader("Daily Spend")
        if daily_data:
            dates = sorted(daily_data.keys())
            costs = [daily_data[d].get("cost_usd", 0.0) for d in dates]

            fig_daily = go.Figure()
            fig_daily.add_trace(go.Bar(
                x=dates,
                y=costs,
                name="Cost ($)",
                marker_color="#636EFA",
                hovertemplate="Date: %{x}<br>Cost: $%{y:.4f}<br>",
            ))
            # Daily budget threshold line
            fig_daily.add_hline(
                y=daily_budget, line_dash="dash", line_color="red",
                annotation_text=f"Daily limit ${daily_budget:.2f}",
                annotation_position="top right",
            )
            fig_daily.update_layout(
                xaxis_title="Date",
                yaxis_title="Cost (USD)",
                height=350,
                margin=dict(l=40, r=20, t=30, b=40),
                template="plotly_dark",
            )
            st.plotly_chart(fig_daily, use_container_width=True)
        else:
            st.info("No daily data yet.")

    with chart_right:
        st.subheader("Cumulative Spend")
        if daily_data:
            dates = sorted(daily_data.keys())
            costs = [daily_data[d].get("cost_usd", 0.0) for d in dates]
            cumulative = []
            running = 0.0
            for c in costs:
                running += c
                cumulative.append(running)

            fig_cum = go.Figure()
            fig_cum.add_trace(go.Scatter(
                x=dates,
                y=cumulative,
                mode="lines+markers",
                name="Cumulative",
                line=dict(color="#00CC96", width=2),
                hovertemplate="Date: %{x}<br>Total: $%{y:.4f}<br>",
            ))
            fig_cum.add_hline(
                y=monthly_budget, line_dash="dash", line_color="red",
                annotation_text=f"Monthly limit ${monthly_budget:.2f}",
                annotation_position="top right",
            )
            fig_cum.update_layout(
                xaxis_title="Date",
                yaxis_title="Cumulative Cost (USD)",
                height=350,
                margin=dict(l=40, r=20, t=30, b=40),
                template="plotly_dark",
            )
            st.plotly_chart(fig_cum, use_container_width=True)
        else:
            st.info("No daily data yet.")

    # Row 2: Tool breakdown (queries pie + cost bar)
    chart_left2, chart_right2 = st.columns(2)

    with chart_left2:
        st.subheader("Queries by Tool")
        by_tool = summary.get("by_tool", {})
        if by_tool:
            tool_names = []
            tool_queries = []
            for tool_name, tool_data in by_tool.items():
                q = tool_data.get("queries", 0)
                if q > 0:
                    tool_names.append(tool_name)
                    tool_queries.append(q)

            if tool_names:
                fig_pie = px.pie(
                    names=tool_names,
                    values=tool_queries,
                    hole=0.4,
                )
                fig_pie.update_layout(
                    height=350,
                    margin=dict(l=20, r=20, t=30, b=20),
                    template="plotly_dark",
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No tool queries recorded yet.")
        else:
            st.info("No tool breakdown data.")

    with chart_right2:
        st.subheader("Cost by Tool")
        by_tool = summary.get("by_tool", {})
        if by_tool:
            tool_names_cost = []
            tool_costs = []
            for tool_name, tool_data in by_tool.items():
                cost = tool_data.get("cost_usd", 0.0)
                tool_names_cost.append(tool_name)
                tool_costs.append(cost)

            # Sort by cost descending
            paired = sorted(zip(tool_costs, tool_names_cost), reverse=True)
            tool_costs = [p[0] for p in paired]
            tool_names_cost = [p[1] for p in paired]

            bar_colors = ["#EF553B" if c > 0 else "#636EFA" for c in tool_costs]
            fig_tool_cost = go.Figure()
            fig_tool_cost.add_trace(go.Bar(
                x=tool_names_cost,
                y=tool_costs,
                marker_color=bar_colors,
                hovertemplate="Tool: %{x}<br>Cost: $%{y:.4f}<br>",
            ))
            fig_tool_cost.update_layout(
                yaxis_title="Cost (USD)",
                height=350,
                margin=dict(l=40, r=20, t=30, b=40),
                template="plotly_dark",
            )
            st.plotly_chart(fig_tool_cost, use_container_width=True)
        else:
            st.info("No tool cost data.")

    # Row 3: Agent session costs + budget forecast
    chart_left3, chart_right3 = st.columns(2)

    with chart_left3:
        st.subheader("Agent Session Costs")
        # Read agent states for cost data
        _agents_dir = BASE_PATH / "agents"
        _agent_cost_names = []
        _agent_cost_vals = []
        if _agents_dir.exists():
            for _adir in sorted(_agents_dir.iterdir()):
                if _adir.is_dir() and _adir.name != "_template":
                    _astate = load_json(_adir / "state.json")
                    if _astate:
                        _agent_cost_names.append(_astate.get("agent", _adir.name))
                        _agent_cost_vals.append(_astate.get("session_cost_usd", 0.0))

        if _agent_cost_names:
            fig_agent = go.Figure()
            fig_agent.add_trace(go.Bar(
                x=_agent_cost_names,
                y=_agent_cost_vals,
                marker_color=["#636EFA", "#EF553B", "#00CC96", "#AB63FA",
                               "#FFA15A", "#19D3F3", "#FF6692", "#B6E880"][
                    :len(_agent_cost_names)
                ],
                hovertemplate="Agent: %{x}<br>Cost: $%{y:.4f}<br>",
            ))
            fig_agent.update_layout(
                yaxis_title="Session Cost (USD)",
                height=300,
                margin=dict(l=40, r=20, t=30, b=40),
                template="plotly_dark",
            )
            st.plotly_chart(fig_agent, use_container_width=True)

            total_agent_cost = sum(_agent_cost_vals)
            st.caption(f"Total agent session spend: ${total_agent_cost:.4f}")
        else:
            st.info("No agent cost data available.")

    with chart_right3:
        st.subheader("Budget Forecast")
        if daily_data and month_spend > 0:
            now = datetime.now()
            day_of_month = now.day
            days_in_month = 31  # conservative estimate
            if now.month in (4, 6, 9, 11):
                days_in_month = 30
            elif now.month == 2:
                days_in_month = 28

            # Count active days this month (days with any spend)
            month_prefix = now.strftime("%Y-%m")
            active_days = sum(
                1 for d in daily_data if d.startswith(month_prefix)
            )
            if active_days > 0:
                avg_daily = month_spend / active_days
                remaining_days = days_in_month - day_of_month
                projected = month_spend + (avg_daily * remaining_days)
            else:
                avg_daily = 0.0
                projected = month_spend

            fc1, fc2 = st.columns(2)
            with fc1:
                st.metric("Avg Daily Spend", f"${avg_daily:.4f}")
                st.metric("Active Days", f"{active_days} / {day_of_month}")
            with fc2:
                delta_vs_budget = projected - monthly_budget
                st.metric(
                    "Projected Month-End",
                    f"${projected:.2f}",
                    delta=f"${delta_vs_budget:+.2f} vs budget",
                    delta_color="inverse",
                )
                pct_used = (month_spend / monthly_budget * 100) if monthly_budget else 0
                st.metric("Budget Used", f"{pct_used:.1f}%")

            # Visual forecast bar
            forecast_pct = min(projected / monthly_budget, 1.0) if monthly_budget else 0
            if projected > monthly_budget:
                forecast_label = f"Projected ${projected:.2f} EXCEEDS ${monthly_budget:.2f}"
            elif projected > monthly_budget * 0.8:
                forecast_label = f"Projected ${projected:.2f} -- approaching limit"
            else:
                forecast_label = f"Projected ${projected:.2f} -- on track"
            st.progress(forecast_pct, text=forecast_label)
        else:
            st.info("Not enough data to forecast. Spend some first!")
else:
    st.warning("Usage log not available. Check usage_log.json.")

st.divider()

# ====================================================================
# SECTION 4 -- Video Pipeline
# ====================================================================

st.header("Video Pipeline")

if video_state and video_state.get("jobs"):
    jobs = video_state["jobs"]
    last_run = video_state.get("last_run", "unknown")
    st.caption(f"Pipeline last run: {last_run}")

    # Overall pipeline completion
    total_segments = 0
    completed_segments = 0
    for job_data in jobs.values():
        total_segments += job_data.get("segments_total", 0)
        completed_segments += len(job_data.get("segments_completed", []))

    overall_pct = int((completed_segments / total_segments) * 100) if total_segments else 0
    st.progress(
        overall_pct / 100,
        text=f"Overall: {completed_segments}/{total_segments} segments ({overall_pct}%)",
    )

    # Per-job cards
    job_cols = st.columns(min(len(jobs), 4))
    for idx, (job_name, job_data) in enumerate(jobs.items()):
        with job_cols[idx % len(job_cols)]:
            status = job_data.get("status", "unknown")
            job_type = job_data.get("job_type", "")
            seg_total = job_data.get("segments_total", 0)
            seg_done = len(job_data.get("segments_completed", []))
            stitched = job_data.get("stitched", False)
            pct = int((seg_done / seg_total) * 100) if seg_total else 0

            if status == "completed":
                color = "green"
            elif status == "in_progress":
                color = "blue"
            else:
                color = "gray"

            st.markdown(f"**{job_name}** &nbsp; :{color}[{status}]")
            st.caption(f"Type: {job_type}")
            st.progress(pct / 100, text=f"{seg_done}/{seg_total} segments")
            if stitched:
                st.caption("Stitched: yes")
            last_upd = job_data.get("last_updated", "")
            if last_upd:
                st.caption(f"Updated: {last_upd[:16]}")
else:
    st.warning("Video pipeline state not available. Check video-production/state/generation_progress.json.")

st.divider()

# ====================================================================
# SECTION 5 -- Trading Research
# ====================================================================

st.header("Trading Research")

TRADING_DIR = BASE_PATH / "trading"
TRADING_RESULTS_DIR = TRADING_DIR / "results"
TRADING_AGENT_STATE_PATH = BASE_PATH / "agents" / "trading" / "state.json"

trading_agent_state = load_json(TRADING_AGENT_STATE_PATH)

# --- Agent progress bar ---
if trading_agent_state:
    t_tasks = trading_agent_state.get("tasks", [])
    t_total = len(t_tasks)
    t_done = sum(1 for t in t_tasks if t.get("status") == "completed")
    t_pct = int((t_done / t_total) * 100) if t_total else 0
    st.progress(t_pct / 100, text=f"Research progress: {t_done}/{t_total} tasks ({t_pct}%)")

    # Current focus from agent notes
    agent_notes = trading_agent_state.get("notes", [])
    if agent_notes:
        st.caption(f"Latest: {agent_notes[-1][:200]}")

# --- Backtest results ---
backtest_results = []
if TRADING_RESULTS_DIR.exists():
    for result_file in sorted(TRADING_RESULTS_DIR.glob("*.json")):
        data = load_json(result_file)
        if data:
            backtest_results.append(data)

if backtest_results:
    st.subheader("Backtest Results")

    # Summary table
    result_cols = st.columns(min(len(backtest_results), 4))
    for idx, result in enumerate(backtest_results):
        with result_cols[idx % len(result_cols)]:
            ticker = result.get("ticker", "?")
            strategy = result.get("strategy", "?")
            ret_pct = result.get("total_return_pct", 0.0)
            dd_pct = result.get("max_drawdown_pct", 0.0)
            trade_count = result.get("trade_count", 0)
            period = result.get("period", "?")
            final_val = result.get("final_value", 0.0)

            ret_color = "green" if ret_pct > 0 else "red" if ret_pct < 0 else "gray"
            st.markdown(f"**{ticker} -- {strategy.upper()}**")
            st.markdown(f"Return: :{ret_color}[{ret_pct:+.2f}%]")
            st.metric("Final Value", f"${final_val:,.2f}")
            st.caption(f"Trades: {trade_count} | DD: {dd_pct:.2f}% | Period: {period}")

    # Returns comparison chart
    if len(backtest_results) > 1:
        chart_labels = [f"{r.get('ticker','?')} {r.get('strategy','?')} ({r.get('period','?')})" for r in backtest_results]
        chart_returns = [r.get("total_return_pct", 0.0) for r in backtest_results]
        chart_colors = ["#00CC96" if v >= 0 else "#EF553B" for v in chart_returns]

        fig_returns = go.Figure()
        fig_returns.add_trace(go.Bar(
            x=chart_labels,
            y=chart_returns,
            marker_color=chart_colors,
            hovertemplate="Strategy: %{x}<br>Return: %{y:.2f}%<br>",
        ))
        fig_returns.update_layout(
            yaxis_title="Return (%)",
            height=300,
            margin=dict(l=40, r=20, t=30, b=80),
            template="plotly_dark",
        )
        st.plotly_chart(fig_returns, use_container_width=True)

    # Expandable trade log
    with st.expander("Trade Log"):
        for result in backtest_results:
            ticker = result.get("ticker", "?")
            strategy = result.get("strategy", "?")
            trades = result.get("trades", [])
            if trades:
                st.markdown(f"**{ticker} -- {strategy.upper()}** ({len(trades)} trades)")
                for trade in trades:
                    action = trade.get("action", "?")
                    price = trade.get("price", 0.0)
                    date = trade.get("date", "?")
                    action_color = "green" if action == "BUY" else "red"
                    st.markdown(f"- :{action_color}[{action}] {date} @ ${price:.2f}")
            else:
                st.caption(f"{ticker} -- {strategy}: No trades executed")
else:
    st.info("No backtest results yet. Run: `python trading/backtest.py`")

# --- Task detail ---
if trading_agent_state and trading_agent_state.get("tasks"):
    TASK_ICONS = {
        "completed": ":green[done]",
        "in_progress": ":blue[in progress]",
        "pending": ":gray[pending]",
        "blocked": ":red[blocked]",
    }
    with st.expander("Research task detail"):
        for task in trading_agent_state["tasks"]:
            badge = TASK_ICONS.get(task.get("status", "pending"), task.get("status", ""))
            notes = task.get("notes") or ""
            note_str = f" -- {notes[:120]}" if notes else ""
            st.markdown(f"- {badge} **{task.get('name', task.get('id', '?'))}**{note_str}")

# --- Watchlist & config info ---
trading_config_path = TRADING_DIR / "config.py"
if trading_config_path.exists():
    try:
        config_text = trading_config_path.read_text(encoding="utf-8")
        # Extract watchlist from config.py
        wl_match = re.search(r'WATCHLIST\s*=\s*\[([^\]]+)\]', config_text)
        if wl_match:
            tickers_raw = wl_match.group(1)
            tickers = [t.strip().strip('"').strip("'") for t in tickers_raw.split(",") if t.strip()]
            st.caption(f"Watchlist: {', '.join(tickers)}")
    except Exception:
        pass

st.divider()

# ====================================================================
# SECTION 6 -- AWS Certification Progress
# ====================================================================

st.header("AWS Certification Progress")

AWS_CERT_AGENT_STATE_PATH = BASE_PATH / "agents" / "aws-cert" / "state.json"
AWS_STUDY_DIR = BASE_PATH / "knowledge-base" / "training" / "aws" / "clf-c02"
AWS_STUDY_PLAN_PATH = AWS_STUDY_DIR / "study-plan.md"

aws_cert_state = load_json(AWS_CERT_AGENT_STATE_PATH)

# --- Exam info ---
exam_col1, exam_col2, exam_col3, exam_col4 = st.columns(4)
with exam_col1:
    st.metric("Exam", "CLF-C02")
with exam_col2:
    st.metric("Questions", "65 (50 scored)")
with exam_col3:
    st.metric("Passing Score", "700 / 1000")
with exam_col4:
    st.metric("Cost", "$100 USD")

# --- Domain study progress ---
# Define the 4 domains with weights and study note file names
CLF_DOMAINS = [
    {"num": 1, "name": "Cloud Concepts", "weight": 24, "file": "domain-1-cloud-concepts.md"},
    {"num": 2, "name": "Security & Compliance", "weight": 30, "file": "domain-2-security-compliance.md"},
    {"num": 3, "name": "Technology & Services", "weight": 34, "file": "domain-3-technology-services.md"},
    {"num": 4, "name": "Billing & Pricing", "weight": 12, "file": "domain-4-billing-pricing.md"},
]

st.subheader("Domain Study Notes")

domains_dir = AWS_STUDY_DIR / "domains"
practice_dir = AWS_STUDY_DIR / "practice-questions"

domains_complete = 0
domain_cols = st.columns(4)
for idx, domain in enumerate(CLF_DOMAINS):
    with domain_cols[idx]:
        notes_exist = (domains_dir / domain["file"]).exists() if domains_dir.exists() else False
        # Check for practice questions per domain
        pq_file = f"domain-{domain['num']}-questions.md"
        pq_exist = (practice_dir / pq_file).exists() if practice_dir.exists() else False

        if notes_exist:
            domains_complete += 1
            st.markdown(f"**D{domain['num']}: {domain['name']}**")
            st.markdown(f":green[Notes complete] | Weight: {domain['weight']}%")
        else:
            st.markdown(f"**D{domain['num']}: {domain['name']}**")
            st.markdown(f":gray[Notes pending] | Weight: {domain['weight']}%")

        if pq_exist:
            st.caption("Practice Qs: ready")
        else:
            st.caption("Practice Qs: pending")

# Study notes overall progress bar
notes_pct = int((domains_complete / 4) * 100)
st.progress(notes_pct / 100, text=f"Study notes: {domains_complete}/4 domains complete ({notes_pct}%)")

# --- Practice questions status ---
pq_files = list(practice_dir.glob("*.md")) if practice_dir.exists() else []
if pq_files:
    st.caption(f"Practice question files: {len(pq_files)}")
else:
    st.caption("Practice questions: not yet created (80 planned)")

# --- Study materials inventory ---
study_files = list(AWS_STUDY_DIR.rglob("*.md")) if AWS_STUDY_DIR.exists() else []
if study_files:
    st.caption(f"Total study files: {len(study_files)}")

# --- Agent task progress ---
if aws_cert_state:
    st.subheader("Study Agent Progress")
    a_tasks = aws_cert_state.get("tasks", [])
    a_total = len(a_tasks)
    a_done = sum(1 for t in a_tasks if t.get("status") == "completed")
    a_pct = int((a_done / a_total) * 100) if a_total else 0
    st.progress(a_pct / 100, text=f"Agent tasks: {a_done}/{a_total} ({a_pct}%)")

    # Latest agent note
    a_notes = aws_cert_state.get("notes", [])
    if a_notes:
        st.caption(f"Latest: {a_notes[-1][:200]}")

    # Expandable task detail
    CERT_TASK_ICONS = {
        "completed": ":green[done]",
        "in_progress": ":blue[in progress]",
        "pending": ":gray[pending]",
        "blocked": ":red[blocked]",
    }
    with st.expander("Study agent task detail"):
        for task in a_tasks:
            badge = CERT_TASK_ICONS.get(task.get("status", "pending"), task.get("status", ""))
            notes = task.get("notes") or ""
            note_str = f" -- {notes[:120]}" if notes else ""
            st.markdown(f"- {badge} **{task.get('name', task.get('id', '?'))}**{note_str}")

st.divider()

# ====================================================================
# SECTION 7 -- Agent Orchestration
# ====================================================================

st.header("Agent Orchestration")

AGENTS_DIR = BASE_PATH / "agents"
BULLETIN_PATH = AGENTS_DIR / "BULLETIN.md"

# Discover agent directories (skip _template)
agent_names = sorted([
    d.name for d in AGENTS_DIR.iterdir()
    if d.is_dir() and d.name != "_template" and (d / "state.json").exists()
]) if AGENTS_DIR.exists() else []


def _count_agent_tasks(state: dict) -> tuple[int, int, int, int]:
    """Return (total, completed, in_progress, pending) from an agent state.

    Tasks can appear in the tasks[] list with status="completed" AND in
    completed_tasks[].  Deduplicate by using the tasks[] list as the
    canonical source -- it always holds every task including completed ones.
    """
    tasks = state.get("tasks", [])
    total = len(tasks)
    done = sum(1 for t in tasks if t.get("status") == "completed")
    in_prog = sum(1 for t in tasks if t.get("status") == "in_progress")
    pending = total - done - in_prog
    return total, done, in_prog, pending


if agent_names:
    # Load all agent states
    agent_states = {}
    for name in agent_names:
        state = load_json(AGENTS_DIR / name / "state.json")
        if state:
            agent_states[name] = state

    # Overall progress across all agents
    grand_total = 0
    grand_done = 0
    for state in agent_states.values():
        total, done, _, _ = _count_agent_tasks(state)
        grand_total += total
        grand_done += done

    if grand_total > 0:
        overall_pct = int((grand_done / grand_total) * 100)
        st.progress(
            overall_pct / 100,
            text=f"Overall: {grand_done}/{grand_total} tasks across {len(agent_names)} agents ({overall_pct}%)",
        )

    # Per-agent summary cards
    agent_cols = st.columns(min(len(agent_names), 4))
    for idx, name in enumerate(agent_names):
        state = agent_states.get(name, {})
        with agent_cols[idx % len(agent_cols)]:
            status = state.get("status", "unknown")
            iteration = state.get("iteration", 0)
            session_cost = state.get("session_cost_usd", 0.0)
            exit_signal = state.get("exit_signal", False)

            # Status color
            if exit_signal:
                color = "red"
                status_label = state.get("exit_reason", "exited")
            elif status in ("running", "active"):
                color = "blue"
                status_label = status
            elif status == "idle":
                color = "gray"
                status_label = "idle"
            else:
                color = "gray"
                status_label = status

            st.markdown(f"**{name}** &nbsp; :{color}[{status_label}]")
            st.caption(f"Iteration: {iteration} | Cost: ${session_cost:.4f}")

            # Task progress
            total, done, in_prog, pending = _count_agent_tasks(state)
            if total > 0:
                task_pct = int((done / total) * 100)
                st.progress(task_pct / 100, text=f"{done}/{total} tasks")

            current = state.get("current_task")
            if current:
                st.caption(f"Working on: {current}")

            # Heartbeat
            heartbeat_path = AGENTS_DIR / name / "HEARTBEAT.md"
            if heartbeat_path.exists():
                try:
                    hb_content = heartbeat_path.read_text(encoding="utf-8")
                    for line in hb_content.splitlines():
                        if line.startswith("Last alive:"):
                            last_alive = line.replace("Last alive:", "").strip()
                            if last_alive != "never":
                                st.caption(f"Heartbeat: {last_alive[:16]}")
                            break
                except Exception:
                    pass

            last_upd = state.get("last_updated")
            if last_upd:
                st.caption(f"Updated: {last_upd[:16]}")

    # Expandable task detail per agent
    for name in agent_names:
        state = agent_states.get(name, {})
        tasks = state.get("tasks", [])
        if not tasks:
            continue

        with st.expander(f"{name} -- task detail"):
            TASK_ICONS = {
                "completed": ":green[done]",
                "in_progress": ":blue[in progress]",
                "pending": ":gray[pending]",
                "blocked": ":red[blocked]",
            }
            for task in tasks:
                badge = TASK_ICONS.get(task.get("status", "pending"), task.get("status", ""))
                notes = task.get("notes") or ""
                note_str = f" -- {notes[:100]}" if notes else ""
                st.markdown(f"- {badge} **{task.get('name', task.get('id', '?'))}**{note_str}")

            # Agent notes
            agent_notes = state.get("notes", [])
            if agent_notes:
                st.markdown("---")
                st.markdown("**Agent notes:**")
                for note in agent_notes[-3:]:  # show last 3
                    st.caption(note)

    # Bulletin board status + recent completions
    if BULLETIN_PATH.exists():
        try:
            bulletin = BULLETIN_PATH.read_text(encoding="utf-8")
        except Exception:
            bulletin = ""

        # Cost Guardian signal
        signal_match = re.search(r"SIGNAL:\s*(\S+)", bulletin)
        signal = signal_match.group(1) if signal_match else "UNKNOWN"

        if signal not in ("NONE", "NONE,"):
            st.error(f"Cost Guardian Signal: {signal}")
        else:
            st.success("Cost Guardian: All clear")

        # Recent completions from BULLETIN
        completions = re.findall(
            r"- \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\] (\S+): (.+)",
            bulletin,
        )
        if completions:
            with st.expander("Recent agent completions"):
                for ts, agent, desc in completions[-10:]:
                    st.markdown(f"- **{agent}** ({ts}): {desc}")
else:
    st.info("No agents configured. See agents/ directory.")

st.divider()

# ====================================================================
# Footer
# ====================================================================

st.caption("Automation Machine Command Center -- local-first AI orchestration")
