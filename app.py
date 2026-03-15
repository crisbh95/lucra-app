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
st.header("⚽ Configuração da Aposta")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1. Favorito")
    nome_fav = st.text_input("Nome", "Flamengo")
    odd_fav = st.number_input("Odd", min_value=1.01, value=1.50)
    stake_fav = st.number_input("Stake ($)", min_value=1.0, value=60.0)

with col2:
    st.markdown("### 2. Proteção")
    nome_prot = st.text_input("Proteger Contra", "Empate/Derrota")
    odd_prot = st.number_input("Odd Proteção", min_value=1.01, value=4.00)
    
    tipo_hedge = st.radio("Estratégia", ["💸 Lucro Máximo (Green Up)", "🛡️ Zerar Prejuízo (Break Even)"])
    
    # Lógica de Hedge
    if "Green Up" in tipo_hedge:
        stake_prot = (stake_fav * (odd_fav - 1)) / (odd_prot - 1) if (odd_prot - 1) > 0 else 0
    else:
        stake_prot = (stake_fav * odd_fav) / odd_prot

    st.markdown(f"""
    <div class="card" style="border-color: #00D4FF;">
        <div class="metric-label">VALOR DA PROTEÇÃO</div>
        <div class="metric-value">${stake_prot:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# --- ANÁLISE DE MERCADO ---
st.markdown("---")
col_mer1, col_mer2 = st.columns(2)

prob_fav = (1/odd_fav) * 100
prob_prot = (1/odd_prot) * 100
soma_probs = prob_fav + prob_prot

with col_mer1:
    if soma_probs > 98:
        st.markdown(f"""<div class="overround-alert" style="background-color: #3E1C1C; color: #FF3B30;">⚠️ ATENÇÃO: Mercado Caro ({soma_probs:.1f}%)</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="overround-alert" style="background-color: #1C3E2C; color: #00F090;">✅ Mercado Sólido: {soma_probs:.1f}%</div>""", unsafe_allow_html=True)

# --- VALIDAÇÃO RISCO ---
total_apostado = stake_fav + stake_prot
margem = limite_max - total_apostado

with col_mer2:
    if margem < 0:
        st.error(f"⚠️ Excedeu o limite em ${abs(margem):,.2f}")
    else:
        st.success(f"✅ Saldo disponível: ${margem:,.2f}")

# --- SEGURO DE GOLS (DINÂMICO) ---
st.markdown("---")
st.header("🛡️ Seguro de Gols (Over 1.5)")

# Calculo do Lucro Potencial do Fav (Green Up)
lucro_bruto_fav = (stake_fav * odd_fav) - total_apostado
# Se o hedge comeu tudo, o lucro pode ser 0 ou menor. Vamos considerar 0 se não greenup.
if lucro_bruto_fav < 0: lucro_bruto_fav = 0

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.markdown(f"Lucro potencial do favorito: **${lucro_bruto_fav:,.2f}**")
    pct_seguro = st.slider("% do Lucro para Seguro", 0, 100, 10)
    
    # Cálculo Dinâmico: Baseado no Lucro, não na Stake
    stake_seguro = lucro_bruto_fav * (pct_seguro / 100)
    
    st.metric("Valor do Seguro", f"${stake_seguro:,.2f}")
    
with col_s2:
    odd_over = st.number_input("Odd Over 1.5", 1.01, 10.0, 1.8)
    retorno_seguro = stake_seguro * odd_over
    st.info(f"Retorno potencial: ${retorno_seguro:,.2f}")
    st.caption("Este valor sai do seu lucro.")

# --- CENÁRIOS ---
st.header("🔎 Resultado Final")

c1, c2 = st.columns(2)

# Cenário 1: Fav Ganha
retorno_fav = stake_fav * odd_fav
lucro_fav = (retorno_fav + retorno_seguro) - (total_apostado + stake_seguro)
roi_fav = (lucro_fav / (total_apostado + stake_seguro)) * 100 if (total_apostado + stake_seguro) > 0 else 0
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

# Cenário 2: Proteção Ganha
# Cenário 2 = Empate/Derrota. Seguro Over 1.5 Gols geralmente PERDE nesse cenário (0-0, 1-0)
# Vamos considerar que o Seguro Perdeu (-stake_seguro)
lucro_prot = (stake_prot * odd_prot) - (stake_fav + stake_prot) - stake_seguro
roi_prot = (lucro_prot / (total_apostado + stake_seguro)) * 100 if (total_apostado + stake_seguro) > 0 else 0
cor_prot = "success-text" if lucro_prot >= 0 else "warning-text"

with c2:
    st.markdown(f"""
    <div class="card">
        <h3>🛡️ {nome_prot}</h3>
        <div class="metric-value {cor_prot}">${lucro_prot:,.2f}</div>
        <div class="metric-label">LUCRO LÍQUIDO</div>
        <div class="roi-text">ROI: {roi_prot:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.caption(f"💡 Total investido (com seguro): ${total_apostado + stake_seguro:,.2f}")
