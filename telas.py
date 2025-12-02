import streamlit as st
import pandas as pd
from utils import carregar_enderecos, salvar_enderecos, excluir_enderecos, extrai_coord, vectura, salva_historico, reduzir_para_historico, limpar_historico, carregar_fixos, salvar_fixos, fixar_calculo, limpar_fixos, gerar_mapa
from streamlit_folium import st_folium
import folium

def tela_0():
    
    st.markdown("""<div class="app-info">
  <style>
    .app-info {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
      color: #e9eef8;
      background: linear-gradient(180deg, #000000 0%, #0d0d0d 100%);
      border-radius: 12px;
      padding: 28px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.6);
      max-width: 920px;
      margin: 12px auto;
      line-height: 1.55;
    }

    .app-info h1 {
      margin: 0 0 10px 0;
      font-size: 28px;
      color: #ffffff;
      letter-spacing: -0.3px;
    }

    .accent {
      color: #0d6efd;
      font-weight: 600;
    }

    .app-info h2 {
      color: #dfe9ff;
      margin-top: 20px;
      margin-bottom: 8px;
      font-size: 18px;
    }

    .app-info p, .app-info li {
      color: #cbd8ff;
      font-size: 15px;
    }

    .steps {
      background: rgba(13,110,253,0.06);
      padding: 14px;
      border-radius: 8px;
      border: 1px solid rgba(13,110,253,0.12);
      margin-top: 8px;
    }

    .steps ol {
      margin: 0;
      padding-left: 18px;
    }

    .bullet {
      display:inline-block;
      width:10px;
      height:10px;
      background:#0d6efd;
      border-radius:50%;
      margin-right:8px;
      vertical-align:middle;
    }

    .features {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-top: 12px;
    }

    .feature-card {
      background: rgba(255,255,255,0.03);
      border-radius: 8px;
      padding: 12px;
      border: 1px solid rgba(255,255,255,0.03);
    }

    @media (max-width:600px){
      .app-info { padding: 18px; }
      .app-info h1 { font-size: 22px; }
    }
  </style>

  <h1>Sobre o Aplicativo: </h1>
  <p>O Vectura foi criado para <span class="accent">simplificar e agilizar</span> um cálculo essencial no dia a dia da operação logística: a comparação de custos entre dois cenários de transporte — sem a necessidade de planilhas complexas.</p>

  <h2>Cenário 1 – <span class="accent">Operação direta</span></h2>
  <div class="steps">
    <ol>
      <li><strong>O caminhão sai carregado (6 eixos)</strong> da Origem.</li>
      <li>Descarrega no <strong>Destino 1</strong>.</li>
      <li>Retorna para a Origem <strong>descarregado (3 eixos)</strong>.</li>
    </ol>
    <p style="margin-top:8px"><em>Este é o modelo mais simples: ida carregado, volta descarregado.</em></p>
  </div>

  <h2>Cenário 2 – <span class="accent">Operação com recarga</span></h2>
  <div class="steps">
    <ol>
      <li><strong>O caminhão sai carregado (6 eixos)</strong> da Origem.</li>
      <li>Descarrega no <strong>Destino 1</strong>.</li>
      <li>Segue <strong>descarregado (3 eixos)</strong> até o <strong>Ponto de Recarga</strong> (pode ser diferente da Origem).</li>
      <li>Recarrega e segue <strong>carregado (6 eixos)</strong> até o <strong>Destino 2</strong>.</li>
      <li>Retorna <strong>descarregado (3 eixos)</strong> à Origem.</li>
    </ol>
    <p style="margin-top:8px"><em>Neste cenário há uma etapa extra de recarga e um segundo destino final, tornando custos e distâncias mais complexos de calcular manualmente.</em></p>
  </div>

  <h2>O que o aplicativo faz por você</h2>
  <div class="features">
    <div class="feature-card">
      <div class="bullet"></div><strong>Diferença total de quilômetros rodados</strong>
    </div>
    <div class="feature-card">
      <div class="bullet"></div><strong>Diferença de pedágio pago</strong><br><small>(considerando eixos e tarifas)</small>
    </div>
    <div class="feature-card">
      <div class="bullet"></div><strong>Cálculo do Frete</strong><br><small>Baseado no valor por km informado</small>
    </div>
  </div>

  <p style="margin-top:14px">Tudo isso em segundos — com precisão, transparência e sem depender de planilhas externas.</p>
</div>""", unsafe_allow_html=True)

