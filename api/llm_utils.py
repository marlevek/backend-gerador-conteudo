from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def gerar_conteudo(
    modelo,
    temperatura,
    tema,
    plataforma,
    tom,
    tamanho,
    publico,
    incluir_cta,
    incluir_hashtags,
    palavras_chave,
    nicho,
    incluir_sugestoes_imagens,
):
    system_prompt = """
Você é um especialista em marketing digital com foco em SEO, copywriting e escrita persuasiva.
Você escreve sempre em português do Brasil, em linguagem clara, moderna e escaneável.
Adapte o texto ao nicho informado, ao tipo de público e à plataforma escolhida.
Nicho do cliente: {nicho}
"""

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
- {"Inclua uma CTA no final." if incluir_cta else "Não inclua CTA."}
- {"Inclua hashtags relevantes ao final." if incluir_hashtags else "Não inclua hashtags."}
{f"- Palavras-chave importantes para SEO: {palavras_chave}" if palavras_chave else ""}
{ "- Inclua sugestões de imagens ao final." if incluir_sugestoes_imagens else "" }
"""

    if eh_video_curto:
        user_prompt += """
Como é vídeo curto (Reels / Shorts / TikTok), gere também:
1. Ideia de vídeo
2. Roteiro sugerido
3. Sugestões de cenas
4. Sugestões de músicas por estilo
"""

    regras = """
Regras importantes:
1. Não explique o passo a passo.
2. Não envolva o texto inteiro em aspas.
3. Estruture em parágrafos curtos e listas quando fizer sentido.
"""

    user_prompt += regras

    template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{user_prompt}"),
        ]
    )

    llm = ChatOpenAI(model=modelo, temperature=temperatura, max_retries=2)

    chain = template | llm | StrOutputParser()

    resultado = chain.invoke(
        {
            "nicho": nicho or "negócios locais",
            "user_prompt": user_prompt,
        }
    )

    return resultado
