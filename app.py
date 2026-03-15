import streamlit as st

st.set_page_config(page_title="Lucra+ | Estratégia Completa", page_icon="🎯", layout="wide")

# --- CSS Custom ---
st.markdown("""
<style>
    .stApp { background-color: #0B0E11; color: #E1E7EF; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #00F090 0%, #00D4FF 100%);
        color: #0B0E11;
        font-weight: bold;
        border: none;
        padding: 10px;
        font-size: 16px;
    }
    .card {
        background-color: #151A21;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #2A3038;
        margin-bottom: 15px;
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    h1, h2, h3 { color: #00F090 !important; }
    .metric-value { font-size: 24px; font-weight: bold; color: #00D4FF; }
    .metric-label { font-size: 12px; color: #8B9BB4; text-transform: uppercase; }
    .roi-text { color: #FFD700; font-weight: bold; font-size: 18px; }
    .warning-text { color: #FF3B30; font-weight: bold; }
    .success-text { color: #00F090; font-weight: bold; }
    .stNumberInput > div > div > input { color: white; background-color: #1E232B; }
    .overround-alert { padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🎯 Lucra+ | Estratégia Completa (3 Caminhos)")

# --- BARRA LATERAL ---
st.sidebar.header("💰 Gestão de Banca")
banca_total = st.sidebar.number_input("Banca Total ($)", min_value=0.0, value=100.0, step=10.0)
risco_pct = st.sidebar.slider("% Risco por Jogo", 1, 20, 5)
limite_max = banca_total * (risco_pct / 100)
st.sidebar.markdown(f"**Limite:** ${limite_max:,.2f}")

# --- FLUXO PRINCIPAL ---
st.header("⚽ Jogo Completo")

col_inputs, col_estrategia = st.columns([1, 1])

with col_inputs:
    st.markdown("### 📝 Inputs")
    nome_fav = st.text_input("Favorito", "Flamengo")
    odd_fav = st.number_input(f"Odd {nome_fav}", min_value=1.01, value=1.50)
    stake_fav = st.number_input(f"Stake {nome_fav} ($)", min_value=1.0, value=60.0)
    
    nome_empate = st.text_input("Empate", "Empate")
    odd_empate = st.number_input(f"Odd {nome_empate}", min_value=1.01, value=4.00)
    
    nome_zebra = st.text_input("Zebra", "Criciúma")
    odd_zebra = st.number_input(f"Odd {nome_zebra}", min_value=1.01, value=8.00)
    
    st.markdown("### 🛡️ Seguro Gols")
    lucro_bruto = (stake_fav * odd_fav) - stake_fav
    if lucro_bruto < 0: lucro_bruto = 0
    
    pct_seguro = st.slider("% Lucro Seguro", 0, 100, 10)
    valor_seguro = lucro_bruto * (pct_seguro / 100)
    odd_over = st.number_input("Odd Over 1.5", 1.01, 10.0, 1.8)

with col_estrategia:
    st.markdown("### 🎯 Estratégia")
    estrategia = st.radio("Tipo", ["💸 Lucro Máximo (Green Up)", "🛡️ Cobrir Custo (Break Even)"])
    
    # Cálculo da Cobertura
    if "Green Up" in estrategia:
        lucro_fav = stake_fav * (odd_fav - 1)
        stake_empate = lucro_fav / (odd_empate - 1) if (odd_empate - 1) > 0 else 0
        stake_zebra = lucro_fav / (odd_zebra - 1) if (odd_zebra - 1) > 0 else 0
    else:
        stake_empate = stake_fav / (odd_empate - 1) if (odd_empate - 1) > 0 else 0
        stake_zebra = stake_fav / (odd_zebra - 1) if (odd_zebra - 1) > 0 else 0
        
        total_sem_empate = stake_fav + stake_zebra + valor_seguro
        stake_empate = total_sem_empate / (odd_empate - 1) if (odd_empate - 1) > 0 else 0
        
        total_sem_zebra = stake_fav + stake_empate + valor_seguro
        stake_zebra = total_sem_zebra / (odd_zebra - 1) if (odd_zebra - 1) > 0 else 0

    st.markdown(f"""
    <div class="card" style="border-color: #FF3B30;">
        <div class="metric-label">COBERTURA {nome_empate}</div>
        <div class="metric-value" style="color:#FF3B30">${stake_empate:,.2f}</div>
        <div class="metric-label">COBERTURA {nome_zebra}</div>
        <div class="metric-value" style="color:#FF3B30">${stake_zebra:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    prob_fav = (1/odd_fav) * 100
    prob_empate = (1/odd_empate) * 100
    prob_zebra = (1/odd_zebra) * 100
    soma_probs = prob_fav + prob_empate + prob_zebra

    if soma_probs > 105:
        st.markdown(f"""<div class="overround-alert" style="background-color: #3E1C1C; color: #FF3B30;">⚠️ MERCADO CARO ({soma_probs:.1f}%)</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="overround-alert" style="background-color: #1C3E2C; color: #00F090;">✅ MERCADO OK ({soma_probs:.1f}%)</div>""", unsafe_allow_html=True)

    total_apostado = stake_fav + stake_empate + stake_zebra
    margem = limite_max - total_apostado

    if margem < 0:
        st.error(f"⚠️ Excedeu limite em ${abs(margem):,.2f}")
    else:
        st.success(f"✅ Saldo: ${margem:,.2f}")
    
    st.metric("Valor Seguro", f"${valor_seguro:,.2f}", f"Ret: ${valor_seguro * odd_over:,.2f}")

# --- CENÁRIOS ---
st.markdown("---")
st.header("🔎 4 Cenários")

c1, c2, c3, c4 = st.columns(4)

# 1. Fav Ganha
lucro_1 = (stake_fav * odd_fav) - total_apostado - valor_seguro
roi_1 = (lucro_1 / total_apostado) * 100 if total_apostado > 0 else 0
cor_1 = "success-text" if lucro_1 >= 0 else "warning-text"

with c1:
    st.markdown(f"""
    <div class="card">
        <h3>🏆 {nome_fav}</h3>
        <div class="metric-value {cor_1}">${lucro_1:,.2f}</div>
        <div class="roi-text">ROI: {roi_1:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# 2. Empate
lucro_2 = (stake_empate * odd_empate) - total_apostado - valor_seguro
roi_2 = (lucro_2 / total_apostado) * 100 if total_apostado > 0 else 0
cor_2 = "success-text" if lucro_2 >= 0 else "warning-text"

with c2:
    st.markdown(f"""
    <div class="card">
        <h3>⚖️ {nome_empate}</h3>
        <div class="metric-value {cor_2}">${lucro_2:,.2f}</div>
        <div class="roi-text">ROI: {roi_2:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# 3. Zebra Ganha
lucro_3 = (stake_zebra * odd_zebra) - total_apostado - valor_seguro
roi_3 = (lucro_3 / total_apostado) * 100 if total_apostado > 0 else 0
cor_3 = "success-text" if lucro_3 >= 0 else "warning-text"

with c3:
    st.markdown(f"""
    <div class="card">
        <h3>🏅 {nome_zebra}</h3>
        <div class="metric-value {cor_3}">${lucro_3:,.2f}</div>
        <div class="roi-text">ROI: {roi_3:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# 4. Muitos Gols (Over 1.5) - Seguro Ganha
# O seguro paga (valor_seguro * odd_over) mas não paga o favorito
lucro_seguro = (valor_seguro * odd_over) - valor_seguro  # Lucro puro do seguro
lucro_4 = lucro_seguro - (stake_empate + stake_zebra)  # Ganha seguro, perde coberturas
roi_4 = (lucro_4 / total_apostado) * 100 if total_apostado > 0 else 0
cor_4 = "success-text" if lucro_4 >= 0 else "warning-text"

with c4:
    st.markdown(f"""
    <div class="card">
        <h3>⚽ Over 1.5</h3>
        <div class="metric-label">Seguro Ganha</div>
        <div class="metric-value {cor_4}">${lucro_4:,.2f}</div>
        <div class="roi-text">ROI: {roi_4:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.caption(f"Total Investido: ${total_apostado + valor_seguro:,.2f}")