def tela_1():
    st.subheader("💰 Cálculo Frete") # Subtítulo da página Vectura
    st.divider()

    # ---- Sidebar ----
    origens = [None] + list(st.session_state["enderecos"]["Origem"].keys())
    destinos = [None] + list(st.session_state["enderecos"]["Destino"].keys())
    recargas = [None] + list(st.session_state["enderecos"]["Recarga"].keys())

    st.sidebar.subheader("⚙️ Chave API")

    api_key = st.sidebar.text_input("Insira a chave de API")

    st.sidebar.divider()

    st.sidebar.subheader("🚚 Locais de Origem/Destino") # Título do Sidebar
    
    origem = st.sidebar.selectbox(label="Origem:", options=origens, format_func=lambda x: "Selecione..." if x is None else x, placeholder="Selecione uma das opções.") # Selectbox para endereço de saída do caminhão
    if origem == None:
      pass

    else:
      endereco_origem = st.session_state["enderecos"]["Origem"][origem]["endereco_formatado"]
      st.sidebar.write(endereco_origem)

    destino = st.sidebar.selectbox(label="Destino:", options=destinos, format_func=lambda x: "Selecione..." if x is None else x, placeholder="Selecione uma das opções.") # Selectbox para endereço de entrega do caminhão

    if destino == None:
        pass
    
    else:
      endereco_destino = st.session_state["enderecos"]["Destino"][destino]["endereco_formatado"]
      st.sidebar.write(endereco_destino)

    recarga = st.sidebar.selectbox(label="Recarga:", options=recargas, format_func=lambda x: "Selecione..." if x is None else x, placeholder="Selecione uma das opções.") # Selectbox para endereço de entrega do caminhão

    if recarga == None:
      pass
    
    else:
      endereco_recarga = st.session_state["enderecos"]["Recarga"][recarga]["endereco_formatado"]
      st.sidebar.write(endereco_recarga)
    
    opcoes_segundo = [None] + [e for e in list(st.session_state["enderecos"]["Destino"].keys()) if e != destino]

    segundo_destino = st.sidebar.selectbox(label="Segundo Destino:", options=opcoes_segundo, format_func=lambda x: "Selecione..." if x is None else x, placeholder="Selecione uma das opções.") # Text input para endereço de entrega complementar do caminhão

    if segundo_destino == None:
       pass
    
    else:
       endereco_segundo = st.session_state["enderecos"]["Destino"][segundo_destino]["endereco_formatado"]
       st.sidebar.write(endereco_segundo)

    st.sidebar.divider()

    st.sidebar.subheader("💸 Racional (R$/Km rodado)")

    racional = st.sidebar.number_input("Defina o valor a ser cobrado por km rodado: ", 0.00, 1000.00, 12.00, 0.1)

    st.sidebar.write("")

    botao_rodar = st.sidebar.button("Rodar") # Botão para rodar o modelo

    # ---- Fim do Sidebar ----

    # ---- Tela Principal ----

    if origem == None and destino == None and recarga == None and segundo_destino == None:
      # Gera o mapa para ficar exposto na tela inicial
      localizacao_inicial = (-23.5505, -46.6333) 
      mapa = folium.Map(location=localizacao_inicial, zoom_start=9)

      st_folium(mapa, width=1200, height=600)
    
    else:

      # Gera o mapa para ficar exposto na tela inicial
      localizacao_inicial = (-23.5505, -46.6333) 
      mapa = folium.Map(location=localizacao_inicial, zoom_start=9)

      if origem is not None:
        dados = st.session_state["enderecos"]["Origem"][origem]
        folium.Marker(
            location=[dados["latitude"], dados["longitude"]],
            popup=f"Origem: {origem}",
            icon=folium.Icon(color="blue")
        ).add_to(mapa)

      # Exibir pin do destino
      if destino is not None:
          dados = st.session_state["enderecos"]["Destino"][destino]
          folium.Marker(
              location=[dados["latitude"], dados["longitude"]],
              popup=f"Destino: {destino}",
              icon=folium.Icon(color="black")
          ).add_to(mapa)

      # Exibir pin da recarga
      if recarga is not None:
          dados = st.session_state["enderecos"]["Recarga"][recarga]
          folium.Marker(
              location=[dados["latitude"], dados["longitude"]],
              popup=f"Recarga: {recarga}",
              icon=folium.Icon(color="red")
          ).add_to(mapa)

      if segundo_destino is not None:
         dados = extrai_coord(segundo_destino, api_key)
         folium.Marker(
              location=[dados[1][0], dados[1][1]],
              popup=f"Segundo Destino: {segundo_destino}",
              icon=folium.Icon(color="orange")
          ).add_to(mapa)

      st_folium(mapa, width=900, height=600)

    # ---- Fim da Tela Principal ----

      if botao_rodar: # Se o botão "Rodar" for selecionado:

        status, mensagem, dados = vectura(origem=endereco_origem, 
                          destino=endereco_destino, 
                          recarga=endereco_recarga, 
                          destino_2=endereco_segundo,
                          chave_api = api_key,
                          racional=racional
                          ) # Roda o modelo
        
        if status:

          st.session_state["resultados_vectura"] = dados
          st.session_state["rodou_vectura"] = True
          st.session_state["mensagem_vectura"] = mensagem
      
      if st.session_state.get("rodou_vectura", False):

        dados = st.session_state["resultados_vectura"]
        mensagem = st.session_state["mensagem_vectura"]

        st.session_state["polilinha_1"] = dados["polilinha_1"]
        st.session_state["polilinha_2"] = dados["polilinha_2"]

        st.session_state["mapa_1"] = gerar_mapa(dados["polilinha_1"])
        st.session_state["mapa_2"] = gerar_mapa(dados["polilinha_2"])

        dados_reduzidos = reduzir_para_historico(dados)
        salva_historico(st.session_state["historico"], dados_reduzidos)

        col_mensagem, col_botao = st.columns([0.9, 0.1])

        col_mensagem.success(mensagem)
        botao_fixar = col_botao.button("📌 Fixar Cálculo")

        abas = st.tabs(["Valor Sugerido", "Mapas", "Distâncias", "Pedágios"]) # Criação de abas para apresentação dos resultados

        with abas[0]:
          st.subheader("💰 Valor Sugerido ao Cliente")
          st.metric("Valor Excedente / Sugerido", dados['valor_excedente'])

          st.divider()

          st.subheader("Resumo Geral")
          col1, col2 = st.columns(2)

          with col1:
              st.write("### Ida e Volta Simples")
              st.metric("Total (km)", dados["km_total_simples"])
              st.metric("Total (tempo)", dados["tempo_total_simples"])
              st.metric("Valor Pedágios", dados["valor_pedagio_total_simples"])

          with col2:
              st.write("### Rota Completa (Com Recarga)")
              st.metric("Total (km)", dados["km_total"])
              st.metric("Total (tempo)", dados["tempo_total"])
              st.metric("Valor Pedágios", dados["valor_pedagios_total"])

          st.divider()

          st.write("### Diferenças Entre Rotas")
          colA, colB, colC = st.columns(3)
          colA.metric("Dif. km", dados["km_diff"])
          colB.metric("Dif. tempo", dados["tempo_diff"])
          colC.metric("Dif. tarifas", dados["tarifas_diff"])

          st.divider()
          st.write("### Racional do Cálculo")
          st.info(dados["racional"])
        
        with abas[1]:
          st.subheader("🗺️ Mapa - Ida e Volta")
          st_folium(st.session_state["mapa_1"], width=1200, height=300)

          st.divider()

          st.subheader("🗺️ Mapa - Rota Completa")
          st_folium(st.session_state["mapa_2"], width=1200, height=300)
        # st.subheader("🗺️ Mapa - Ida e Volta")
        # polilinha_1 = dados["polilinha_1"]
        # mapa_1 = gerar_mapa(polilinha_1)
        # st_folium(mapa_1, width=400, height=300)


        # st.subheader("🗺️ Mapa - Rota Completa")
        # polilinha_2 = dados["polilinha_2"]  
        # mapa_2 = gerar_mapa(polilinha_2)
        # st_folium(mapa_2, width=400, height=300)

        # st.divider()

        # col10, col11, col12, col13 = st.columns(4)

        # st.subheader("🗺️ Mapas - Rota Completa")

        # col10.subheader("🗺️ Rota - Trecho 1")
        # col10.image(dados["mapa_rota_trecho_1"])

        # col11.subheader("🗺️ Rota - Trecho 2")
        # col11.image(dados["mapa_rota_trecho_2"])

        # col12.subheader("🗺️ Rota - Trecho 3")
        # col12.image(dados["mapa_rota_trecho_3"]) 

        # col13.subheader("🗺️ Rota - Trecho 4")
        # col13.image(dados["mapa_rota_trecho_4"])        

        with abas[2]:
          st.subheader("📏 Distâncias - Ida e Volta")
          col1, col2 = st.columns(2)

          col1.metric("Ida", dados["km_ida"])
          col2.metric("Volta", dados["km_volta"])

          st.divider()

          st.subheader("📏 Distâncias - Rota Completa")

          col3, col4, col5, col6 = st.columns(4)

          col3.metric("Trecho 1", dados["km_trecho_1"])
          col4.metric("Trecho 2", dados["km_trecho_2"])
          col5.metric("Trecho 3", dados["km_trecho_3"])
          col6.metric("Trecho 4", dados["km_trecho_4"])

          st.divider()

          st.write("")
          st.write("### Diferenças entre rotas")
          st.metric("Diferença Total", dados["km_diff"])
          
        with abas[3]:
          st.subheader("🛣️ Pedágios — Ida e Volta Simples")
          st.metric("Valor Total", dados["valor_pedagio_total_simples"])

          # st.write("### Lista Pedágios (Simples)")
          # st.table(pd.DataFrame(dados["lista_pedagios_total_simples"], columns=["Pedágio"]))

          st.divider()

          st.subheader("🛣️ Pedágios — Rota Completa")
          st.metric("Valor Total", dados["valor_pedagios_total"])

          # st.write("### Lista Pedágios (Completa)")
          # st.table(pd.DataFrame(dados["lista_pedagios_total"], columns=["Pedágio"]))

          st.divider()

          st.subheader("Diferenças entre rotas")
          colD1, colD2 = st.columns(2)
          colD1.metric("Dif. Tarifas", dados["tarifas_diff"])
          colD2.metric("—", "")
        
        if botao_fixar:

            dados_fixar = reduzir_para_historico(dados)
            status, mensagem = fixar_calculo(dados_fixar)

            if status:
                # >>>> ATUALIZA O SESSION STATE!
                st.session_state["fixos"] = carregar_fixos()

                st.success(mensagem)
            else:
                st.error(mensagem)
          

