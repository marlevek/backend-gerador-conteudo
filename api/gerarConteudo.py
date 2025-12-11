import streamlit as st
import streamlit.components.v1 as components

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Carrega variáveis de ambiente (OPENAI_API_KEY, etc.)
load_dotenv()


# ==============================
# Botão "Copiar conteúdo"
# ==============================
def botao_copiar(texto: str, label: str = "📋 Copiar texto gerado"):
    components.html(
        f"""
        <button onclick="
            navigator.clipboard.writeText(`{texto}`);
            this.innerText = '✅ Copiado!';
            setTimeout(() => this.innerText = '{label}', 2000);
        " style="
            padding: 0.5rem 1rem;
            border-radius: 6px;
            border: 1px solid #ccc;
            cursor: pointer;
            background-color: #f0f2f6;
        ">
            {label}
        </button>
        """,
        height=50,
    )


# ==============================
# Obter LLM da OpenAI
# ==============================
def get_llm(model_id: str, temperature: float):
    """
    model_id: ex. 'gpt-4.1-mini', 'gpt-4.1', etc.
    """
    return ChatOpenAI(
        model=model_id,
        temperature=temperature,
        max_retries=2,
    )


# ==============================
# Geração de conteúdo (post estático + vídeo curto)
# ==============================
def llm_generate(
    llm,
    tema: str,
    plataforma: str,
    tom: str,
    tamanho: str,
    publico: str,
    incluir_cta: bool,
    incluir_hashtags: bool,
    palavras_chave: str,
    nicho: str,
    incluir_sugestoes_imagens: bool,
):
    system_prompt = """
Você é um especialista em marketing digital com foco em SEO, copywriting e escrita persuasiva.
Você escreve sempre em português do Brasil, em linguagem clara, moderna e escaneável.
Adapte o texto ao nicho informado, ao tipo de público e à plataforma escolhida.
Traga ideias específicas, práticas e aplicáveis para o contexto do cliente.
Nicho do cliente: {nicho}
"""

    # Detectar se é plataforma de vídeo curto / reels
    plataformas_video_curto = [
        "Instagram Reels",
        "YouTube Shorts",
        "TikTok (vídeo curto)",
    ]
    eh_video_curto = plataforma in plataformas_video_curto

    user_prompt = f"""
Escreva um conteúdo com SEO otimizado sobre o tema: '{tema}'.

- Plataforma onde será publicado: {plataforma}
- Tom do texto: {tom}
- Público-alvo: {publico}
- Comprimento desejado: {tamanho}
- {"Inclua uma chamada para ação clara e forte ao final." if incluir_cta else "Não inclua chamada para ação."}
- {"Inclua ao final do texto uma lista de hashtags relevantes para esta publicação." if incluir_hashtags else "Não inclua hashtags."}
{f"- Palavras-chave obrigatórias para SEO: {palavras_chave}" if palavras_chave else ""}
{ "- Ao final, adicione um subtítulo 'Sugestões de imagens:' e liste de 3 a 5 ideias de imagens específicas para essa publicação, adequadas à plataforma selecionada." if incluir_sugestoes_imagens else "" }
"""

    if eh_video_curto:
        user_prompt += """
Além disso, como a plataforma selecionada é de VÍDEO CURTO (Reels / Shorts / TikTok), faça também:

1. Crie uma seção chamada **Ideia de vídeo**, com um resumo em 2–3 linhas do conceito do vídeo.
2. Crie uma seção **Roteiro sugerido**, em formato de tópicos, com:
   - Hook (primeiros 3–5 segundos para prender atenção)
   - Desenvolvimento (o que aparece em seguida, em até 3 blocos)
   - CTA final (o que a pessoa deve fazer depois de ver o vídeo).
3. Crie uma seção **Sugestões de cenas**, listando de 3 a 5 cenas/enquadramentos práticos que podem ser gravados (ex.: close no rosto do profissional, bastidores da clínica, tela de antes/depois, etc.).
4. Crie uma seção **Sugestões de músicas**, indicando 3 a 5 estilos ou tipos de trilha sonora adequados (ex.: “lofi motivacional”, “pop animado”, “trilha relaxante”, etc.), sem citar músicas com direitos autorais específicos.

Mantenha tudo em um único texto, bem organizado em seções, pronto para uso.
"""

    regras_resposta = """
Regras importantes da resposta:
1. Entregue apenas o texto final (sem explicar o passo a passo).
2. Não use aspas envolvendo o texto inteiro.
3. Estruture o conteúdo em parágrafos curtos e, se fizer sentido, use listas ou bullets.
"""

    user_prompt += regras_resposta

    template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{user_prompt}"),
        ]
    )

    chain = template | llm | StrOutputParser()

    res = chain.invoke(
        {
            "nicho": nicho or "negócios locais",
            "user_prompt": user_prompt,
        }
    )
    return res


