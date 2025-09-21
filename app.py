import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.graph_objects as go
import calendar

CSV_FILE = "trades.csv"
INVEST_CSV = "investment.csv"

def init_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["Date", "Symbol", "Side", "Quantity", "Price", "Net P&L", "Pips"])
        df.to_csv(CSV_FILE, index=False)

def init_investment():
    if not os.path.exists(INVEST_CSV):
        pd.DataFrame([{"Date": datetime.today().strftime("%Y-%m-%d"), "Amount": 0.0}]).to_csv(INVEST_CSV, index=False)

def get_investment():
    df = pd.read_csv(INVEST_CSV)
    return df["Amount"].sum()

def add_investment(amount):
    df = pd.read_csv(INVEST_CSV)
    df = pd.concat([df, pd.DataFrame([{"Date": datetime.today().strftime("%Y-%m-%d"), "Amount": amount}])], ignore_index=True)
    df.to_csv(INVEST_CSV, index=False)

def add_trade_form():
    with st.form("trade_form"):
        date = st.date_input("Date", value=datetime.today())
        symbol = st.text_input("Symbol", key="symbol", max_chars=10)
        side = st.selectbox("Side", ["Buy", "Sell"], key="side")
        quantity = st.text_input("Quantity", key="quantity", max_chars=10)
        price = st.text_input("Price", key="price", max_chars=10)
        pnl = st.text_input("Net P&L", key="pnl", max_chars=10)
        pips = st.text_input("Pips", key="pips", max_chars=10)  # <-- New field
        submitted = st.form_submit_button("Add Trade")
        if submitted:
            try:
                quantity_val = float(quantity)
                price_val = float(price)
                pnl_val = float(pnl)
                pips_val = float(pips)
                return {
                    "Date": date.strftime("%Y-%m-%d"),
                    "Symbol": symbol,
                    "Side": side,
                    "Quantity": quantity_val,
                    "Price": price_val,
                    "Net P&L": pnl_val,
                    "Pips": pips_val
                }
            except ValueError:
                st.error("Please enter valid numbers for Quantity, Price, Net P&L, and Pips.")
    return None