def tela_2():

    tabs = st.tabs(["Registro/Exclusão", "Locais Registrados"]) # Criação de 2 abas

    # Na primeira aba:
    with tabs[0]:

        col1, divider, col2 = st.columns([1, 0.05, 1]) # Criação das colunas dando um espaço entre as duas colunas principais

        # ---- Coluna 1 ----

        col1.subheader("📍 Registro de Endereços") # Subtítulo da Primeira Coluna
        col1.divider()
        
        tipo = col1.selectbox("Qual tipo de endereço você deseja registrar?", options=["Origem", "Destino", "Recarga"], placeholder="Selecione uma das opções.") # Selectbox para escolha da opção de registro de endereço

        nome_salvar = col1.text_input("Salvar como:", placeholder = "Insira o nome desejado para salvar o endereço.") # Text input para o nome que o endereço será salvo
        endereco_salvar = col1.text_input("Endereço:", placeholder = "Insira o endereço.") # Text input para o endereço em si
        api_key = col1.text_input("Chave:", placeholder="Insira a chave")

        botao_salvar_endereco = col1.button("Salvar Endereço") # Cria um botão para salvar o endereço.

        if botao_salvar_endereco == True: # Se a seleção feita acima for "Saída", procurar na lista de endereços de Saída. Se não tiver o endereço, salvar com o nome inputado.
            sucesso, mensagem = salvar_enderecos(tipo, nome_salvar, endereco_salvar, st.session_state["enderecos"], api_key)

            # Caso as entradas passem pelas validações da função salvar_enderecos, solta uma mensagem de sucesso e carrega os enderecos

            if sucesso: 
                col1.success(mensagem)
                st.session_state["enderecos"] = carregar_enderecos()
            
            # Caso contrário, solta uma mensagem de erro.

            else:
                col1.error(mensagem)

        # ---- Coluna 2 ----

        col2.subheader("🗑️ Exclusão de Endereços") # Subtítulo da Segunda Coluna
        col2.divider()

        tipo = col2.selectbox("Qual tipo de endereço você deseja excluir?", options=["Origem", "Destino", "Recarga"], placeholder="Selecione uma das opções.") # Selectbox para escolha da opção de registro de endereço

        nomes = [None] + list(st.session_state["enderecos"][tipo].keys())

        nome_excluir = col2.selectbox("Selecione o endereço que você deseja excluir.", options=nomes, format_func=lambda x: "Selecione..." if x is None else x, placeholder="Selecione uma das opções.") # Text input para o nome do endereço que será excluído

        if nome_excluir == None:
            pass
        
        else:

          endereco_excluir = st.session_state["enderecos"][tipo][nome_excluir]["endereco_formatado"] # Escreve o endereço do nome selecionado para confirmação da exclusão
          col2.write(f"_*Endereço correspondente*_: {endereco_excluir}")

        botao_excluir_endereco = col2.button("Excluir Endereço") # Cria um botão para excluir o endereço.

        if botao_excluir_endereco == True: # Procura na lista da opção selecionada o nome do endereço, se passar pela validação, o endereço excluído
            sucesso2, mensagem2 = excluir_enderecos(tipo, nome_excluir, st.session_state["enderecos"])

            # Se a exclusão for bem sucedida, solta uma mensagem de sucesso e atualiza a lista de endereços salvos

            if sucesso2:
                col2.success(mensagem2)
                st.session_state["enderecos"] = carregar_enderecos()

            # Caso contrário, solta uma mensagem de erro
            
            else:
                col2.error(mensagem2)
    
    with tabs[1]:

        data_origens = st.session_state["enderecos"]["Origem"]
        data_destino = st.session_state["enderecos"]["Destino"]
        data_recarga = st.session_state["enderecos"]["Recarga"]

        

        df_origem = pd.DataFrame([
                    {
                        "Nome": nome,
                        "Endereço": dados["endereco_formatado"]
                    }
                    for nome, dados in data_origens.items()
                ]) # Cria o DataFrame com os endereços de saída 
        
        df_destino = pd.DataFrame([
                    {
                        "Nome": nome,
                        "Endereço": dados["endereco_formatado"]
                    }
                    for nome, dados in data_destino.items()
                ]) # Cria o DataFrame com os endereços de entrega
        
        df_recarga = pd.DataFrame([
                    {
                        "Nome": nome,
                        "Endereço": dados["endereco_formatado"]
                    }
                    for nome, dados in data_recarga.items()
                ]) # Cria o DataFrame com os endereços de recarga

        col3, col4, col5 = st.columns([1, 1, 1])

        col3.subheader("🏭 Locais de Saída") # Subtítulo da primeira coluna
        col3.divider()
        col3.dataframe(df_origem) # Expõe o DF de origem criado acima

        col4.subheader("📦 Locais de Entrega") # Subtítulo da segunda coluna
        col4.divider()
        col4.dataframe(df_destino) # Expõe o DF de destino criado acima

        col5.subheader("🔃 Locais de Recarga") # Subtítulo da segunda coluna
        col5.divider()
        col5.dataframe(df_recarga) # Expõe o DF de recarga criado acima


