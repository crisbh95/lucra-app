import streamlit as st

st.set_page_config(page_title="Lucra+ | Estratégia SwissTony", page_icon="🎯", layout="wide")

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

st.title("🎯 Lucra+ | Estratégia Automática")

# --- BARRA LATERAL ---
st.sidebar.header("💰 Gestão de Banca")
banca_total = st.sidebar.number_input("Banca Total ($)", min_value=0.0, value=100.0, step=10.0)
risco_pct = st.sidebar.slider("% Risco por Jogo", 1, 20, 5)
limite_max = banca_total * (risco_pct / 100)
st.sidebar.markdown(f"**Limite:** ${limite_max:,.2f}")

# --- FLUXO PRINCIPAL ---
st.header("⚽ Jogo: Favorito vs Zebra")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1. Favorito (Seu Palpite)")
    nome_fav = st.text_input("Time Favorito", "Flamengo")
    odd_fav = st.number_input(f"Odd {nome_fav}", min_value=1.01, value=1.50)
    valor_principal = st.number_input(f"Quanto apostar no {nome_fav}? ($)", min_value=1.0, value=60.0)

with col2:
    st.markdown("### 2. Zebra (Proteção)")
    nome_zebra = st.text_input("Time Zebra", "Criciúma")
    odd_zebra = st.number_input(f"Odd {nome_zebra}", min_value=1.01, value=8.00)
    
    tipo_cobertura = st.radio("Estratégia de Cobertura", ["💸 Lucro Máximo (Green Up)", "🛡️ Cobrir Custo (Zerar Prejuízo)"])
    
    # Lógica de Cobertura
    # Green Up: Lucro Fav = Lucro Zebra
    # Lucro Fav = valor_principal * (odd_fav - 1)
    # Lucro Zebra = valor_zebra * (odd_zebra - 1)
    # valor_zebra = (valor_principal * (odd_fav - 1)) / (odd_zebra - 1)
    
    # Cover Cost (Break Even): Retorno Zebra >= Investimento Total (Fav + Zebra)
    # valor_zebra * odd_zebra >= valor_principal + valor_zebra
    # valor_zebra * (odd_zebra - 1) >= valor_principal
    # valor_zebra = valor_principal / (odd_zebra - 1)
    
    if "Green Up" in tipo_cobertura:
        valor_zebra = (valor_principal * (odd_fav - 1)) / (odd_zebra - 1) if (odd_zebra - 1) > 0 else 0
    else:
        valor_zebra = valor_principal / (odd_zebra - 1) if (odd_zebra - 1) > 0 else 0

    st.markdown(f"""
    <div class="card" style="border-color: #00D4FF;">
        <div class="metric-label">VALOR NA ZEBRA ({nome_zebra})</div>
        <div class="metric-value">${valor_zebra:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# --- ANÁLISE DE MERCADO ---
st.markdown("---")
col_mer1, col_mer2 = st.columns(2)

prob_fav = (1/odd_fav) * 100
prob_zebra = (1/odd_zebra) * 100
soma_probs = prob_fav + prob_zebra

with col_mer1:
    if soma_probs > 98:
        st.markdown(f"""<div class="overround-alert" style="background-color: #3E1C1C; color: #FF3B30;">⚠️ ATENÇÃO: Mercado Caro ({soma_probs:.1f}%)</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="overround-alert" style="background-color: #1C3E2C; color: #00F090;">✅ Mercado Sólido: {soma_probs:.1f}%</div>""", unsafe_allow_html=True)

# --- VALIDAÇÃO RISCO ---
total_apostado = valor_principal + valor_zebra
margem = limite_max - total_apostado

with col_mer2:
    if margem < 0:
        st.error(f"⚠️ Excedeu o limite em ${abs(margem):,.2f}")
    else:
        st.success(f"✅ Saldo disponível: ${margem:,.2f}")

# --- SEGURO DE GOLS (DINÂMICO) ---
st.markdown("---")
st.header("🛡️ Seguro de Gols (Over 1.5)")

lucro_bruto_fav = (valor_principal * odd_fav) - valor_principal
if lucro_bruto_fav < 0: lucro_bruto_fav = 0

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.markdown(f"Lucro potencial do favorito: **${lucro_bruto_fav:,.2f}**")
    pct_seguro = st.slider("% do Lucro para Seguro", 0, 100, 10)
    valor_seguro = lucro_bruto_fav * (pct_seguro / 100)
    st.metric("Valor do Seguro", f"${valor_seguro:,.2f}")
    
with col_s2:
    odd_over = st.number_input("Odd Over 1.5", 1.01, 10.0, 1.8)
    retorno_seguro = valor_seguro * odd_over
    st.info(f"Retorno potencial: ${retorno_seguro:,.2f}")
    st.caption("Este valor sai do seu lucro.")

# --- CENÁRIOS ---
st.header("🔎 Resultado Final")

c1, c2 = st.columns(2)

# Cenário 1: Fav Ganha
retorno_fav = valor_principal * odd_fav
# Neste cenário, a Zebra perde (-valor_zebra)
# O Seguro Over pode ganhar ou perder. Vamos assumir que SIM, houve gol.
lucro_fav = (retorno_fav + retorno_seguro) - (total_apostado + valor_seguro)
roi_fav = (lucro_fav / (total_apostado + valor_seguro)) * 100 if (total_apostado + valor_seguro) > 0 else 0
cor_fav = "success-text" if lucro_fav >= 0 else "warning-text"

with c1:
    st.markdown(f"""
    <div class="card">
        <h3>🏆 {nome_fav} VENCE</h3>
        <div class="metric-value {cor_fav}">${lucro_fav:,.2f}</div>
        <div class="metric-label">LUCRO LÍQUIDO</div>
        <div class="roi-text">ROI: {roi_fav:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# Cenário 2: Zebra Ganha
retorno_zebra = valor_zebra * odd_zebra
# Neste cenário, o Fav perde (-valor_principal)
# Seguro Over: Se Zebra venceu (ex: 0-1), provavelmente NÃO teve Over 1.5 (menos de 2 golos).
# Custo do seguro perdido.
lucro_zebra = (retorno_zebra - valor_zebra - valor_principal) - valor_seguro
roi_zebra = (lucro_zebra / (total_apostado + valor_seguro)) * 100 if (total_apostado + valor_seguro) > 0 else 0
cor_zebra = "success-text" if lucro_zebra >= 0 else "warning-text"

with c2:
    st.markdown(f"""
    <div class="card">
        <h3>🏅 {nome_zebra} VENCE (ZEBRA)</h3>
        <div class="metric-value {cor_zebra}">${lucro_zebra:,.2f}</div>
        <div class="metric-label">LUCRO LÍQUIDO</div>
        <div class="roi-text">ROI: {roi_zebra:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.caption(f"💡 Total investido (com seguro): ${total_apostado + valor_seguro:,.2f}")
