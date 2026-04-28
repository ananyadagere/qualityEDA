"""
ELRP Quality EDA Dashboard  —  Light Theme
Employee · Learnability · Retention · Performance
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ELRP · Quality Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# LIGHT THEME CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f8fafc;
}

/* Sidebar — light */
section[data-testid="stSidebar"] {
    background: #f1f5f9;
    border-right: 1px solid #e2e8f0;
}
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #1e3a5f;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}

/* Page header */
.elrp-header {
    background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 60%, #f0fdf4 100%);
    padding: 20px 28px;
    border-radius: 12px;
    border: 1px solid #bfdbfe;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.elrp-header h1 { color: #1e3a5f; margin: 0; font-size: 22px; font-weight: 700; }
.elrp-header .badge {
    background: #1e3a5f;
    color: #dbeafe;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

/* KPI cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
}
.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.kpi-value { font-size: 26px; font-weight: 700; color: #1e3a5f; margin: 0; }
.kpi-label { font-size: 11px; color: #64748b; margin: 4px 0 0; font-weight: 600;
              text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-sub   { font-size: 11px; color: #94a3b8; margin: 2px 0 0; }

/* Insight callouts */
.insight-card {
    background: #f0f9ff;
    border-left: 4px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 8px 0 16px;
}
.insight-card.warn    { background: #fff7ed; border-color: #f97316; }
.insight-card.success { background: #f0fdf4; border-color: #22c55e; }
.insight-card.danger  { background: #fff1f2; border-color: #f43f5e; }
.insight-card p { margin: 0; font-size: 13px; color: #1e293b; line-height: 1.7; }

/* Section headers */
.section-title {
    font-size: 15px; font-weight: 700; color: #1e3a5f;
    margin: 24px 0 2px;
    padding-bottom: 6px;
    border-bottom: 2px solid #e2e8f0;
}
.section-sub { font-size: 12px; color: #64748b; margin: 0 0 14px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #e2e8f0;
    padding: 4px;
    border-radius: 8px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    color: #475569;
    background: transparent;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #1e3a5f !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Metric widget */
div[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PALETTE  — light-theme friendly
# ─────────────────────────────────────────────────────────────────────────────
P = {
    "primary":  "#1e3a5f",
    "blue":     "#2563eb",
    "sky":      "#0284c7",
    "teal":     "#0d9488",
    "amber":    "#d97706",
    "red":      "#dc2626",
    "violet":   "#7c3aed",
    "gray":     "#6b7280",
    "low":      "#dc2626",
    "mid":      "#d97706",
    "high":     "#059669",
    "low_bg":   "#fee2e2",
    "mid_bg":   "#fef3c7",
    "high_bg":  "#d1fae5",
}
TIER_COLORS = {"Low": P["low"], "Mid": P["mid"], "High": P["high"]}
SCALE_RYG   = ["#dc2626", "#d97706", "#059669"]   # red → yellow → green
T = "plotly_white"                                  # plotly template


def fmt(n, d=1):  return f"{n:,.{d}f}"
def pct(n):       return f"{n:.1f}%"


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading quality data…")
def load_quality(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    df["GEO"]          = df["GEO"].str.strip().str.upper()
    df["Account_name"] = df["Account_name"].str.strip().str.upper()
    df["lob"]          = df["lob"].str.strip().str.upper()
    df["qa_pct"]       = (df["base_points_achieved"] / df["max_base_points"] * 100
                          ).replace([np.inf, -np.inf], np.nan)
    df["qa_pct_capped"] = df["qa_pct"].clip(upper=100)
    df["month_dt"]      = df["date"].dt.to_period("M").dt.to_timestamp()
    df["quarter"]       = df["date"].dt.to_period("Q").astype(str)
    return df


@st.cache_data(show_spinner=False)
def build_emp(df: pd.DataFrame, tier_method: str) -> pd.DataFrame:
    emp = df.groupby("GLOBAL_ID").agg(
        avg_qa        = ("qa_pct_capped", "mean"),
        qa_std        = ("qa_pct_capped", "std"),
        n_evals       = ("qa_pct_capped", "count"),
        n_accounts    = ("Account_name",  "nunique"),
        n_lobs        = ("lob",           "nunique"),
        first_eval    = ("date",          "min"),
        last_eval     = ("date",          "max"),
        geo           = ("GEO",           "first"),
    ).reset_index()
    emp["tenure_days"] = (emp["last_eval"] - emp["first_eval"]).dt.days
    emp["qa_std"]      = emp["qa_std"].fillna(0)

    if tier_method.startswith("Score"):
        conds = [emp["avg_qa"] < 85, emp["avg_qa"] < 95, emp["avg_qa"] >= 95]
        emp["perf_tier"] = np.select(conds, ["Low", "Mid", "High"], default="High")
    else:
        emp["perf_tier"] = pd.qcut(
            emp["avg_qa"], q=3, labels=["Low", "Mid", "High"]
        ).astype(str)
    return emp


def safe_json(obj):
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    if isinstance(obj, float) and np.isnan(obj):
        return None
    if hasattr(obj, "item"):
        return obj.item()
    raise TypeError(type(obj))


def to_rec(df): return json.loads(
    df.to_json(orient="records", date_format="iso", default_handler=str))


# ─────────────────────────────────────────────────────────────────────────────
# JSON REPORT
# ─────────────────────────────────────────────────────────────────────────────
def build_report(df, emp, geo_sel, acct_sel, lob_sel):
    rpt = {
        "generated_at": datetime.now().isoformat(),
        "elrp_version": "v1.0-2025",
        "filters": {"geo": geo_sel, "account": acct_sel, "lob": lob_sel},
        "sections": [],
    }

    def sec(title, desc, charts):
        rpt["sections"].append(
            {"section_title": title, "description": desc, "charts": charts})

    def ch(title, desc, data_df, ann=None):
        c = {"chart_title": title, "description": desc, "data": to_rec(data_df)}
        if ann: c["annotations"] = ann
        return c

    # S1 — Health
    geo_agg = df.groupby("GEO").agg(
        evals=("GLOBAL_ID","count"), emps=("GLOBAL_ID","nunique"),
        avg_qa=("qa_pct_capped","mean")).reset_index()
    acct_agg = df.groupby("Account_name").agg(
        evals=("GLOBAL_ID","count"), emps=("GLOBAL_ID","nunique"),
        avg_qa=("qa_pct_capped","mean")).reset_index()
    missing = pd.DataFrame({
        "Column": ["base_points_achieved", "qa_pct"],
        "Missing": [df["base_points_achieved"].isnull().sum(), df["qa_pct"].isnull().sum()],
        "Missing_pct": [df["base_points_achieved"].isnull().mean()*100,
                        df["qa_pct"].isnull().mean()*100],
    })
    sec("Dataset Health", "Completeness, GEO split, account distribution.",
        [ch("GEO Distribution", "Evals and avg QA by GEO.", geo_agg),
         ch("Account Distribution", "Evals and avg QA by account.", acct_agg),
         ch("Missing Data", "Null counts per key column.", missing)])

    # S2 — Distributions
    stats = df["qa_pct_capped"].describe().reset_index()
    stats.columns = ["Statistic", "Value"]
    tier_dist = emp.groupby("perf_tier").agg(
        Employees=("GLOBAL_ID","count"), Avg_QA=("avg_qa","mean"),
        Avg_Evals=("n_evals","mean")).reset_index()
    geo_score = df.groupby("GEO")["qa_pct_capped"].agg(
        ["mean","std","count"]).reset_index()
    sec("Score Distributions", "QA score spread across employees and geographies.",
        [ch("Score Stats", "Descriptive stats.", stats,
            ann={"mean": round(float(df["qa_pct_capped"].mean()),2),
                 "median": round(float(df["qa_pct_capped"].median()),2)}),
         ch("Tier Distribution", "Low/Mid/High breakdown.", tier_dist),
         ch("Score by GEO", "Avg and spread by geography.", geo_score)])

    # S3 — Trends
    monthly = df.groupby(["month_dt","GEO"])["qa_pct_capped"].mean().reset_index()
    vol     = df.groupby("month_dt").agg(
        Evals=("GLOBAL_ID","count"), Avg_QA=("qa_pct_capped","mean")).reset_index()
    sec("Trends", "Month-over-month performance evolution.",
        [ch("Monthly GEO Trend", "Avg QA by GEO over time.", monthly),
         ch("Volume vs QA", "Eval volume and avg score.", vol)])

    # S4 — ELRP
    consistency = emp[["GLOBAL_ID","qa_std","avg_qa","n_evals","perf_tier"]].copy()
    learn_early = df[df["date"] < pd.Timestamp("2025-07-01")
                     ].groupby("GLOBAL_ID")["qa_pct_capped"].mean()
    learn_late  = df[df["date"] >= pd.Timestamp("2025-07-01")
                     ].groupby("GLOBAL_ID")["qa_pct_capped"].mean()
    learn = pd.DataFrame({"early": learn_early, "late": learn_late}
                         ).dropna().reset_index()
    learn["change"] = learn["late"] - learn["early"]
    sec("ELRP Performance Intelligence", "Consistency, learnability, fitment.",
        [ch("Score Consistency", "Avg QA vs std dev per employee.", consistency),
         ch("Learnability", "QA change H1 vs H2 2025.", learn)])

    # S5 — Account × LOB
    al = df.groupby(["Account_name","lob"])["qa_pct_capped"].agg(
        ["mean","count","std"]).reset_index()
    al.columns = ["Account","LOB","Avg_QA","Count","Std"]
    sec("Account × LOB", "Performance drilled to LOB level.",
        [ch("Account × LOB Heatmap", "Avg QA by account and LOB.", al)])

    return rpt


# ─────────────────────────────────────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def callout(text, kind="info"):
    cls = {"info": "", "warn": " warn", "success": " success", "danger": " danger"
           }.get(kind, "")
    st.markdown(f'<div class="insight-card{cls}"><p>{text}</p></div>',
                unsafe_allow_html=True)


def sh(title, sub=""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="section-sub">{sub}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────────────────────
def main():

    # ── HEADER ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="elrp-header">
      <div>
        <h1>🎯 ELRP · Quality Intelligence Dashboard</h1>
        <p style="color:#475569;margin:4px 0 0;font-size:13px;">
          Employee &nbsp;·&nbsp; Learnability &nbsp;·&nbsp; Retention &nbsp;·&nbsp; Performance
        </p>
      </div>
      <span class="badge">v1.0 · 2025</span>
    </div>
    """, unsafe_allow_html=True)

    # ── SIDEBAR ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 📂 Data Source")
        uploaded = st.file_uploader("Upload Quality CSV", type=["csv"])

        if uploaded is None:
            import os
            fallback = next(
                (p for p in ["Quality_3162.csv",
                              "/mnt/user-data/uploads/Quality_3162.csv"]
                 if os.path.exists(p)), None)
            if fallback:
                df_raw = load_quality(fallback)
                st.success(f"✅ {fallback.split('/')[-1]}")
            else:
                st.info("📤 Upload Quality_3162.csv to get started.")
                st.stop()
        else:
            import tempfile, os
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(uploaded.read())
            df_raw = load_quality(tmp.name)
            st.success(f"✅ {uploaded.name}  ({len(df_raw):,} rows)")

        st.markdown("---")
        st.markdown("### 🔧 Filters")

        geo_opts  = sorted(df_raw["GEO"].dropna().unique())
        geo_sel   = st.multiselect("GEO", geo_opts, default=geo_opts)

        acct_opts = sorted(df_raw["Account_name"].dropna().unique())
        acct_sel  = st.multiselect("Account", acct_opts, default=acct_opts)

        lob_opts  = sorted(df_raw["lob"].dropna().unique())
        lob_sel   = st.multiselect("LOB", lob_opts, default=lob_opts)

        dmin = df_raw["date"].min().date()
        dmax = df_raw["date"].max().date()
        drange = st.date_input("Date range", value=(dmin, dmax),
                               min_value=dmin, max_value=dmax)
        d0, d1 = (drange[0], drange[1]) if len(drange) == 2 else (dmin, dmax)

        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        tier_method = st.radio(
            "Performance tier method",
            ["Score thresholds (85 / 95%)", "Equal thirds (tertile)"],
            help="Thresholds give meaningful ranges. Tertile forces equal group sizes.",
        )

    # ── FILTER DATA ──────────────────────────────────────────────────────────
    df = df_raw[
        df_raw["GEO"].isin(geo_sel) &
        df_raw["Account_name"].isin(acct_sel) &
        df_raw["lob"].isin(lob_sel) &
        (df_raw["date"].dt.date >= d0) &
        (df_raw["date"].dt.date <= d1)
    ].copy()

    if df.empty:
        st.warning("⚠️ No data for the current filters.")
        st.stop()

    emp = build_emp(df, tier_method)
    tier_counts = emp["perf_tier"].value_counts()

    # ── TABS ─────────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "📊 Overview",
        "📈 Score Distribution",
        "⏱️ Trends",
        "🎯 ELRP Performance",
        "🏢 Account & LOB",
        "⬇️ Download",
    ])

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 1  OVERVIEW
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[0]:
        n_emp   = emp["GLOBAL_ID"].nunique()
        n_evals = len(df)
        avg_qa  = df["qa_pct_capped"].mean()
        compl   = (1 - df["base_points_achieved"].isnull().mean()) * 100
        bonus   = int((df["qa_pct"] > 100).sum())
        n_acct  = df["Account_name"].nunique()

        st.markdown(f"""
        <div class="kpi-grid">
          <div class="kpi-card">
            <p class="kpi-value">{n_emp:,}</p>
            <p class="kpi-label">Employees</p>
            <p class="kpi-sub">In filtered view</p>
          </div>
          <div class="kpi-card">
            <p class="kpi-value">{n_evals:,}</p>
            <p class="kpi-label">QA Evaluations</p>
            <p class="kpi-sub">Jan 2025 – Apr 2026</p>
          </div>
          <div class="kpi-card">
            <p class="kpi-value">{avg_qa:.1f}%</p>
            <p class="kpi-label">Overall Avg QA</p>
            <p class="kpi-sub">Normalised & capped at 100%</p>
          </div>
          <div class="kpi-card">
            <p class="kpi-value">{compl:.1f}%</p>
            <p class="kpi-label">Data Completeness</p>
            <p class="kpi-sub">Non-null base scores</p>
          </div>
          <div class="kpi-card">
            <p class="kpi-value">{n_acct}</p>
            <p class="kpi-label">Active Accounts</p>
            <p class="kpi-sub">In filtered view</p>
          </div>
          <div class="kpi-card">
            <p class="kpi-value">{bonus:,}</p>
            <p class="kpi-label">Bonus-Point Rows</p>
            <p class="kpi-sub">Score exceeds scorecard max</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        callout(
            "💡 <strong>How scores are calculated:</strong> "
            "<code>qa_pct = base_points_achieved / max_base_points × 100</code>. "
            "max_base_points varies by account/LOB scorecard (1, 8, 16, 84, 100, 200, 500…). "
            "All charts use this normalised % capped at 100 so different scorecards are comparable.",
            "info"
        )

        # ── GEO split + account pie ──
        c1, c2 = st.columns(2)

        with c1:
            sh("Evaluations & Avg QA by Geography",
               "Volume (bars) vs average normalised QA score (diamond markers)")
            geo_agg = df.groupby("GEO").agg(
                Evaluations=("GLOBAL_ID","count"),
                Employees=("GLOBAL_ID","nunique"),
                Avg_QA=("qa_pct_capped","mean"),
            ).reset_index().sort_values("Evaluations", ascending=False)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=geo_agg["GEO"], y=geo_agg["Evaluations"],
                name="Evaluations",
                marker_color=P["blue"], opacity=0.82,
                text=geo_agg["Evaluations"].apply(lambda x: f"{x:,}"),
                textposition="outside",
            ))
            fig.add_trace(go.Scatter(
                x=geo_agg["GEO"], y=geo_agg["Avg_QA"],
                name="Avg QA %", yaxis="y2",
                mode="markers",
                marker=dict(color=P["amber"], size=16, symbol="diamond",
                            line=dict(color="white", width=2)),
            ))
            fig.update_layout(
                template=T, height=320, margin=dict(t=10, b=40),
                yaxis=dict(title="Evaluations", gridcolor="#f1f5f9"),
                yaxis2=dict(title="Avg QA (%)", overlaying="y", side="right",
                            range=[0,110], showgrid=False),
                legend=dict(orientation="h", y=1.08, x=0),
                plot_bgcolor="white", paper_bgcolor="white",
            )
            st.plotly_chart(fig, use_container_width=True)
            callout(
                "PHP contributes 86.5% of evaluations. IND (Aetna PCC) uses binary "
                "0/1 scoring — these two geographies cannot be directly compared without "
                "noting the scorecard difference.",
                "warn"
            )

        with c2:
            sh("Account Mix", "Share of total evaluations by client account")
            acct_agg = (df.groupby("Account_name")["GLOBAL_ID"]
                          .count().reset_index()
                          .rename(columns={"GLOBAL_ID":"Evaluations","Account_name":"Account"})
                          .sort_values("Evaluations", ascending=False))

            fig = px.pie(
                acct_agg, names="Account", values="Evaluations",
                hole=0.52, template=T,
                color_discrete_sequence=[
                    P["blue"], P["sky"], P["teal"],
                    P["amber"], P["violet"], P["gray"],
                    "#6366f1","#14b8a6","#f59e0b","#ef4444","#8b5cf6","#06b6d4"
                ],
            )
            fig.update_traces(textposition="outside", textinfo="percent+label",
                              textfont_size=11)
            fig.update_layout(height=320, margin=dict(t=10,b=10),
                              showlegend=False,
                              paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
            callout(
                "HUMANA accounts for 41% of all evaluations. Small accounts like "
                "PERSPECTA, RADIOLOGY PARTNERS and MOLINA have &lt;100 evaluations each — "
                "treat their averages with caution.",
                "info"
            )

        # ── Tier summary ──
        sh("Performance Tier Summary",
           "Employees split into Low / Mid / High by average QA score")

        tier_tbl = emp.groupby("perf_tier").agg(
            Employees=("GLOBAL_ID","count"),
            Avg_QA=("avg_qa","mean"),
            Avg_Evals=("n_evals","mean"),
            Score_StdDev=("qa_std","mean"),
        ).reindex(["Low","Mid","High"]).reset_index()

        c1, c2, c3 = st.columns(3)
        for col, tier, bg, border in zip(
            [c1, c2, c3],
            ["Low","Mid","High"],
            [P["low_bg"], P["mid_bg"], P["high_bg"]],
            [P["low"], P["mid"], P["high"]],
        ):
            row = tier_tbl[tier_tbl["perf_tier"]==tier]
            if row.empty: continue
            r = row.iloc[0]
            pct_emp = r["Employees"] / len(emp) * 100
            with col:
                st.markdown(f"""
                <div class="kpi-card" style="border-left:4px solid {border};
                     background:{bg};">
                  <p class="kpi-value" style="color:{border}">
                    {int(r['Employees'])}
                    <span style="font-size:13px;color:#6b7280;">({pct_emp:.0f}%)</span>
                  </p>
                  <p class="kpi-label">{tier} Performers</p>
                  <p class="kpi-sub">Avg QA: {r['Avg_QA']:.1f}%
                     &nbsp;|&nbsp; σ {r['Score_StdDev']:.1f}</p>
                </div>
                """, unsafe_allow_html=True)

        callout(
            f"Using score-based thresholds — Low &lt;85%, Mid 85–95%, High &gt;95%: "
            f"<strong>{tier_counts.get('Low',0):,} low performers</strong> are the "
            f"highest-priority targets for coaching intervention under the ELRP model. "
            f"High performers cluster near 100% with minimal variance.",
            "success"
        )

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 2  SCORE DISTRIBUTION
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[1]:
        sh("Per-Employee QA Score Distribution",
           "Each employee's average QA score across all their evaluations")

        callout(
            "The distribution is <strong>heavily left-skewed</strong>: median is near 100% "
            "while a long tail below 85% pulls the mean down. This means the bulk of the "
            "workforce performs well — but the low-performing tail has outsized impact on "
            "client SLA compliance and is the key target for ELRP intervention.",
            "info"
        )

        c1, c2 = st.columns(2)

        with c1:
            fig = px.histogram(
                emp, x="avg_qa", nbins=40,
                template=T,
                color_discrete_sequence=[P["blue"]],
                labels={"avg_qa": "Avg QA Score (%)"},
                title="Distribution of Per-Employee Avg QA",
                opacity=0.85,
            )
            fig.add_vline(x=emp["avg_qa"].mean(), line_dash="dash",
                          line_color=P["amber"], line_width=2,
                          annotation_text=f"Mean {emp['avg_qa'].mean():.1f}%",
                          annotation_position="top right",
                          annotation_font_color=P["amber"])
            fig.add_vline(x=emp["avg_qa"].median(), line_dash="dot",
                          line_color=P["teal"], line_width=2,
                          annotation_text=f"Median {emp['avg_qa'].median():.1f}%",
                          annotation_position="top left",
                          annotation_font_color=P["teal"])
            fig.update_layout(height=340, margin=dict(t=40,b=40),
                              plot_bgcolor="white", paper_bgcolor="white",
                              yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig = px.box(
                emp, x="perf_tier", y="avg_qa",
                color="perf_tier",
                color_discrete_map=TIER_COLORS,
                category_orders={"perf_tier":["Low","Mid","High"]},
                template=T,
                labels={"perf_tier":"Tier","avg_qa":"Avg QA (%)"},
                title="QA Score Spread by Performance Tier",
                points="outliers",
            )
            fig.update_layout(height=340, showlegend=False, margin=dict(t=40,b=40),
                              plot_bgcolor="white", paper_bgcolor="white",
                              yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig, use_container_width=True)

        callout(
            "Low performers show the widest spread (σ ≈ 10–15pp), indicating inconsistent "
            "execution. High performers cluster tightly near 100%, confirming reliable and "
            "repeatable performance. Under ELRP, high variance in the low tier signals "
            "<strong>elevated retention risk</strong> — inconsistency often precedes attrition.",
            "warn"
        )

        # ── Violin by GEO ──
        sh("Score Distribution by Geography",
           "Full score distribution shape per GEO — not just the average")

        fig = px.violin(
            df, x="GEO", y="qa_pct_capped",
            color="GEO", box=True, points=False,
            template=T,
            color_discrete_map={"PHP": P["blue"], "IND": P["red"]},
            labels={"qa_pct_capped":"QA Score (%)","GEO":"Geography"},
            title="QA Score Distribution by GEO",
        )
        fig.update_layout(height=380, showlegend=False, margin=dict(t=40,b=40),
                          plot_bgcolor="white", paper_bgcolor="white",
                          yaxis=dict(gridcolor="#f1f5f9"))
        st.plotly_chart(fig, use_container_width=True)

        callout(
            "PHP shows a bimodal shape — a dense cluster at 100% and a secondary cluster "
            "at 30–50% driven by HUMANA CCC's smaller scorecard. "
            "IND concentrates at 0% and 100% because Aetna PCC uses binary pass/fail scoring. "
            "<strong>Never aggregate IND and PHP raw scores without accounting for this.</strong>",
            "danger"
        )

        # ── Account bar ──
        sh("Avg QA Score by Account",
           "Sorted low to high — muted bars have fewer than 200 evaluations (lower confidence)")

        acct_qa = df.groupby("Account_name").agg(
            Avg_QA=("qa_pct_capped","mean"),
            Evaluations=("GLOBAL_ID","count"),
            Employees=("GLOBAL_ID","nunique"),
        ).reset_index().sort_values("Avg_QA")
        acct_qa["confidence"] = acct_qa["Evaluations"].apply(
            lambda x: "≥ 200 evaluations" if x >= 200 else "< 200 evaluations")

        fig = px.bar(
            acct_qa, x="Avg_QA", y="Account_name",
            orientation="h",
            color="confidence",
            color_discrete_map={
                "≥ 200 evaluations": P["blue"],
                "< 200 evaluations": "#94a3b8",
            },
            template=T,
            hover_data={"Evaluations":True,"Employees":True},
            labels={"Avg_QA":"Avg QA (%)","Account_name":"Account","confidence":""},
            title="Avg QA Score by Account",
            text=acct_qa["Avg_QA"].round(1).astype(str) + "%",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(height=420, margin=dict(t=40,l=10,r=120),
                          legend=dict(orientation="h", y=1.05, x=0),
                          plot_bgcolor="white", paper_bgcolor="white",
                          xaxis=dict(gridcolor="#f1f5f9"))
        st.plotly_chart(fig, use_container_width=True)

        callout(
            "COVENTRY, ENLYTE and AETNA consistently exceed 95% — healthy accounts. "
            "HUMANA CCC scores lower due to a more complex and variable scorecard. "
            "Small accounts (PERSPECTA, RADIOLOGY PARTNERS, MOLINA) need more evaluation "
            "volume before conclusions can be drawn.",
            "warn"
        )

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 3  TRENDS
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[2]:
        sh("QA Score Trend Over Time",
           "Month-over-month performance evolution — a declining trend precedes attrition risk")

        callout(
            "Trend analysis maps to the <strong>Retention</strong> dimension of ELRP. "
            "A declining trend in an account or LOB often precedes an attrition wave. "
            "Stable or improving trends indicate successful onboarding and coaching. "
            "Sudden single-month dips may reflect a process change, new product launch, or "
            "a data batch issue — always cross-check against evaluation volume.",
            "info"
        )

        freq = st.radio("Aggregation:", ["Monthly","Quarterly"], horizontal=True)
        xcol = "month_dt" if freq == "Monthly" else "quarter"

        if freq == "Monthly":
            geo_trend = df.groupby(["month_dt","GEO"])["qa_pct_capped"].mean().reset_index()
            geo_trend.rename(columns={"qa_pct_capped":"Avg_QA"}, inplace=True)
            vol_trend = df.groupby("month_dt").agg(
                Evals=("GLOBAL_ID","count"),
                Avg_QA=("qa_pct_capped","mean")).reset_index()
            acct_trend = df.groupby(["month_dt","Account_name"])["qa_pct_capped"].mean().reset_index()
            acct_trend.rename(columns={"qa_pct_capped":"Avg_QA"}, inplace=True)
        else:
            geo_trend = df.groupby(["quarter","GEO"])["qa_pct_capped"].mean().reset_index()
            geo_trend.rename(columns={"qa_pct_capped":"Avg_QA"}, inplace=True)
            vol_trend = df.groupby("quarter").agg(
                Evals=("GLOBAL_ID","count"),
                Avg_QA=("qa_pct_capped","mean")).reset_index()
            acct_trend = df.groupby(["quarter","Account_name"])["qa_pct_capped"].mean().reset_index()
            acct_trend.rename(columns={"qa_pct_capped":"Avg_QA"}, inplace=True)

        # GEO trend
        fig = px.line(
            geo_trend, x=xcol, y="Avg_QA", color="GEO", markers=True,
            template=T,
            color_discrete_map={"PHP": P["blue"], "IND": P["red"]},
            labels={"Avg_QA":"Avg QA (%)","GEO":"Geography"},
            title=f"QA Score Trend by GEO ({freq})",
        )
        fig.update_layout(height=340, margin=dict(t=40,b=40),
                          yaxis=dict(range=[0,110], gridcolor="#f1f5f9"),
                          plot_bgcolor="white", paper_bgcolor="white",
                          legend=dict(orientation="h",y=1.1))
        st.plotly_chart(fig, use_container_width=True)

        # Volume vs QA
        sh("Evaluation Volume vs Avg QA Score",
           "Are we evaluating more people — and is quality improving alongside volume?")

        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Bar(
            x=vol_trend[xcol], y=vol_trend["Evals"],
            name="Evaluations", marker_color=P["sky"], opacity=0.45,
        ), secondary_y=False)
        fig2.add_trace(go.Scatter(
            x=vol_trend[xcol], y=vol_trend["Avg_QA"],
            name="Avg QA %", mode="lines+markers",
            line=dict(color=P["primary"], width=2.5),
            marker=dict(size=7, color=P["primary"]),
        ), secondary_y=True)
        fig2.update_layout(
            template=T, height=320, margin=dict(t=20,b=40),
            legend=dict(orientation="h",y=1.08,x=0),
            plot_bgcolor="white", paper_bgcolor="white",
        )
        fig2.update_yaxes(title_text="Evaluations", secondary_y=False,
                          gridcolor="#f1f5f9")
        fig2.update_yaxes(title_text="Avg QA (%)", secondary_y=True,
                          range=[0,110], showgrid=False)
        st.plotly_chart(fig2, use_container_width=True)

        callout(
            "A spike in volume without a QA drop means the team is scaling without "
            "compromising standards — a positive signal. If volume rises and QA falls, "
            "it could indicate reviewer fatigue, rushed coaching, or a batch of "
            "historical records (March 2026 shows a 3× volume spike — verify with client).",
            "warn"
        )

        # Account trends
        sh("Account-Level Monthly QA Trend",
           "Top 6 accounts by evaluation volume")

        top6 = df.groupby("Account_name")["GLOBAL_ID"].count().nlargest(6).index.tolist()
        at   = acct_trend[acct_trend["Account_name"].isin(top6)]

        fig3 = px.line(
            at, x=xcol, y="Avg_QA", color="Account_name", markers=True,
            template=T,
            color_discrete_sequence=[P["blue"],P["teal"],P["amber"],
                                     P["violet"],P["sky"],P["red"]],
            labels={"Avg_QA":"Avg QA (%)","Account_name":"Account"},
            title=f"Monthly QA Trend — Top 6 Accounts ({freq})",
        )
        fig3.update_layout(height=360, margin=dict(t=40,b=40),
                           yaxis=dict(range=[0,110], gridcolor="#f1f5f9"),
                           plot_bgcolor="white", paper_bgcolor="white",
                           legend=dict(orientation="h",y=1.12, x=0))
        st.plotly_chart(fig3, use_container_width=True)

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 4  ELRP PERFORMANCE
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[3]:
        sh("ELRP Performance Intelligence",
           "Employee Fitment · Learnability · Retention · Performance")

        callout(
            "<strong>How QA data maps to ELRP:</strong> "
            "(E) <em>Employee Fitment</em> — is this person in the right account/LOB? "
            "(L) <em>Learnability</em> — is their QA improving over time? "
            "(R) <em>Retention risk</em> — is QA declining or highly variable? "
            "(P) <em>Performance</em> — do they consistently hit the SLA threshold?",
            "info"
        )

        # ── P: Consistency ──
        sh("Performance Consistency (P)",
           "Score variability per employee — high std dev = unpredictable quality = retention risk")

        c1, c2 = st.columns(2)

        with c1:
            fig = px.scatter(
                emp, x="avg_qa", y="qa_std",
                color="perf_tier",
                color_discrete_map=TIER_COLORS,
                category_orders={"perf_tier":["Low","Mid","High"]},
                template=T, opacity=0.6,
                labels={"avg_qa":"Avg QA (%)","qa_std":"Score Std Dev","perf_tier":"Tier"},
                title="Avg QA vs Score Variability — all employees",
                hover_data={"GLOBAL_ID":True,"n_evals":True},
            )
            fig.add_vline(x=85, line_dash="dash", line_color=P["red"], line_width=1.5,
                          annotation_text="85% threshold", annotation_position="top left",
                          annotation_font_color=P["red"])
            fig.add_vline(x=95, line_dash="dash", line_color=P["high"], line_width=1.5,
                          annotation_text="95% threshold", annotation_position="top right",
                          annotation_font_color=P["high"])
            fig.update_layout(height=360, margin=dict(t=40,b=40),
                              plot_bgcolor="white", paper_bgcolor="white",
                              yaxis=dict(gridcolor="#f1f5f9"),
                              xaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            tier_c = emp.groupby("perf_tier").agg(
                Avg_StdDev=("qa_std","mean"),
                Employees=("GLOBAL_ID","count"),
            ).reindex(["Low","Mid","High"]).reset_index()

            fig = px.bar(
                tier_c, x="perf_tier", y="Avg_StdDev",
                color="perf_tier",
                color_discrete_map=TIER_COLORS,
                text=tier_c["Avg_StdDev"].round(1),
                template=T,
                labels={"perf_tier":"Tier","Avg_StdDev":"Avg Score Std Dev"},
                title="Score Consistency by Tier (lower = better)",
            )
            fig.update_traces(textposition="outside", texttemplate="%{text:.1f}")
            fig.update_layout(height=360, showlegend=False, margin=dict(t=40,b=40),
                              plot_bgcolor="white", paper_bgcolor="white",
                              yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig, use_container_width=True)

        callout(
            "Low performers don't just score lower — they score <em>less consistently</em>. "
            "A high std dev in the low tier signals employees with occasional good evaluations "
            "but no sustained quality. Under ELRP, these are flagged as "
            "<strong>high retention risk</strong>: inconsistency strongly correlates with attrition.",
            "danger"
        )

        # ── L: Learnability ──
        sh("Learnability — Score Trajectory (L)",
           "Did each employee's QA improve from H1 2025 (Jan–Jun) to H2 2025 (Jul–Apr 2026)?")

        mid = pd.Timestamp("2025-07-01")
        early = df[df["date"] <  mid].groupby("GLOBAL_ID")["qa_pct_capped"].mean()
        late  = df[df["date"] >= mid].groupby("GLOBAL_ID")["qa_pct_capped"].mean()
        ldf   = pd.DataFrame({"early":early,"late":late}).dropna().reset_index()
        ldf["change"]   = ldf["late"] - ldf["early"]
        ldf["improved"] = ldf["change"] > 0
        ldf = ldf.merge(emp[["GLOBAL_ID","perf_tier"]], on="GLOBAL_ID")

        imp_pct = ldf["improved"].mean() * 100
        avg_chg = ldf["change"].mean()

        c1, c2 = st.columns(2)

        with c1:
            fig = px.histogram(
                ldf, x="change",
                color="improved",
                color_discrete_map={True: P["high"], False: P["low"]},
                nbins=50, template=T, opacity=0.82,
                labels={"change":"QA Change (pp)","improved":"Improved"},
                title="Distribution of QA Score Change (H1 → H2)",
            )
            fig.add_vline(x=0, line_dash="dash", line_color=P["gray"])
            fig.add_vline(x=avg_chg, line_dash="dot", line_color=P["amber"],
                          line_width=2,
                          annotation_text=f"Avg {avg_chg:+.1f}pp",
                          annotation_font_color=P["amber"])
            fig.update_layout(height=320, margin=dict(t=40,b=40),
                              plot_bgcolor="white", paper_bgcolor="white",
                              yaxis=dict(gridcolor="#f1f5f9"),
                              legend=dict(title=""))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            lt = ldf.groupby("perf_tier").agg(
                Avg_Change=("change","mean"),
                Improved_Pct=("improved","mean"),
                Employees=("GLOBAL_ID","count"),
            ).reindex(["Low","Mid","High"]).reset_index()

            fig = px.bar(
                lt, x="perf_tier", y="Avg_Change",
                color="perf_tier",
                color_discrete_map=TIER_COLORS,
                template=T,
                labels={"perf_tier":"Tier","Avg_Change":"Avg QA Change (pp)"},
                title="Avg QA Change H1→H2 by Tier",
                text=lt["Avg_Change"].round(1),
            )
            fig.add_hline(y=0, line_dash="dash", line_color=P["gray"])
            fig.update_traces(textposition="outside",
                              texttemplate="%{text:+.1f}pp")
            fig.update_layout(height=320, showlegend=False, margin=dict(t=40,b=40),
                              plot_bgcolor="white", paper_bgcolor="white",
                              yaxis=dict(gridcolor="#f1f5f9"))
            st.plotly_chart(fig, use_container_width=True)

        callout(
            f"<strong>{imp_pct:.1f}%</strong> of employees improved their QA in H2 vs H1 "
            f"(avg change: {avg_chg:+.1f}pp). Low performers who improve represent the highest "
            f"coaching ROI — they show the system is working. Low performers who decline are "
            f"the primary attrition risk and should trigger an ELRP intervention workflow.",
            "success" if avg_chg > 0 else "warn"
        )

        # ── E: Fitment ──
        sh("Employee Fitment — Account Coverage (E)",
           "Employees handling multiple accounts may have a fitment mismatch")

        multi  = emp[emp["n_accounts"] > 1]
        single = emp[emp["n_accounts"] == 1]

        col1, col2, col3 = st.columns(3)
        col1.metric("Single-account employees", f"{len(single):,}")
        col2.metric("Multi-account employees",  f"{len(multi):,}",
                    delta=f"{len(multi)/len(emp)*100:.1f}% of workforce")
        col3.metric("Avg QA — multi-account",   f"{multi['avg_qa'].mean():.1f}%",
                    delta=f"{multi['avg_qa'].mean()-single['avg_qa'].mean():+.1f}pp vs single")

        callout(
            "Employees covering multiple accounts show lower avg QA — context-switching between "
            "different scorecards and processes creates quality risk. "
            "Under ELRP, reducing cross-account exposure for low performers is a "
            "<strong>fitment intervention</strong> that can improve both quality and retention.",
            "warn"
        )

        acct_cov = emp.groupby("n_accounts").agg(
            Employees=("GLOBAL_ID","count"),
            Avg_QA=("avg_qa","mean"),
        ).reset_index()

        fig = px.bar(
            acct_cov, x="n_accounts", y="Employees",
            color="Avg_QA",
            color_continuous_scale=SCALE_RYG,
            range_color=[0, 100],
            text="Employees", template=T,
            labels={"n_accounts":"Accounts Handled","Employees":"Employee Count",
                    "Avg_QA":"Avg QA (%)"},
            title="Employee Count by Number of Accounts Handled",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(height=320, margin=dict(t=40,b=40),
                          plot_bgcolor="white", paper_bgcolor="white",
                          yaxis=dict(gridcolor="#f1f5f9"),
                          coloraxis_colorbar=dict(title="Avg QA (%)"))
        st.plotly_chart(fig, use_container_width=True)

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 5  ACCOUNT & LOB
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[4]:
        sh("Account × LOB Deep Dive",
           "QA performance drilled to line-of-business level")

        callout(
            "LOB-level analysis reveals that quality standards vary significantly even within "
            "the same account. HUMANA CCC and PCC use different scorecard sizes. "
            "Always use normalised qa_pct when comparing across LOBs.",
            "info"
        )

        # Heatmap
        al = df.groupby(["Account_name","lob"])["qa_pct_capped"].mean().reset_index()
        al.columns = ["Account","LOB","Avg_QA"]
        top15 = df["lob"].value_counts().nlargest(15).index.tolist()
        al_f  = al[al["LOB"].isin(top15)]
        pivot = al_f.pivot_table(index="Account", columns="LOB",
                                  values="Avg_QA", aggfunc="mean")

        fig = px.imshow(
            pivot.round(1), text_auto=".0f",
            color_continuous_scale=SCALE_RYG,
            zmin=0, zmax=100,
            template=T, aspect="auto",
            title="Avg QA Score Heatmap: Account × LOB (top 15 LOBs)",
            labels={"color":"Avg QA (%)"},
        )
        fig.update_layout(height=420, margin=dict(t=40,b=40),
                          paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

        callout(
            "Dark red cells = highest-priority intervention areas (QA consistently below 85%). "
            "Green = healthy. Yellow = candidates for targeted coaching to reach the high tier. "
            "Blank cells mean no evaluations exist for that account-LOB combination.",
            "warn"
        )

        # LOB selector
        sh("LOB Performance Ranking",
           "Select an account to see all its LOBs ranked by avg QA")

        sel_acct = st.selectbox("Select Account:", sorted(df["Account_name"].unique()))
        lob_qa = df[df["Account_name"]==sel_acct].groupby("lob").agg(
            Avg_QA=("qa_pct_capped","mean"),
            Evaluations=("GLOBAL_ID","count"),
            Employees=("GLOBAL_ID","nunique"),
        ).reset_index().sort_values("Avg_QA")

        # Color each bar based on its own value using a marker array — NO zmin/zmax on bar
        def qa_color(v):
            if v < 85:   return P["low"]
            if v < 95:   return P["mid"]
            return P["high"]

        lob_qa["bar_color"] = lob_qa["Avg_QA"].apply(qa_color)

        fig = go.Figure(go.Bar(
            x=lob_qa["Avg_QA"],
            y=lob_qa["lob"],
            orientation="h",
            marker_color=lob_qa["bar_color"].tolist(),
            text=[f"{v:.1f}%" for v in lob_qa["Avg_QA"]],
            textposition="outside",
            customdata=np.stack(
                [lob_qa["Evaluations"], lob_qa["Employees"]], axis=-1),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Avg QA: %{x:.1f}%<br>"
                "Evaluations: %{customdata[0]:,}<br>"
                "Employees: %{customdata[1]:,}<extra></extra>"
            ),
        ))
        fig.update_layout(
            template=T, height=max(280, len(lob_qa)*34),
            title=f"{sel_acct} — QA Score by LOB",
            xaxis=dict(range=[0, 115], gridcolor="#f1f5f9",
                       title="Avg QA (%)"),
            yaxis=dict(title=""),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=40, l=10, r=100),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Scorecard table
        sh("Scorecard Ceiling by Account × LOB",
           "max_base_points shows which scorecard each LOB uses — direct raw score comparison is invalid")

        scale_df = (df.groupby(["Account_name","lob","max_base_points"])
                      .size().reset_index(name="Evaluations")
                      .sort_values(["Account_name","Evaluations"], ascending=[True,False]))

        with st.expander("🔍 View max_base_points breakdown"):
            st.dataframe(
                scale_df.rename(columns={
                    "Account_name": "Account",
                    "lob": "LOB",
                    "max_base_points": "Scorecard Ceiling (max_base_points)",
                }),
                use_container_width=True, height=380,
            )
            callout(
                "An employee scoring 8/8 and one scoring 92/100 are both 100% after normalisation "
                "but come from completely different scorecard forms. This table shows how many "
                "distinct scorecards exist per LOB.",
                "warn"
            )

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 6  DOWNLOAD
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[5]:
        sh("Download JSON Report",
           "Export all chart datasets, KPIs and filters as a structured JSON")

        callout(
            "The JSON is organised by section. Each chart entry contains a title, "
            "description, and all underlying data as an array of records. "
            "Use it to feed into an LLM, a BI tool, or share with stakeholders.",
            "info"
        )

        c1, c2 = st.columns([1,2])
        with c1:
            st.markdown("### 📦 Contents")
            st.markdown("""
- **Dataset Health** — GEO, account, missing data  
- **Score Distributions** — tiers, GEO, per-account  
- **Monthly Trends** — GEO and volume  
- **ELRP Performance** — consistency, learnability, fitment  
- **Account × LOB** — heatmap data  
            """)
            generate = st.button("🔄 Generate Report JSON", type="primary",
                                 use_container_width=True)

        with c2:
            st.markdown("### 👁️ JSON structure")
            st.json({
                "generated_at": "<ISO timestamp>",
                "elrp_version": "v1.0-2025",
                "filters": {"geo":["PHP","IND"],"account":["..."],"lob":["..."]},
                "sections": [{
                    "section_title": "<section name>",
                    "description": "<coverage>",
                    "charts": [{
                        "chart_title": "<name>",
                        "description": "<what the data shows>",
                        "data": [{"column": "value"}],
                        "annotations": {"key": "summary value"},
                    }],
                }],
            })

        if generate:
            with st.spinner("Building report…"):
                rpt     = build_report(df, emp, geo_sel, acct_sel, lob_sel)
                js      = json.dumps(rpt, default=safe_json, indent=2, ensure_ascii=False)
                ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
                n_ch    = sum(len(s["charts"]) for s in rpt["sections"])

            st.success(
                f"✅ Ready — {len(rpt['sections'])} sections · "
                f"{n_ch} chart datasets · {len(js):,} characters"
            )
            st.download_button(
                "⬇️ Download ELRP Quality Report JSON",
                data=js.encode("utf-8"),
                file_name=f"elrp_quality_report_{ts}.json",
                mime="application/json",
                use_container_width=True,
            )


if __name__ == "__main__":
    main()