def tela_3():
    abas = st.tabs(["Histórico de Consultas", "Consultas Fixadas"])

    with abas[0]:

      col1, col2 = st.columns([0.872, 0.128])

      col1.subheader("🕛 Histórico de Consultas")

      botao_limpar_historico = col2.button("🧹 Limpar Histórico")

      if botao_limpar_historico:
          if st.session_state["historico"]:

              status, mensagem = limpar_historico()

              if status:
                  st.session_state["historico"] = []
                  st.success(mensagem)
              else:
                  st.error("❌ Não foi possível apagar o histórico")

      if st.session_state["historico"]:

        df_historico = pd.DataFrame(st.session_state["historico"])

        df_historico = df_historico.rename(
           columns={"origem": "Origem",
                    "destino_1": "Destino 1",
                    "recarga": "Recarga",
                    "destino_2": "Destino 2",
                    "km_total_simples": "KM Total (Simples)",
                    "tempo_total_simples": "Tempo Total (Simples)",
                    "qtd_pedagio_total_simples": "Qtd. Pedágios (Simples)",
                    "valor_pedagio_total_simples": "Valor Pedágios (Simples)",
                    "lista_pedagios_total_simples": "Lista Pedágios (Simples)",
                    "km_total": "KM Total",
                    "tempo_total": "Tempo Total",
                    "qtd_total_pedagios": "Qtd. Total Pedágios",
                    "valor_pedagios_total": "Valor Total Pedágios",
                    "lista_pedagios_total": "Lista Total Pedágios",
                    "km_diff": "Diferença KM",
                    "tempo_diff": "Diferença Tempo",
                    "qtd_pedagio_diff": "Diferença Pedágios",
                    "tarifas_diff": "Diferença Tarifas",
                    "racional": "Racional",
                    "valor_excedente": "Valor Excedente"}
        )

        st.dataframe(df_historico)
      else:
        st.info("Nenhuma consulta realizada ainda.")
          
    with abas[1]:
      
      col1, col2 = st.columns([0.84, 0.16])

      col1.subheader("📌 Consultas Fixas")

      botao_limpar_fixo = col2.button("🧹 Limpar Consultas Fixas")

      if botao_limpar_fixo:
        if st.session_state["fixos"]:

          status, mensagem = limpar_fixos(st.session_state["fixos"])

          if status:
              # >>>> LIMPA O SESSION STATE
              st.session_state["fixos"] = []

              st.success(mensagem)
          else:
              st.error("❌ Não foi possível apagar as consultas fixas")
    
        else:
           pass

      if st.session_state["fixos"]:

        df_fixos = pd.DataFrame(st.session_state["fixos"])

        df_fixos = df_fixos.rename(
           columns={"origem": "Origem",
                    "destino_1": "Destino 1",
                    "recarga": "Recarga",
                    "destino_2": "Destino 2",
                    "km_total_simples": "KM Total (Simples)",
                    "tempo_total_simples": "Tempo Total (Simples)",
                    "qtd_pedagio_total_simples": "Qtd. Pedágios (Simples)",
                    "valor_pedagio_total_simples": "Valor Pedágios (Simples)",
                    "lista_pedagios_total_simples": "Lista Pedágios (Simples)",
                    "km_total": "KM Total",
                    "tempo_total": "Tempo Total",
                    "qtd_total_pedagios": "Qtd. Total Pedágios",
                    "valor_pedagios_total": "Valor Total Pedágios",
                    "lista_pedagios_total": "Lista Total Pedágios",
                    "km_diff": "Diferença KM",
                    "tempo_diff": "Diferença Tempo",
                    "qtd_pedagio_diff": "Diferença Pedágios",
                    "tarifas_diff": "Diferença Tarifas",
                    "racional": "Racional",
                    "valor_excedente": "Valor Excedente"}
        )

        st.dataframe(df_fixos)
      else:

        st.info("Nenhuma consulta foi fixada ainda.")