# ==============================
# Configuração da página
# ==============================
st.set_page_config(
    page_title="Gerador de Conteúdo com IA",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Gerador de conteúdo com IA para negócios")
st.caption("Focado em SEO, copy persuasiva e posts prontos para redes sociais.")


# ==============================
# Sidebar – Configurações da IA
# ==============================
with st.sidebar:
    st.header("⚙️ Configurações da IA")

    modelo_opcao = st.selectbox(
        "Modelo OpenAI:",
        [
            "gpt-4.1-mini",
            "gpt-4.1",
        ],
    )

    temperatura = st.slider(
        "Criatividade (temperature):",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.05,
        help="Valores mais baixos = mais objetivo; valores mais altos = mais criativo.",
    )

    st.markdown("---")
    st.markdown("**Dica:** use nichos específicos, ex.: “clínica de psicologia”, “empresa de ar-condicionado”.")


# Inicializa histórico na sessão
if "historico" not in st.session_state:
    st.session_state.historico = []


# ==============================
# Abas
# ==============================
aba_gerar, aba_sobre = st.tabs(["✍️ Gerar conteúdo", "ℹ️ Sobre o app"])


# ------------------------------
# ABA 1 – Gerar conteúdo
# ------------------------------
with aba_gerar:
    col_form, col_hist = st.columns([2, 1])

    with col_form:
        st.subheader("🧾 Briefing do conteúdo")

        nicho = st.text_input(
            "Nicho / Tipo de negócio:",
            placeholder="Ex: clínica de psicologia, consultório odontológico, empresa de ar-condicionado...",
        )

        topic = st.text_input(
            "Tema do conteúdo:",
            placeholder="Ex: saúde mental, manutenção preventiva de ar-condicionado, alimentação saudável...",
        )

        platform = st.selectbox(
            "Plataforma:",
            [
                "Instagram (feed)",
                "Instagram Reels",
                "Facebook (feed)",
                "LinkedIn",
                "Blog",
                "YouTube (descrição de vídeo)",
                "YouTube Shorts",
                "TikTok (vídeo curto)",
            ],
        )

        # Detecta se é plataforma de vídeo curto
        plataformas_video_curto = [
            "Instagram Reels",
            "YouTube Shorts",
            "TikTok (vídeo curto)",
        ]
        eh_video_curto = platform in plataformas_video_curto

        if eh_video_curto:
            st.markdown("##### 🎬 Modo vídeo curto (Reels / Shorts / TikTok)")
            st.caption(
                "Além do texto, serão geradas ideia de vídeo, roteiro, sugestões de cenas e sugestões de músicas."
            )
        else:
            st.markdown("##### 📝 Modo post estático")
            st.caption(
                "Geração focada em texto para feed, blog ou descrição, com possibilidade de sugestões de imagens."
            )

        tone = st.selectbox("Tom:", ["Normal", "Informativo", "Inspirador", "Urgente", "Informal", "Educativo"])

        length = st.selectbox("Tamanho:", ["Curto", "Médio", "Longo"])

        audience = st.selectbox(
            "Público-alvo:",
            [
                "Geral",
                "Jovens adultos",
                "Famílias",
                "Idosos",
                "Adolescentes",
                "Empresários",
                "Profissionais da saúde",
            ],
        )

        cta = st.checkbox("Incluir CTA (chamada para ação)")
        hashtags = st.checkbox("Incluir hashtags")

        sugestoes_imagens_label = (
            "Incluir sugestões de cenas/imagens de apoio para o vídeo"
            if eh_video_curto
            else "Incluir sugestões de imagens para o post"
        )
        sugestoes_imagens = st.checkbox(sugestoes_imagens_label)

        keywords = st.text_area(
            "Palavras-chave (SEO):",
            placeholder="Ex: bem-estar, medicina preventiva, manutenção preventiva, PMOC...",
        )

        gerar = st.button("🚀 Gerar conteúdo", type="primary")

        if gerar:
            if not topic:
                st.warning("Informe pelo menos o tema do conteúdo.")
            else:
                try:
                    with st.spinner("Gerando conteúdo, aguarde..."):
                        llm = get_llm(modelo_opcao, temperatura)

                        res = llm_generate(
                            llm=llm,
                            tema=topic,
                            plataforma=platform,
                            tom=tone,
                            tamanho=length,
                            publico=audience,
                            incluir_cta=cta,
                            incluir_hashtags=hashtags,
                            palavras_chave=keywords,
                            nicho=nicho,
                            incluir_sugestoes_imagens=sugestoes_imagens,
                        )

                    st.success("✅ Conteúdo gerado com sucesso!")

                    st.text_area(
                        "📝 Conteúdo gerado:",
                        value=res,
                        height=350,
                        key="conteudo_gerado",
                    )

                    botao_copiar(res)

                    # Salvar no histórico
                    st.session_state.historico.append(
                        {
                            "tema": topic,
                            "plataforma": platform,
                            "tom": tone,
                            "público": audience,
                            "tamanho": length,
                            "texto": res,
                            "modelo": modelo_opcao,
                            "nicho": nicho,
                        }
                    )

                except Exception as e:
                    st.error(f"Erro ao chamar a IA: {e}")

    with col_hist:
        st.subheader("📚 Histórico de conteúdos")

        if st.session_state.historico:
            for i, item in enumerate(reversed(st.session_state.historico), 1):
                with st.expander(f"{i}. {item['tema']} ({item['plataforma']}) – {item['modelo']}"):
                    if item.get("nicho"):
                        st.markdown(f"**Nicho:** {item['nicho']}")
                    st.markdown(f"**Tom:** {item['tom']}")
                    st.markdown(f"**Público-alvo:** {item['público']}")
                    st.markdown(f"**Tamanho:** {item['tamanho']}")
                    st.markdown("**Texto gerado:**")
                    st.markdown(item["texto"])
        else:
            st.info("Nenhum conteúdo gerado ainda.")


# ------------------------------
# ABA 2 – Sobre o app
# ------------------------------
with aba_sobre:
    st.subheader("ℹ️ Sobre o Gerador de Conteúdo com IA")

    st.markdown(
        """
Este gerador foi pensado para **profissionais e negócios** que precisam produzir conteúdo recorrente,
mas não têm tempo para escrever tudo do zero.

Com poucos cliques você gera textos otimizados para:

- Instagram (feed e Reels)
- Facebook (feed)
- LinkedIn
- Blog
- Descrição de vídeos no YouTube
- YouTube Shorts
- TikTok (vídeos curtos)

Sempre adaptando para:

- Nicho do negócio (ex.: clínica de psicologia, consultório odontológico, empresa de ar-condicionado)
- Público-alvo
- Tom da comunicação
- Tamanho do conteúdo
        """
    )

    st.markdown("---")
    st.markdown("### 🧭 Como funciona na prática")

    st.markdown(
        """
1. **Informe o nicho** do seu negócio (ou do seu cliente).  
2. **Defina o tema** do conteúdo que deseja gerar.  
3. Escolha a **plataforma**, o **tom**, o **tamanho** e o **público-alvo**.  
4. Opcionalmente, informe **palavras-chave de SEO**, marque se deseja **CTA**, **hashtags** e **sugestões de imagens/cenas**.  
5. Clique em **“Gerar conteúdo”** e copie o texto pronto para utilizar nas suas redes.

Se a plataforma for de **vídeo curto** (Reels / Shorts / TikTok), o app gera também:

- Ideia de vídeo  
- Roteiro sugerido  
- Sugestões de cenas  
- Sugestões de músicas (por estilo)
        """
    )

    st.markdown("---")
    st.markdown("### 💼 Possíveis planos (para vender como serviço)")

    st.markdown(
        """
**Plano Starter**  
- Até 30 conteúdos por mês  
- Foco em 1 rede social  
- Indicado para autônomos e pequenos negócios

**Plano Profissional**  
- Até 80 conteúdos por mês  
- Até 3 redes (Instagram, Facebook, LinkedIn)  
- Sugestões de imagens e vídeos incluídas  
- Foco em negócios locais e profissionais de saúde

**Plano Agência**  
- Conteúdos ilimitados sob demanda  
- Múltiplos nichos e clientes  
- Ideal para social media, agências e consultorias

Esses planos são apenas um modelo — você pode adaptar nomes, limites e preços para a sua realidade.
        """
    )

    st.markdown("---")
    st.markdown("### 🛠️ Tecnologias e arquitetura")

    st.markdown(
        """
- **Frontend / UI:** Streamlit  
- **IA:** Modelos OpenAI (via `langchain-openai`)  
- **Orquestração:** LangChain (prompt, cadeia, parser)  
- **Infraestrutura sugerida:** Railway / Render / outro provedor Python

Se você quiser evoluir este projeto para um SaaS completo (com login, créditos por usuário, painel admin e cobrança recorrente),
dá para aproveitar essa base e ir crescendo aos poucos.
        """
    )