def save_trade(trade_data):
    df = pd.read_csv(CSV_FILE)
    df = pd.concat([df, pd.DataFrame([trade_data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    # --- Update investment automatically ---
    add_investment(trade_data["Net P&L"])

def load_trades():
    return pd.read_csv(CSV_FILE)

def load_investments():
    return pd.read_csv(INVEST_CSV)

def save_investments(df):
    df.to_csv(INVEST_CSV, index=False)

def display_investments_table(df):
    for idx, row in df.iterrows():
        cols = st.columns([2, 2, 1, 1])
        cols[0].markdown(f"<div style='padding:4px;text-align:center'>{row['Date']}</div>", unsafe_allow_html=True)
        cols[1].markdown(f"<div style='padding:4px;text-align:center'>{row['Amount']}</div>", unsafe_allow_html=True)
        edit_btn = cols[2].button("Edit", key=f"edit_invest_{idx}")
        delete_btn = cols[3].button("Delete", key=f"delete_invest_{idx}")
        if edit_btn:
            st.session_state['edit_invest_row'] = idx
        if delete_btn:
            st.session_state['delete_invest_row'] = idx

def investment_edit_form(row):
    with st.form("edit_investment_form"):
        date = st.text_input("Date", value=row["Date"])
        amount = st.text_input("Amount", value=str(row["Amount"]))
        submitted = st.form_submit_button("Update")
        if submitted:
            try:
                amount_val = float(amount)
                return {"Date": date, "Amount": amount_val}
            except ValueError:
                st.error("Please enter a valid number for the amount.")
    return None

def calculate_statistics():
    df = pd.read_csv(CSV_FILE)
    stats = {
        "Total Trades": len(df),
        "Total P&L": df["Net P&L"].sum(),
        "Win Rate": (df["Net P&L"] > 0).mean() * 100 if len(df) > 0 else 0,
        "Avg Win": df[df["Net P&L"] > 0]["Net P&L"].mean() if (df["Net P&L"] > 0).any() else 0,
        "Avg Loss": df[df["Net P&L"] < 0]["Net P&L"].mean() if (df["Net P&L"] < 0).any() else 0,
    }
    return stats

def display_statistics(stats):
    st.metric("Total Trades", stats["Total Trades"])
    st.metric("Total P&L", f"${stats['Total P&L']:.2f}")
    st.metric("Win Rate", f"{stats['Win Rate']:.2f}%")
    st.metric("Avg Win", f"${stats['Avg Win']:.2f}")
    st.metric("Avg Loss", f"${stats['Avg Loss']:.2f}")

def pie_chart(trades):
    win = (trades["Net P&L"] > 0).sum()
    loss = (trades["Net P&L"] < 0).sum()
    fig = go.Figure(data=[go.Pie(labels=['Win', 'Loss'], values=[win, loss], marker_colors=['#3498db', '#9b59b6'])])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250)
    st.plotly_chart(fig, use_container_width=True)

def daily_pnl_chart(trades):
    daily_win = trades[trades["Net P&L"] > 0].groupby("Date")["Net P&L"].sum().reset_index()
    daily_loss = trades[trades["Net P&L"] < 0].groupby("Date")["Net P&L"].sum().reset_index()

    all_dates = sorted(set(trades["Date"]))
    win_map = dict(zip(daily_win["Date"], daily_win["Net P&L"]))
    loss_map = dict(zip(daily_loss["Date"], daily_loss["Net P&L"]))

    win_values = [win_map.get(date, 0) for date in all_dates]
    loss_values = [loss_map.get(date, 0) for date in all_dates]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=all_dates, y=win_values,
        name="Winning P&L",
        marker_color="#3498db"  # Blue
    ))
    fig.add_trace(go.Bar(
        x=all_dates, y=loss_values,
        name="Losing P&L",
        marker_color="#9b59b6"  # Purple
    ))
    fig.update_layout(
        barmode='group',
        margin=dict(l=0, r=0, t=0, b=0),
        height=180,
        xaxis_title="Date",
        yaxis_title="Net P&L"
    )
    st.plotly_chart(fig, use_container_width=True)

def calculate_zella_score(trades):
    win_rate = (trades["Net P&L"] > 0).mean() * 100 if len(trades) > 0 else 0
    profit_factor = trades[trades["Net P&L"] > 0]["Net P&L"].sum() / abs(trades[trades["Net P&L"] < 0]["Net P&L"].sum()) if (trades["Net P&L"] < 0).any() else 0
    avg_winloss = trades["Net P&L"].mean() if len(trades) > 0 else 0
    max_drawdown = trades["Net P&L"].min() if len(trades) > 0 else 0
    recovery_factor = trades["Net P&L"].sum() / abs(max_drawdown) if max_drawdown < 0 else 0
    consistency = win_rate  # For demo, use win_rate as consistency

    radar_metrics = [
        min(win_rate, 100),
        min(profit_factor * 20, 100),
        min(avg_winloss * 5, 100),
        min(abs(max_drawdown) * 0.5, 100),
        min(recovery_factor * 20, 100),
        min(consistency, 100)
    ]
    zella_score = sum(radar_metrics) / len(radar_metrics)
    return radar_metrics, zella_score

def zella_score_section(trades):
    radar_metrics, zella_score = calculate_zella_score(trades)
    categories = ["Win %", "Profit factor", "Avg win/loss", "Max drawdown", "Recovery factor", "Consistency"]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=radar_metrics,
        theta=categories,
        fill='toself',
        line_color='purple',
        fillcolor='rgba(155,89,182,0.5)'
    ))
    fig.update_layout(
        polar=dict(bgcolor="#181818"),
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=300
    )

    st.markdown("#### Zella Score")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"""
        <div style="margin-top: -30px;">
            <span style="font-size: 1.2em;">Your Zella Score</span>
            <div style="background: linear-gradient(90deg, #e74c3c, #f1c40f, #2ecc71); height: 18px; border-radius: 8px; margin: 8px 0; position: relative;">
                <div style="position: absolute; left: {zella_score}%; top: -8px;">
                    <span style="color: #fff; background: #222; border-radius: 4px; padding: 2px 8px;">{zella_score:.2f}</span>
                </div>
                <div style="width: {zella_score}%; height: 18px; background: rgba(155,89,182,0.7); border-radius: 8px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_trades(trades):
    # --- Table Header ---
    header_cols = st.columns([2,2,2,2,2,2,2,1,1])
    headers = ["Date", "Symbol", "Side", "Quantity", "Price", "Pips", "Net P&L", "Edit", "Delete"]
    for i, col in enumerate(headers):
        header_cols[i].markdown(f"<b style='color:#FFD700'>{col}</b>", unsafe_allow_html=True)

    # --- Table Rows ---
    for idx, row in trades.iterrows():
        cols = st.columns([2,2,2,2,2,2,2,1,1])
        for i, col_name in enumerate(["Date", "Symbol", "Side", "Quantity", "Price", "Pips", "Net P&L"]):
            if col_name == "Net P&L":
                if row[col_name] > 0:
                    color = "#27ae60"   # Green
                    text_color = "white"
                elif row[col_name] < 0:
                    color = "#c0392b"   # Red
                    text_color = "white"
                else:
                    color = "white"
                    text_color = "black"
                cols[i].markdown(
                    f"<div style='background-color:{color};color:{text_color};padding:4px;border-radius:4px;text-align:center'>{row[col_name]}</div>",
                    unsafe_allow_html=True)
            else:
                cols[i].markdown(f"<div style='padding:4px;text-align:center'>{row[col_name]}</div>", unsafe_allow_html=True)
        # Add Edit and Delete buttons
        edit_btn = cols[7].button("✏️", key=f"edit_trade_{idx}", help="Edit this trade")
        delete_btn = cols[8].button("🗑️", key=f"delete_trade_{idx}", help="Delete this trade")
        if edit_btn:
            st.session_state['edit_trade_row'] = idx
        if delete_btn:
            st.session_state['delete_trade_row'] = idx

    # --- Daily Total P&L ---
    if not trades.empty:
        trades["Date"] = pd.to_datetime(trades["Date"])
        daily_pnl = trades.groupby(trades["Date"].dt.date)["Net P&L"].sum()
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<b style='color:#FFD700'>Daily Total P&L:</b>", unsafe_allow_html=True)
        for day, pnl in daily_pnl.items():
            color = "#3498db" if pnl > 0 else "#9b59b6" if pnl < 0 else "#444"
            st.markdown(
                f"<span style='color:{color};font-weight:bold'>{day}: {pnl:.2f}</span>",
                unsafe_allow_html=True
            )

def trade_edit_form(row):
    with st.form("edit_trade_form"):
        date = st.date_input("Date", value=pd.to_datetime(row["Date"]))
        symbol = st.text_input("Symbol", value=row["Symbol"])
        side = st.selectbox("Side", ["Buy", "Sell"], index=0 if row["Side"]=="Buy" else 1)
        quantity = st.text_input("Quantity", value=str(row["Quantity"]))
        price = st.text_input("Price", value=str(row["Price"]))
        pnl = st.text_input("Net P&L", value=str(row["Net P&L"]))
        pips = st.text_input("Pips", value=str(row.get("Pips", "")))
        submitted = st.form_submit_button("Update")
        if submitted:
            try:
                quantity_val = float(quantity)
                price_val = float(price)
                pnl_val = float(pnl)
                pips_val = float(pips)
                return {
                    "Date": date.strftime("%Y-%m-%d"),
                    "Symbol": symbol,
                    "Side": side,
                    "Quantity": quantity_val,
                    "Price": price_val,
                    "Net P&L": pnl_val,
                    "Pips": pips_val
                }
            except ValueError:
                st.error("Please enter valid numbers for Quantity, Price, Net P&L, and Pips.")
    return None

def kpi_cards(trades):
    total_trades = len(trades)
    total_pnl = trades["Net P&L"].sum() if not trades.empty else 0
    win_trades = trades[trades["Net P&L"] > 0]
    loss_trades = trades[trades["Net P&L"] < 0]
    win_rate = (len(win_trades) / total_trades * 100) if total_trades else 0
    avg_win = win_trades["Net P&L"].mean() if not win_trades.empty else 0
    avg_loss = loss_trades["Net P&L"].mean() if not loss_trades.empty else 0
    profit_factor = win_trades["Net P&L"].sum() / abs(loss_trades["Net P&L"].sum()) if not loss_trades.empty else 0
    current_investment = get_investment()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Trades", total_trades)
    c2.metric("Total P&L", f"${total_pnl:.2f}")
    c3.metric("Win Rate", f"{win_rate:.2f}%")
    c4.metric("Avg Win", f"${avg_win:.2f}")
    c5.metric("Avg Loss", f"${avg_loss:.2f}")
    c6.metric("Current Investment", f"${current_investment:.2f}")

def profit_factor_daywin_chart(trades):
    if trades.empty:
        return
    trades_by_day = trades.groupby("Date")
    days = []
    profit_factors = []
    win_percents = []
    for day, group in trades_by_day:
        win = group[group["Net P&L"] > 0]["Net P&L"].sum()
        loss = abs(group[group["Net P&L"] < 0]["Net P&L"].sum())
        pf = win / loss if loss > 0 else win
        win_pct = (group["Net P&L"] > 0).mean() * 100
        days.append(day)
        profit_factors.append(pf)
        win_percents.append(win_pct)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=days, y=profit_factors, name="Profit Factor", marker_color="#3498db"))
    fig.add_trace(go.Scatter(x=days, y=win_percents, name="Day Win %", yaxis="y2", marker_color="#9b59b6"))
    fig.update_layout(
        yaxis=dict(title="Profit Factor"),
        yaxis2=dict(title="Day Win %", overlaying="y", side="right"),
        barmode='group',
        height=180,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

def avg_win_loss_chart(trades):
    if trades.empty:
        return
    trades_by_day = trades.groupby("Date")
    days = []
    avg_wins = []
    avg_losses = []
    for day, group in trades_by_day:
        win = group[group["Net P&L"] > 0]["Net P&L"].mean() if not group[group["Net P&L"] > 0].empty else 0
        loss = group[group["Net P&L"] < 0]["Net P&L"].mean() if not group[group["Net P&L"] < 0].empty else 0
        days.append(day)
        avg_wins.append(win)
        avg_losses.append(loss)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=days, y=avg_wins, name="Avg Win", marker_color="#2980b9"))
    fig.add_trace(go.Bar(x=days, y=avg_losses, name="Avg Loss", marker_color="#8e44ad"))
    fig.update_layout(
        barmode='group',
        height=180,
        margin=dict(l=0, r=0, t=0, b=0),
        yaxis_title="Average"
    )
    st.plotly_chart(fig, use_container_width=True)

def month_status_calendar(trades):
    if trades.empty:
        return
    trades["Date"] = pd.to_datetime(trades["Date"])
    month = st.selectbox(
        "Select Month", 
        sorted(trades["Date"].dt.strftime("%Y-%m").unique()), 
        index=len(trades["Date"].dt.strftime("%Y-%m").unique())-1,
        key="month_status_calendar_month"
    )
    month_trades = trades[trades["Date"].dt.strftime("%Y-%m") == month]
    days = pd.date_range(start=month_trades["Date"].min(), end=month_trades["Date"].max())
    pnl_map = month_trades.groupby(month_trades["Date"].dt.day)["Net P&L"].sum().to_dict()
    calendar = []
    for day in days:
        pnl = pnl_map.get(day.day, 0)
        color = "#3498db" if pnl > 0 else "#9b59b6" if pnl < 0 else "#444"
        calendar.append({"day": day.day, "pnl": pnl, "color": color})
    st.write("#### Month Status")
    cols = st.columns(7)
    for i, entry in enumerate(calendar):
        with cols[i % 7]:
            st.markdown(
                f"<div style='background:{entry['color']};color:white;padding:8px;border-radius:6px;text-align:center;margin-bottom:4px'>"
                f"<b>{entry['day']}</b><br>${entry['pnl']:.2f}</div>",
                unsafe_allow_html=True
            )

def trading_calendar(trades):
    if trades.empty:
        st.info("No trades to display in calendar.")
        return

    trades["Date"] = pd.to_datetime(trades["Date"])
    # Select month and year
    months = sorted(trades["Date"].dt.strftime("%Y-%m").unique())
    selected_month = st.selectbox(
        "Select Month", 
        months, 
        index=len(months)-1,
        key="trading_calendar_month"
    )
    year, month = map(int, selected_month.split('-'))

    # Prepare daily P&L
    month_trades = trades[trades["Date"].dt.strftime("%Y-%m") == selected_month]
    daily_pnl = month_trades.groupby(month_trades["Date"].dt.day)["Net P&L"].sum().to_dict()
    daily_count = month_trades.groupby(month_trades["Date"].dt.day).size().to_dict()

    # Calendar grid
    cal = calendar.Calendar(firstweekday=0)  # 0=Monday, 6=Sunday
    month_days = cal.monthdayscalendar(year, month)
    week_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    st.markdown(f"### {calendar.month_name[month]} {year}")
    cols = st.columns(7)
    for i, label in enumerate(week_labels):
        cols[i].markdown(f"<b style='color:#FFD700'>{label}</b>", unsafe_allow_html=True)

    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].markdown(" ")
            else:
                pnl = daily_pnl.get(day, 0)
                count = daily_count.get(day, 0)
                if pnl > 0:
                    color = "#27ae60"  # Green
                    text_color = "white"
                elif pnl < 0:
                    color = "#c0392b"  # Red
                    text_color = "white"
                else:
                    color = "#222"
                    text_color = "#888"
                if count > 0:
                    cols[i].markdown(
                        f"<div style='background:{color};color:{text_color};padding:4px 0 2px 0;border-radius:5px;text-align:center;font-size:0.85em;min-height:38px;line-height:1.1;'>"
                        f"<b>{day}</b><br><span style='font-size:0.95em'>${pnl:,.0f}</span><br><span style='font-size:0.8em'>{count} trade{'s' if count>1 else ''}</span></div>",
                        unsafe_allow_html=True
                    )
                else:
                    cols[i].markdown(
                        f"<div style='background:#222;color:#888;padding:4px 0 2px 0;border-radius:5px;text-align:center;font-size:0.85em;min-height:38px;line-height:1.1;'>{day}</div>",
                        unsafe_allow_html=True
                    )

def main():
    st.set_page_config(page_title="Personal Trading Journal", layout="wide")
    st.markdown(
        "<h1 style='text-align:center; color:#FFD700; font-size: 3em; font-weight: bold;'>DD_ TRADING</h1>",
        unsafe_allow_html=True
    )
    init_csv()
    init_investment()

    # --- Ensure 'Pips' column exists in trades.csv ---
    trades = pd.read_csv(CSV_FILE)
    if "Pips" not in trades.columns:
        trades["Pips"] = ""
        trades.to_csv(CSV_FILE, index=False)

    # --- Investment Adjustment Section ---
    st.markdown("## 💰 Investment Adjustment")
    current_investment = get_investment()
    st.info(f"**Current Investment:** ${current_investment:,.2f}")

    # --- Investment Table Visibility Toggle ---
    if "show_investments" not in st.session_state:
        st.session_state["show_investments"] = False
    eye_icon = "👁️" if st.session_state["show_investments"] else "🙈"
    if st.button(f"{eye_icon} Show/Hide Investment Table"):
        st.session_state["show_investments"] = not st.session_state["show_investments"]

    investments_df = load_investments()

    # --- Handle Delete ---
    if 'delete_invest_row' in st.session_state:
        investments_df = investments_df.drop(st.session_state['delete_invest_row']).reset_index(drop=True)
        save_investments(investments_df)
        del st.session_state['delete_invest_row']
        st.rerun()

    # --- Handle Edit ---
    if 'edit_invest_row' in st.session_state:
        row = investments_df.iloc[st.session_state['edit_invest_row']]
        st.info("Edit Investment Entry")
        updated = investment_edit_form(row)
        if updated:
            investments_df.iloc[st.session_state['edit_invest_row']] = updated
            save_investments(investments_df)
            del st.session_state['edit_invest_row']
            st.success("Investment updated!")
            st.rerun()
        st.stop()  # Only show the edit form while editing

    # --- Investment Add Form ---
    with st.form("investment_form", clear_on_submit=True):
        adj_amount = st.text_input("Enter amount (use negative for withdraw)", value="", max_chars=15)
        submitted = st.form_submit_button("Submit")
        if submitted:
            try:
                adj_amount_val = float(adj_amount)
                add_investment(adj_amount_val)
                st.success("Investment adjusted!")
                st.rerun()
            except ValueError:
                st.error("Please enter a valid number for the amount.")

    # --- Show/Hide Investment Table ---
    if st.session_state["show_investments"]:
        st.markdown("### Investment History")
        display_investments_table(investments_df)

    trades = load_trades()

    # Sidebar for input and stats
    with st.sidebar:
        st.write("### Add Trade")
        trade_data = add_trade_form()
        if trade_data:
            save_trade(trade_data)
            st.success("Trade added successfully!")
            st.rerun()
        st.write("### Stats")
        stats = calculate_statistics()
        display_statistics(stats)
        st.write("### Win/Loss Pie")
        if not trades.empty:
            pie_chart(trades)

    # --- KPI Cards ---
    kpi_cards(trades)
    st.divider()

    # --- First Row: 3 Small Charts ---
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<h5 style='text-align:center;'>Profit Factor & Day Win %</h5>", unsafe_allow_html=True)
            profit_factor_daywin_chart(trades)
        with col2:
            st.markdown("<h5 style='text-align:center;'>Avg Win/Loss</h5>", unsafe_allow_html=True)
            avg_win_loss_chart(trades)
        with col3:
            st.markdown("<h5 style='text-align:center;'>Zella Score</h5>", unsafe_allow_html=True)
            zella_score_section(trades)
    st.divider()

    # --- Second Row: Month Calendar & Daily P&L ---
    with st.container():
        col4, col5 = st.columns(2)
        with col4:
            st.markdown("<h5 style='text-align:center;'>Month Status</h5>", unsafe_allow_html=True)
            month_status_calendar(trades)
        with col5:
            st.markdown("<h5 style='text-align:center;'>Daily P&L</h5>", unsafe_allow_html=True)
            daily_pnl_chart(trades)
    st.divider()

    # --- Trades Table ---
    st.markdown("<h5 style='text-align:center;'>Trades Table</h5>", unsafe_allow_html=True)
    display_trades(trades)

    st.divider()  # or st.markdown("<hr>", unsafe_allow_html=True)

    # --- Handle Trade Delete ---
    if 'delete_trade_row' in st.session_state:
        trades = trades.drop(st.session_state['delete_trade_row']).reset_index(drop=True)
        trades.to_csv(CSV_FILE, index=False)
        del st.session_state['delete_trade_row']
        st.rerun()

    # --- Handle Trade Edit ---
    if 'edit_trade_row' in st.session_state:
        row = trades.iloc[st.session_state['edit_trade_row']]
        st.info("Edit Trade Entry")
        updated = trade_edit_form(row)
        if updated:
            trades.iloc[st.session_state['edit_trade_row']] = updated
            trades.to_csv(CSV_FILE, index=False)
            del st.session_state['edit_trade_row']
            st.success("Trade updated!")
            st.rerun()
        st.stop()  # Only show the edit form while editing

    # --- Trading Calendar ---
    st.divider()
    st.markdown("<h5 style='text-align:center;'>Trading Calendar</h5>", unsafe_allow_html=True)
    trading_calendar(trades)

if __name__ == "__main__":
    main()
