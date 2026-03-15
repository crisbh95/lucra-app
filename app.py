import streamlit as st
import requests

def buscar_mercado_polymarket(query):
    try:
        # Busca apenas mercados ativos e não encerrados
        url = "https://clob.polymarket.com/markets"
        params = {
            "active": "true",
            "closed": "false",
            "order_by": "volume",
            "limit": "100"
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            markets = []
            
            if "data" in data:
                for market in data["data"]:
                    # Filtro adicional: ignora mercados encerrados ou muito antigos
                    if market.get("closed", True):
                        continue
                    
                    # Verifica se o mercado tem data futura (simplificado)
                    question = market.get("question", "").lower()
                    query_lower = query.lower()
                    
                    # Procura por times similares no nome
                    if query_lower in question or any(word in question for word in query_lower.split()):
                        # Ignora mercados de política ou antigos
                        if any(x in question for x in ["2025", "2024", "2023", "2022", "winner", "election"]):
                            continue
                            
                        # Busca os precos dos outcomes
                        outcomes = market.get("outcomes", [])
                        tokens = market.get("tokens", [])
                        
                        precos = {}
                        for i, outcome in enumerate(outcomes):
                            if i < len(tokens):
                                token_id = tokens[i]
                                # Busca preco deste token
                                try:
                                    price_url = f"https://clob.polymarket.com/prices?token_ids={token_id}"
                                    price_resp = requests.get(price_url, timeout=5)
                                    if price_resp.status_code == 200:
                                        price_data = price_resp.json()
                                        if price_data and len(price_data) > 0:
                                            precos[outcome.lower()] = price_data[0].get("price", 0) * 100
                                except:
                                    pass
                        
                        markets.append({
                            "question": market.get("question"),
                            "id": market.get("id"),
                            "slug": market.get("slug"),
                            "closed": market.get("closed", False),
                            "precos": precos
                        })
            return markets[:5]  # Retorna no maximo 5 resultados
        return []
    except Exception as e:
        st.error(f"Erro ao buscar mercado: {e}")
        return []

def importar_mercado(market):
    """Importa os dados do mercado selecionado para os inputs"""
    st.session_state["importar_mercado"] = market
    st.rerun()

def get_preco_central(price_data):
    if not price_data:
        return None
    try:
        if isinstance(price_data, dict):
            return (price_data.get("bid1", 0) + price_data.get("ask1", 0)) / 2
        return price_data
    except:
        return None

def input_odd_or_cents(label, default_odd=1.5, key_prefix=""):
    modo = st.radio(
        f"Modo {label}:",
        ["Modo Casa Brasileira", "Centavos (Polymarket)"],
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
            min_value=1.01, value=float(default_odd), step=0.05, format="%.2f",
            key=f"odd_{key_prefix}"
        )
        is_polymarket = False
    
    return odd, is_polymarket, cents

st.set_page_config(page_title="Lucra+ | Estratégia Completa", page_icon="🎯", layout="wide")

# Inicializa session_state para stake
if "stake_fav" not in st.session_state:
    st.session_state["stake_fav"] = 10.00

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

if st.button("🗑️ Limpar Jogo Atual"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.info("💡 **Dica Polymarket:** No campo Amount do Polymarket, você digita o valor em Dólares (Stake). O site calcula sozinho quantas 'Shares' você compra.")

# --- BARRA LATERAL ---
st.sidebar.header("💰 Gestão de Banca")
banca_total = st.sidebar.number_input("Banca Total ($)", min_value=0.0, value=100.0, step=10.0)
risco_pct = st.sidebar.slider("% Risco por Jogo", 1, 20, 5)
limite_max = banca_total * (risco_pct / 100)
st.sidebar.markdown(f"**Limite:** ${limite_max:,.2f}")
banca_maxima = st.sidebar.number_input("Banca Máxima por Jogo ($)", min_value=0.0, value=limite_max, step=5.0)

# --- FLUXO PRINCIPAL ---
st.header("⚽ Jogo Completo")

col_inputs, col_estrategia = st.columns([1, 1])

with col_inputs:
    st.markdown("### 📝 Inputs")
    nome_fav = st.text_input("Favorito", "Flamengo")
    odd_fav, is_poly_fav, cents_fav = input_odd_or_cents(nome_fav, default_odd=1.50, key_prefix="fav")
    stake_fav = st.number_input(f"Stake {nome_fav} ($)", min_value=1.0, value=st.session_state.get("stake_fav", 10.00), step=5.0, format="%.2f")
    
    nome_empate = st.text_input("Empate", "Empate")
    odd_empate, is_poly_empate, cents_empate = input_odd_or_cents(nome_empate, default_odd=4.00, key_prefix="emp")
    
    nome_zebra = st.text_input("Zebra", "Criciúma")
    odd_zebra, is_poly_zebra, cents_zebra = input_odd_or_cents(nome_zebra, default_odd=8.00, key_prefix="zebra")
    
    # Validacao e sugestao automatica para Polymarket
    is_poly_mode = is_poly_fav or is_poly_empate or is_poly_zebra
    
    if is_poly_mode:
        total_cents = cents_fav + cents_empate + cents_zebra
        
        if total_cents > 102:
            st.error("⚠️ Jogo com taxa muito alta. A proteção vai custar mais que o lucro. Procure outro mercado.")
        elif total_cents > 100:
            st.warning(f"⚠️ Aviso: A soma dos centavos é {total_cents} (o mercado tem ~3% de taxa/spread). Os cálculos continuarão.")
        
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
    ativar_seguro = st.checkbox("Ativar Seguro de Gols", value=True)
    
    modo_seguro = "Modo Casa Brasileira" # Default in case it is deactivated
    if ativar_seguro:
        modo_seguro = st.radio("Modo Seguro:", ["Modo Casa Brasileira", "Centavos (Polymarket)"], horizontal=True, key="modo_seguro")
        
        if modo_seguro == "Centavos (Polymarket)":
            cents_seguro = st.number_input("Preço Over 1.5 (¢)", min_value=1, max_value=99, value=70, key="cents_seguro")
            odd_over = 100 / cents_seguro
            st.info(f"Equivalent Odd: {odd_over:.2f}")
        else:
            odd_over = st.number_input("Odd Over 1.5", min_value=1.01, value=1.30, format="%.2f", key="odd_over")
        
        valor_seguro = st.number_input("Valor da Aposta no Seguro ($)", min_value=0.0, value=5.00, step=1.0, format="%.2f", key="valor_seguro")
    else:
        odd_over = 1.01  # Apenas para evitar divisão por zero, valor inativo
        valor_seguro = 0.0
    
    # Estrategia padrao para calculos temporarios
    estrategia_calc = "💸 Lucro Máximo (Green Up)"
    
    # Sugestao automatica do seguro (maximo 5% do investimento total)
    if is_poly_mode:
        # Primeiro calcula as stakers temporariamente para ter o custo total
        # Usamos o modo Maximizar Lucro por padrao para a estimativa
        denominador_temp = (odd_empate - 1.0) * (odd_zebra - 1.0) - 1.0
        if denominador_temp > 0:
            stake_empate_temp = (stake_fav * odd_zebra) / denominador_temp
            stake_zebra_temp = (stake_fav * odd_empate) / denominador_temp
        else:
            stake_empate_temp = stake_fav / (odd_empate - 1.0) if (odd_empate - 1.0) > 0 else 0
            stake_zebra_temp = stake_fav / (odd_zebra - 1.0) if (odd_zebra - 1.0) > 0 else 0
        
        custo_principal = stake_fav + stake_empate_temp + stake_zebra_temp
        limite_seguro = custo_principal * 0.05
        
        if valor_seguro > limite_seguro:
            st.warning(f"⚠️ Sugestão: O seguro ideal não deve ultrapassar 5% do investimento (${limite_seguro:.2f})")
    
    # Ponto de Equilibrio - preco maximo em centavos para ter lucro no favorito
    if is_poly_fav:
        # Calcula o custo das protecoes para saber o ponto de equilibrio
        # Usamos O modo Maximizar Lucro para a base do calculo
        denominador_temp = (odd_empate - 1.0) * (odd_zebra - 1.0) - 1.0
        if denominador_temp > 0:
            stake_empate_temp = (stake_fav * odd_zebra) / denominador_temp
            stake_zebra_temp = (stake_fav * odd_empate) / denominador_temp
        else:
            stake_empate_temp = stake_fav / (odd_empate - 1.0) if (odd_empate - 1.0) > 0 else 0
            stake_zebra_temp = stake_fav / (odd_zebra - 1.0) if (odd_zebra - 1.0) > 0 else 0
        
        custo_protecoes = stake_empate_temp + stake_zebra_temp + valor_seguro
        custo_total_estimado = stake_fav + custo_protecoes
        
        # Lucro-minimo = custo total - stake_fav (para cobrir todas as protecoes)
        # odd_fav * stake_fav >= custo_total -> stake_fav >= custo_total / odd_fav
        # preco_max = 100 / odd_minima_para_lucro
        
        odd_min_para_lucro = custo_total_estimado / stake_fav
        if odd_min_para_lucro > 1:
            cents_max = int(100 / odd_min_para_lucro)
            st.info(f"🎯 Ponto de Equilíbrio: Para cobrir as proteções (${custo_protecoes:.2f}), o favorito precisa estar no máximo em {cents_max}¢ (Odd {odd_min_para_lucro:.2f})")
        else:
            st.success("✅ Com este favorito forte, você já tem lucro garantido!")

with col_estrategia:
    st.markdown("### 🎯 Estratégia")
    
    # Botao para abrir no Polymarket
    search_query = f"{nome_fav} {nome_zebra}"
    polymarket_url = f"https://polymarket.com/search?q={search_query.replace(' ', '%20')}"
    
    # Campo de busca na API
    st.markdown("#### 🔍 Buscar Jogo no Polymarket")
    st.markdown(f"[🌐 Abrir Jogo no Polymarket]({polymarket_url})")
    
    st.markdown("---")
    
    estrategia = st.radio("Objetivo da Operação", ["🛡️ Cercar Jogo (Break Even)", "💸 Maximizar Lucro (Favorito)"])
    
    # Botao de Otimizacao
    if st.button("⚡ Otimizar Lucro"):
        # Calcula as probablidades
        prob_fav_calc = (1/odd_fav) * 100
        prob_empate_calc = (1/odd_empate) * 100
        prob_zebra_calc = (1/odd_zebra) * 100
        soma_probs_calc = prob_fav_calc + prob_empate_calc + prob_zebra_calc
        
        if soma_probs_calc > 105:
            st.error("🔴 Custo operacional muito alto. Recomenda-se aguardar as Odds subirem.")
        else:
            # Calcula o lucro necessario (10% do investimento)
            custo_atual = stake_fav + stake_empate + stake_zebra + valor_seguro
            lucro_desejado = custo_atual * 0.10
            
            # Calcula o que o favorito precisa dar de lucro
            lucro_fav_necessario = stake_empate + stake_zebra + valor_seguro + lucro_desejado
            
            # Odd minima para ter 10% de lucro
            odd_minima_10 = (stake_fav + lucro_fav_necessario) / stake_fav
            cents_max_10 = int(100 / odd_minima_10) if odd_minima_10 > 1 else 99
            
            # Calcula preco maximo para Empate e Zebra
            # Se o favorito der 10% de lucro, quanto podemos pagar nas protecoes?
            stake_empate_otimo = stake_fav * (odd_fav - 1) - stake_zebra - valor_seguro + lucro_desejado
            stake_zebra_otimo = stake_fav * (odd_fav - 1) - stake_empate - valor_seguro + lucro_desejado
            
            # Converte para centavos
            if stake_empate_otimo > 0 and odd_empate > 1:
                odd_empate_max = 1 + (stake_fav / stake_empate_otimo) if stake_empate_otimo > 0 else 99
                cents_empate_max = int(100 / odd_empate_max) if odd_empate_max > 1 else 99
            else:
                cents_empate_max = 1
                
            if stake_zebra_otimo > 0 and odd_zebra > 1:
                odd_zebra_max = 1 + (stake_fav / stake_zebra_otimo) if stake_zebra_otimo > 0 else 99
                cents_zebra_max = int(100 / odd_zebra_max) if odd_zebra_max > 1 else 99
            else:
                cents_zebra_max = 1
            
            st.success(f"✅ Otimização aplicada!")
            st.info(f"📊 Meta: Para ter 10% de lucro no {nome_fav}, você precisa de Odd mínima {odd_minima_10:.2f} ({cents_max_10}¢)")
            st.info(f"💡 Preço máximo sugerido: Empate {cents_empate_max}¢ | Zebra {cents_zebra_max}¢")
    
    # Cálculo da Cobertura
    if "Cercar Jogo" in estrategia:
        # Equal Profit - Partilha Igualitária
        retorno_total = stake_fav * odd_fav
        stake_empate = retorno_total / odd_empate if odd_empate > 0 else 0
        stake_zebra = retorno_total / odd_zebra if odd_zebra > 0 else 0
        st.success("✅ Partilha de Lucros: O prêmio será igual independente de quem vencer.")
    else:
        # Maximizar Lucro (Favorito) com Cobertura Cruzada Mútua
        denominador = (odd_empate - 1.0) * (odd_zebra - 1.0) - 1.0
        if denominador > 0:
            stake_empate = ((stake_fav + valor_seguro) * odd_zebra) / denominador
            stake_zebra = ((stake_fav + valor_seguro) * odd_empate) / denominador
        else:
            # Fallback (Matematicamente impossível cobrir ambos simultaneamente zerados)
            stake_empate = (stake_fav + valor_seguro) / (odd_empate - 1.0) if (odd_empate - 1.0) > 0 else 0
            stake_zebra = (stake_fav + valor_seguro) / (odd_zebra - 1.0) if (odd_zebra - 1.0) > 0 else 0
        st.success("✅ Proteção Matemática Ativada: Empate e Zebra cobrem custos ($0.00), focando no Favorito.")

    st.markdown(f"""
    <div class="card" style="border-color: #FF3B30;">
        <div class="metric-label">COBERTURA {nome_empate}</div>
        <div class="metric-value" style="color:#FF3B30">${stake_empate:,.2f}</div>
        <div class="metric-label">COBERTURA {nome_zebra}</div>
        <div class="metric-value" style="color:#FF3B30">${stake_zebra:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Botao de Stake Minima
    if st.button("🚀 Calcular Stake Mínima (Lucro 10%)"):
        # Verifica se o mercado nao esta muito caro
        soma_cents = cents_fav + cents_empate + cents_zebra
        if soma_cents > 105:
            st.error("❌ Mercado muito caro para operar com proteção. Aguarde as odds subirem.")
        else:
            # Soma de quanto você está gastando para proteger o jogo
            custo_total_protecoes = stake_empate + stake_zebra + valor_seguro
            
            # Preço do favorito (ex: 52 centavos vira 0.52)
            preco_fav = cents_fav / 100
            
            # Verifica se é matematicamente possível
            # Se o favorito está muito barato (cents_fav baixo), o denominador (1 - preco_fav) será alto
            # e a stake necessária pode ficar infinita ou impossível
            if (1 - preco_fav) <= 0:
                st.error("❌ Matematicamente impossível lucrar em todos os cenários com estes preços.")
            else:
                # Stake = (Custo Proteções * 1.10) / (1 - preco_fav)
                stake_minima = (custo_total_protecoes * 1.10) / (1 - preco_fav)
                
                # Atualiza o valor no session_state para persistir
                st.session_state["stake_fav"] = stake_minima
                
                if stake_minima > banca_maxima:
                    st.warning("⚠️ Atenção Cris: Esta operação exige mais do que o seu limite definido. Reduza o seguro ou procure uma Odd maior.")
                else:
                    st.success(f"💰 Stake atualizada para: **${stake_minima:.2f}**")
                st.rerun()
    
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

    st.markdown("---")
    with st.expander("🚦 Guia de Operação", expanded=False):
        st.markdown("""
    **🟢 TUDO VERDE:** Favorito com lucro e Proteções em $0.00. (Sinal para Apostar).
    *Como usar:* Olhou o robô e o card do Favorito está verde e os outros em $0.00? É o sinal 🟢. Pode fazer a aposta no Polymarket sem medo.

    **🟠 LARANJA:** Favorito no prejuízo, mas Proteções em $0.00. (Custo de proteção muito alto).
    *Como usar:* O card do Favorito está negativo (mesmo o empate estando em $0.00)? É o sinal 🟠. Significa que o seguro ou a proteção estão caros demais para essa Odd. Melhor não entrar.

    **🔴 TUDO VERMELHO:** Todos os cards negativos. (Erro de Odd ou Matemática).
    *Como usar:* Apareceu tudo negativo? É o sinal 🔴. Pare tudo e verifique se as odds foram digitadas corretamente.
    """)

# --- CENÁRIOS ---
st.markdown("---")
st.header("🔎 4 Cenários")

# Funcao para exibir os 4 cenarios
def exibir_quatro_cenarios(stake_fav, stake_emp, stake_zeb, stake_seg, odd_fav, odd_emp, odd_zeb, odd_seg, ativar_seguro=True):
    # Cálculo do investimento total
    total = stake_fav + stake_emp + stake_zeb + stake_seg
    
    # Cálculo do lucro real de cada cenário
    l_fav = (stake_fav * odd_fav) - total
    l_emp = (stake_emp * odd_emp) - total
    l_zeb = (stake_zeb * odd_zeb) - total
    l_seg = (stake_seg * odd_seg) - total

    # Estilo CSS para as bordas e cores
    st.markdown("""
        <style>
        .card {
            border: 2px solid #4B5563;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            background-color: #1F2937;
            margin-bottom: 10px;
        }
        .verde { color: #10B981 !important; }
        .laranja { color: #F97316 !important; }
        .vermelho { color: #EF4444 !important; }
        .cinza { color: #9CA3AF !important; }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    titulos = [f"🏆 {nome_fav}", f"⚖️ {nome_empate}", f"🏅 {nome_zebra}", "⚽ Over 1.5"]
    lucros = [l_fav, l_emp, l_zeb, l_seg]

    aviso_laranja = False
    
    for i, col in enumerate(cols):
        cor = "verde" if lucros[i] >= -0.01 else "vermelho"
        valor_str = f"$ {lucros[i]:.2f}"
        roi_str = f"ROI: {((lucros[i]/total)*100):.1f}%"
        
        # Apenas para o favorito
        if i == 0 and lucros[i] < -0.01:
            cor = "laranja"
            aviso_laranja = True
            
        # Para o Over 1.5 se o seguro estiver desativado
        if i == 3 and not ativar_seguro:
            cor = "cinza"
            valor_str = "DESATIVADO"
            roi_str = ""
            
        with col:
            st.markdown(f"""
                <div class="card">
                    <p style="margin:0; font-weight:bold;">{titulos[i]}</p>
                    <h2 class="{cor}" style="margin:10px 0;">{valor_str}</h2>
                    <p style="margin:0; font-size: 0.8em;">{roi_str}</p>
                </div>
            """, unsafe_allow_html=True)

    st.info(f"💰 Investimento Total na Operação: $ {total:.2f}")
    if aviso_laranja:
        st.warning("⚠️ Odd muito baixa para cercar o jogo. Tente tirar o seguro ou aumentar a stake principal.")
    
    return l_fav, l_emp, l_zeb, l_seg, total

# Chama a funcao
lucro_1, lucro_2, lucro_3, lucro_4, custo_total = exibir_quatro_cenarios(
    stake_fav, stake_empate, stake_zebra, valor_seguro, 
    odd_fav, odd_empate, odd_zebra, odd_over, ativar_seguro
)

# --- COMPROVANTE DE ENTRADA ---
st.markdown("---")
if "mostrar_comprovante" not in st.session_state:
    st.session_state["mostrar_comprovante"] = False

col_gerar, col_limpar_comp = st.columns([1, 1])

with col_gerar:
    if st.button("🧾 Gerar Comprovante", use_container_width=True):
        st.session_state["mostrar_comprovante"] = True

with col_limpar_comp:
    if st.button("🗑️ Limpar Comprovante", use_container_width=True):
        st.session_state["mostrar_comprovante"] = False
        st.rerun()

if st.session_state["mostrar_comprovante"]:
    def calc_shares(stake, odd):
        # odd = 100 / cents -> cents = 100 / odd
        # shares = stake / (cents / 100) -> stake / (1 / odd) -> stake * odd
        shares = stake * odd
        return shares
        
    shares_fav = calc_shares(stake_fav, odd_fav)
    shares_emp = calc_shares(stake_empate, odd_empate)
    shares_zeb = calc_shares(stake_zebra, odd_zebra)
    
    st.info(f"📋 **Resumo para Polymarket:**")
    st.markdown(f"✅ Comprar **YES** em `{nome_fav}`: **${stake_fav:,.2f}** (Aprox. {shares_fav:,.2f} Shares)")
    st.markdown(f"✅ Comprar **YES** em `{nome_empate}`: **${stake_empate:,.2f}** (Aprox. {shares_emp:,.2f} Shares)")
    st.markdown(f"✅ Comprar **YES** em `{nome_zebra}`: **${stake_zebra:,.2f}** (Aprox. {shares_zeb:,.2f} Shares)")
    
    texto_comprovante = f"📋 Resumo de Entradas - Lucra+\n==============================\n"
    texto_comprovante += f"✅ Comprar YES em {nome_fav}: ${stake_fav:,.2f} (Aprox. {shares_fav:,.2f} Shares)\n"
    texto_comprovante += f"✅ Comprar YES em {nome_empate}: ${stake_empate:,.2f} (Aprox. {shares_emp:,.2f} Shares)\n"
    texto_comprovante += f"✅ Comprar YES em {nome_zebra}: ${stake_zebra:,.2f} (Aprox. {shares_zeb:,.2f} Shares)\n"
    
    if ativar_seguro and valor_seguro > 0:
        shares_seg = calc_shares(valor_seguro, odd_over)
        st.markdown(f"✅ Comprar **YES** no `Over 1.5`: **${valor_seguro:,.2f}** (Aprox. {shares_seg:,.2f} Shares)")
        texto_comprovante += f"✅ Comprar YES no Over 1.5: ${valor_seguro:,.2f} (Aprox. {shares_seg:,.2f} Shares)\n"
        
    texto_comprovante += "==============================\nBoa sorte!"
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="💾 Baixar Comprovante (TXT)",
        data=texto_comprovante,
        file_name="comprovante_lucra.txt",
        mime="text/plain",
        use_container_width=True
    )

# --- VERIFICACAO DE VIABILIDADE ---
if "Maximizar" in estrategia and lucro_1 <= 0.00:
    st.warning("⚠️ Jogo Inviável: Proteções muito caras para esta Odd")

# Verifica se algum cenario esta negativo
if lucro_1 < 0 or lucro_2 < 0 or lucro_3 < 0:
    st.error("🔴 JOGO INVIÁVEL: O custo das proteções é maior que o lucro do favorito.")
    
    # Sugestao de preco maximo do favorito
    custo_protecoes = stake_empate + stake_zebra + valor_seguro
    odd_minima = (stake_fav + custo_protecoes) / stake_fav
    cents_max_sugerido = int(100 / odd_minima) if odd_minima > 1 else 99
    
    st.warning(f"💡 Para lucrar aqui, você precisa que a Odd do Favorito seja maior que {odd_minima:.2f} (ou {cents_max_sugerido}¢ no Polymarket)")
else:
    st.success("✅ JOGO VIÁVEL: Todos os cenários estão verdes!")

# --- CHECKLIST DE SEGURANCA ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚨 Checklist de Segurança")
soma_total = cents_fav + cents_empate + cents_zebra

if soma_total > 105:
    st.sidebar.error("❌ MERCADO MUITO CARO: A taxa da casa vai comer seu lucro.")
elif lucro_1 < 0:
    st.sidebar.warning("⚠️ AJUSTE NECESSÁRIO: O favorito não cobre as proteções. Aumente a Stake ou mude o jogo.")
else:
    st.sidebar.success("✅ OPERAÇÃO BLINDADA: Lucro garantido em todos os cenários!")

# --- MANUAL NA BARRA LATERAL ---
st.sidebar.markdown("---")
with st.sidebar.expander("📖 Manual de Operação", expanded=False):
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
* Escolha: **{"Polymarket (YES)" if modo_seguro == "Centavos (Polymarket)" else "Casa"}**
* Digite: **{f"{int(100/odd_over)}¢ (Amount: ${valor_seguro:,.2f})" if modo_seguro == "Centavos (Polymarket)" else f"${valor_seguro:,.2f}"}**

---
**💡 Dica para você ler o gráfico:**
* 🔴 **Tudo Vermelho:** O robô está maluco ou as odds são horríveis. Não aposte.
* 🟠 **Empate/Zebra em $ 0.00 e Favorito Laranja:** O robô está certo, mas o jogo não dá lucro (as taxas da casa são maiores que o prêmio).
* 🟢 **Empate/Zebra em $ 0.00 e Favorito Verde:** É aqui que você ganha dinheiro. É o sinal verde para apostar.
""")

st.sidebar.info("💡 Lembrete: O 'NÃO' no favorito substitui as apostas individuais em Empate e Zebra.")

# --- RESET DE DADOS ---
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Limpar Dados"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
