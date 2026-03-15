import streamlit as st

def input_odd_or_cents(label, default_odd=1.5, key_prefix=""):
    modo = st.radio(
        f"Modo {label}:",
        ["Odd Decimal (Brasil)", "Centavos (Polymarket)"],
        horizontal=True,
        key=f"modo_{key_prefix}"
    )
    
    cents = 0
    
    if modo == "Centavos (Polymarket)":
        cents = st.number_input(
            f"Preço em Centavos ¢ ({label})",
            min_value=1, max_value=99, value=43,
            key=f"cents_{key_prefix}"
        )
        odd = 100 / cents
        st.info(f"Equivalent Odd: {odd:.2f}")
        is_polymarket = True
    else:
        odd = st.number_input(
            f"Odd {label}",
            min_value=1.01, value=default_odd, format="%.2f",
            key=f"odd_{key_prefix}"
        )
        is_polymarket = False
    
    return odd, is_polymarket, cents

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

st.info("💡 **Dica Polymarket:** No campo Amount do Polymarket, você digita o valor em Dólares (Stake). O site calcula sozinho quantas 'Shares' você compra.")

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
    odd_fav, is_poly_fav, cents_fav = input_odd_or_cents(nome_fav, default_odd=1.50, key_prefix="fav")
    stake_fav = st.number_input(f"Stake {nome_fav} ($)", min_value=1.0, value=60.0)
    
    nome_empate = st.text_input("Empate", "Empate")
    odd_empate, is_poly_empate, cents_empate = input_odd_or_cents(nome_empate, default_odd=4.00, key_prefix="emp")
    
    nome_zebra = st.text_input("Zebra", "Criciúma")
    odd_zebra, is_poly_zebra, cents_zebra = input_odd_or_cents(nome_zebra, default_odd=8.00, key_prefix="zebra")
    
    # Validacao e sugestao automatica para Polymarket
    is_poly_mode = is_poly_fav or is_poly_empate or is_poly_zebra
    
    if is_poly_mode:
        total_cents = cents_fav + cents_empate + cents_zebra
        
        if total_cents > 100:
            st.error(f"⚠️ Erro: A soma dos centavos ({total_cents}) não pode ultrapassar 100.")
        
        # Sugestao automatica baseada no que sobra
        if is_poly_fav and not is_poly_empate and not is_poly_zebra:
            if total_cents < 100:
                suggested_emp = 100 - total_cents
                st.success(f"💡 Sugestão: Para um mercado justo, o Empate deveria estar em ~{suggested_emp}¢ e a Zebra em ~1¢ (ou vice-versa).")
        elif is_poly_fav and is_poly_empate and not is_poly_zebra:
            if total_cents < 100:
                suggested_zebra = 100 - total_cents
                st.success(f"💡 Sugestão: Para um mercado justo, a Zebra deveria estar em ~{suggested_zebra}¢.")
    
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

# Custo total de todas as apostas
custo_total = stake_fav + stake_empate + stake_zebra + valor_seguro

# Lucro do seguro
lucro_seguro = valor_seguro * odd_over

# 1. Fav Ganha (não soma seguro - favorito geralmente não tem muitos gols)
lucro_1 = (stake_fav * odd_fav) - custo_total
roi_1 = (lucro_1 / custo_total) * 100 if custo_total > 0 else 0
cor_1 = "success-text" if lucro_1 >= 0 else "warning-text"

with c1:
    st.markdown(f"""
    <div class="card">
        <h3>🏆 {nome_fav}</h3>
        <div class="metric-value {cor_1}">${lucro_1:,.2f}</div>
        <div class="roi-text">ROI: {roi_1:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# 2. Empate + Seguro
lucro_2 = (stake_empate * odd_empate) + lucro_seguro - custo_total
roi_2 = (lucro_2 / custo_total) * 100 if custo_total > 0 else 0
cor_2 = "success-text" if lucro_2 >= 0 else "warning-text"

with c2:
    st.markdown(f"""
    <div class="card">
        <h3>⚖️ {nome_empate}</h3>
        <div class="metric-value {cor_2}">${lucro_2:,.2f}</div>
        <div class="roi-text">ROI: {roi_2:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# 3. Zebra + Seguro
lucro_3 = (stake_zebra * odd_zebra) + lucro_seguro - custo_total
roi_3 = (lucro_3 / custo_total) * 100 if custo_total > 0 else 0
cor_3 = "success-text" if lucro_3 >= 0 else "warning-text"

with c3:
    st.markdown(f"""
    <div class="card">
        <h3>🏅 {nome_zebra}</h3>
        <div class="metric-value {cor_3}">${lucro_3:,.2f}</div>
        <div class="roi-text">ROI: {roi_3:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# 4. Over 1.5 - Apenas Seguro
lucro_4 = lucro_seguro - custo_total
roi_4 = (lucro_4 / custo_total) * 100 if custo_total > 0 else 0
cor_4 = "success-text" if lucro_4 >= 0 else "warning-text"

with c4:
    st.markdown(f"""
    <div class="card">
        <h3>⚽ Over 1.5</h3>
        <div class="metric-label">Apenas Seguro</div>
        <div class="metric-value {cor_4}">${lucro_4:,.2f}</div>
        <div class="roi-text">ROI: {roi_4:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.caption(f"Total Investido: ${custo_total:,.2f}")

# --- MANUAL NA BARRA LATERAL ---
st.sidebar.markdown("---")
st.sidebar.header("📖 Manual de Operação")

# Função auxiliar para exibir o valor correto no manual
def get_display_value(mode, stake, odd, is_poly):
    if is_poly:
        cents = int(100 / odd)
        return f"{cents}¢ (Amount: ${stake:,.2f})"
    else:
        return f"${stake:,.2f}"

st.sidebar.markdown(f"""
**1. Escolha o Mercado**
Procure por: `{nome_fav} vs {nome_zebra}`.

**2. Opção SIM (Favorito)**
Se você acha que o {nome_fav} vence:
* Escolha: **{"Polymarket (YES)" if is_poly_fav else "Casa (1)" if "1" in nome_fav else "Casa"}**
* Digite: **{get_display_value("fav", stake_fav, odd_fav, is_poly_fav)}**

**3. Opção NÃO (Proteção)**
Para cobrir Empate e Zebra:
* Escolha: **{"Polymarket (NO)" if is_poly_empate or is_poly_zebra else "Casa (X ou 2)"}**
* Digite Empate: **{get_display_value("emp", stake_empate, odd_empate, is_poly_empate)}**
* Digite Zebra: **{get_display_value("zebra", stake_zebra, odd_zebra, is_poly_zebra)}**
* *Isso cobre qualquer tropeço do favorito.*

**4. Seguro de Gols**
Procure o mercado: `Total Goals Over 1.5`
* Escolha: **Casa**
* Digite: **${valor_seguro:,.2f}**
""")

st.sidebar.info("💡 Dica: O 'NÃO' no favorito substitui as apostas individuais em Empate e Zebra.")
