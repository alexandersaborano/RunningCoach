import json
from datetime import datetime
from pathlib import Path
from config.settings import (
    ANALISES_GLOBAIS_DIR,
    FICHEIRO_MEMORIA,
    FICHEIRO_RECUPERACAO,
    HISTORICO_DIR,
)
from core.data_validation import (
    validate_global_analysis,
    validate_memory,
    validate_recovery,
    validate_session,
)


class MemoryManager:
    def __init__(self, caminho_ficheiro: Path = FICHEIRO_MEMORIA):
        self.caminho_ficheiro = caminho_ficheiro
        self._garantir_ficheiro_existe()

    def _garantir_ficheiro_existe(self):
        """Cria o ficheiro JSON de memória inicial caso ainda não exista."""
        if not self.caminho_ficheiro.exists():
            estrutura_inicial = {
                "padroes_atleta": [],
                "regras_estilo": [],
                "historico_feedback": [],
                "resumos_semanais_ai": [],
                "resultados_recomendacoes": [],
            }
            self.guardar_memoria(estrutura_inicial)

    def carregar_memoria(self) -> dict:
        """Carrega e devolve o conteúdo do ficheiro de memória do atleta."""
        try:
            with open(self.caminho_ficheiro, "r", encoding="utf-8") as f:
                memoria = json.load(f)
                if not isinstance(memoria, dict):
                    raise ValueError("A memória deve ser um objeto JSON.")

                # Migrate the original field names while keeping existing data.
                memoria["padroes_atleta"] = memoria.get(
                    "padroes_atleta", memoria.get("padroes_observados", [])
                )
                memoria["regras_estilo"] = memoria.get(
                    "regras_estilo", memoria.get("instrucoes_de_estilo", [])
                )
                memoria["historico_feedback"] = memoria.get("historico_feedback", [])
                memoria["resumos_semanais_ai"] = memoria.get("resumos_semanais_ai", [])
                memoria["resultados_recomendacoes"] = memoria.get("resultados_recomendacoes", [])
                antes = json.dumps(
                    (memoria.get("padroes_atleta_entradas"), memoria.get("regras_estilo_entradas")),
                    sort_keys=True,
                    ensure_ascii=False,
                )
                self._normalizar_entradas_memoria(memoria)
                self._sincronizar_listas_ativas(memoria)
                depois = json.dumps(
                    (memoria.get("padroes_atleta_entradas"), memoria.get("regras_estilo_entradas")),
                    sort_keys=True,
                    ensure_ascii=False,
                )
                if antes != depois:
                    self.guardar_memoria(memoria)
                return memoria
        except Exception as e:
            print(f"[ERRO MEMÓRIA] Erro ao carregar memória: {e}")
            return {
                "padroes_atleta": [],
                "regras_estilo": [],
                "historico_feedback": [],
                "resumos_semanais_ai": [],
                "resultados_recomendacoes": [],
            }

    @staticmethod
    def _normalizar_entradas_memoria(memoria):
        """Cria metadados sem substituir as listas antigas usadas pela UI."""
        agora = datetime.now().isoformat(timespec="seconds")
        for legacy, key in (("padroes_atleta", "padroes_atleta_entradas"),
                            ("regras_estilo", "regras_estilo_entradas")):
            valores = memoria.get(legacy, [])
            if not isinstance(valores, list):
                valores = []
            existentes = memoria.get(key, [])
            if not isinstance(existentes, list):
                existentes = []
            textos = {str(e.get("conteudo", e.get("texto", ""))) for e in existentes if isinstance(e, dict)}
            for valor in valores:
                texto = valor if isinstance(valor, str) else str(valor)
                if texto and texto not in textos:
                    existentes.append({"conteudo": valor, "criado_em": agora,
                                       "expira_em": None, "ativo": True, "origem": "legado"})
                    textos.add(texto)
            memoria[key] = existentes
        return memoria

    @staticmethod
    def _sincronizar_listas_ativas(memoria):
        """Mantém as listas legadas usadas pelos prompts alinhadas com o estado."""
        for legacy, key in (("padroes_atleta", "padroes_atleta_entradas"),
                            ("regras_estilo", "regras_estilo_entradas")):
            entradas = memoria.get(key, [])
            memoria[legacy] = [
                entrada.get("conteudo", entrada.get("texto", ""))
                for entrada in entradas
                if isinstance(entrada, dict) and entrada.get("ativo", True)
            ]
        return memoria

    def guardar_memoria(self, dados: dict):
        """Guarda o dicionário de memória no ficheiro JSON."""
        dados = validate_memory(dados)
        self.caminho_ficheiro.parent.mkdir(parents=True, exist_ok=True)
        with open(self.caminho_ficheiro, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

    def guardar_resumo_semanal(self, resumo: dict):
        memoria = self.carregar_memoria()
        chave = resumo.get("semana_inicio")
        items = [item for item in memoria.get("resumos_semanais_ai", [])
                 if item.get("semana_inicio") != chave]
        items.append(resumo)
        memoria["resumos_semanais_ai"] = items
        self.guardar_memoria(memoria)

    def carregar_resumos_semanais(self) -> list:
        return self.carregar_memoria().get("resumos_semanais_ai", [])

    def guardar_resultado_recomendacao(self, resultado: dict):
        memoria = self.carregar_memoria()
        memoria.setdefault("resultados_recomendacoes", []).append(resultado)
        self.guardar_memoria(memoria)

    def carregar_resultados_recomendacoes(self) -> list:
        return self.carregar_memoria().get("resultados_recomendacoes", [])

    # aliases explícitos para consumidores que distinguem artefactos AI
    guardar_resumo_semanal_ai = guardar_resumo_semanal
    carregar_resumos_semanais_ai = carregar_resumos_semanais
    guardar_outcome_recomendacao = guardar_resultado_recomendacao
    carregar_outcomes_recomendacoes = carregar_resultados_recomendacoes

    def carregar_recuperacao(self, data: str = None) -> dict:
        """Carrega os dados de recuperação guardados para uma data."""
        if not FICHEIRO_RECUPERACAO.exists():
            return {}
        try:
            with open(FICHEIRO_RECUPERACAO, "r", encoding="utf-8") as ficheiro:
                dados = json.load(ficheiro)
            return dados.get(data, {}) if isinstance(dados, dict) and data else dados
        except (OSError, json.JSONDecodeError) as e:
            print(f"[ERRO RECUPERAÇÃO] Erro ao carregar dados: {e}")
            return {}

    def guardar_recuperacao(
        self,
        data: str,
        sono_horas: float,
        recuperacao: int,
        fc_repouso: int,
    ):
        """Guarda ou atualiza sono, recuperação percebida e FC de repouso."""
        dados = self.carregar_recuperacao()
        dados[data] = {
            "data": data,
            "sono_horas": sono_horas,
            "recuperacao": recuperacao,
            "fc_repouso": fc_repouso,
        }
        validate_recovery(dados)
        FICHEIRO_RECUPERACAO.parent.mkdir(parents=True, exist_ok=True)
        with open(FICHEIRO_RECUPERACAO, "w", encoding="utf-8") as ficheiro:
            json.dump(dados, ficheiro, indent=4, ensure_ascii=False)

    def sincronizar_bem_estar(self, registos: list[dict]) -> int:
        """Mescla wellness remoto, substituindo os valores da mesma data."""
        from core.data_validation import validate_wellness_records

        registos = validate_wellness_records(registos)
        dados = self.carregar_recuperacao()
        sincronizado_em = datetime.now().isoformat(timespec="seconds")
        guardados = 0
        for remoto in registos:
            data = str(remoto["data"])[:10]
            anterior = dict(remoto)
            anterior["data"] = data
            anterior["origem"] = "intervals_icu"
            anterior["sincronizado_em"] = sincronizado_em
            dados[data] = anterior
            guardados += 1
        if guardados:
            validate_recovery(dados)
            FICHEIRO_RECUPERACAO.parent.mkdir(parents=True, exist_ok=True)
            with open(FICHEIRO_RECUPERACAO, "w", encoding="utf-8") as ficheiro:
                json.dump(dados, ficheiro, indent=4, ensure_ascii=False)
        return guardados

    merge_wellness = sincronizar_bem_estar
    sincronizar_wellness = sincronizar_bem_estar
    mesclar_bem_estar = sincronizar_bem_estar

    def adicionar_padrao(self, novo_padrao: str):
        """Adiciona um novo padrão fisiológico/pessoal identificado à memória."""
        memoria = self.carregar_memoria()
        padroes = memoria.get("padroes_atleta", [])
        
        if novo_padrao and novo_padrao not in padroes:
            padroes.append(novo_padrao)
            memoria["padroes_atleta"] = padroes
            self.guardar_memoria(memoria)

    def adicionar_regra(self, nova_regra: str):
        """Adiciona uma nova regra de análise/estilo à memória."""
        memoria = self.carregar_memoria()
        regras = memoria.get("regras_estilo", [])
        
        if nova_regra and nova_regra not in regras:
            regras.append(nova_regra)
            memoria["regras_estilo"] = regras
            self.guardar_memoria(memoria)

    def listar_memorias_geriveis(self) -> list[dict]:
        """Lista padrões e regras com estado de ativação e identificador estável."""
        memoria = self.carregar_memoria()
        resultado = []
        for categoria, chave in (
            ("Padrão do atleta", "padroes_atleta_entradas"),
            ("Regra de análise", "regras_estilo_entradas"),
        ):
            for indice, entrada in enumerate(memoria.get(chave, [])):
                if isinstance(entrada, dict):
                    texto = entrada.get("conteudo", entrada.get("texto", ""))
                    ativo = entrada.get("ativo", True)
                else:
                    texto = str(entrada)
                    ativo = True
                resultado.append({
                    "id": f"{chave}:{indice}",
                    "categoria": categoria,
                    "texto": texto,
                    "ativo": bool(ativo),
                    "origem": entrada.get("origem", "manual") if isinstance(entrada, dict) else "legado",
                })
        return resultado

    def atualizar_memoria_gerivel(self, memoria_id: str, *, ativo: bool | None = None, remover: bool = False):
        """Ativa, desativa ou remove uma memória sem alterar o feedback histórico."""
        chave, separador, indice_texto = memoria_id.partition(":")
        if not separador or chave not in {"padroes_atleta_entradas", "regras_estilo_entradas"}:
            raise ValueError("Identificador de memória inválido.")
        try:
            indice = int(indice_texto)
        except ValueError as exc:
            raise ValueError("Índice de memória inválido.") from exc
        memoria = self.carregar_memoria()
        entradas = memoria.get(chave, [])
        if indice < 0 or indice >= len(entradas):
            raise ValueError("Memória não encontrada.")
        entrada_original = entradas[indice]
        if remover:
            entradas.pop(indice)
            texto_removido = (
                entrada_original.get("conteudo", entrada_original.get("texto", ""))
                if isinstance(entrada_original, dict)
                else str(entrada_original)
            )
            legacy = "padroes_atleta" if chave == "padroes_atleta_entradas" else "regras_estilo"
            memoria[legacy] = [
                valor for valor in memoria.get(legacy, [])
                if str(valor) != str(texto_removido)
            ]
        else:
            entrada = entradas[indice]
            if not isinstance(entrada, dict):
                entrada = {
                    "conteudo": str(entrada),
                    "criado_em": datetime.now().isoformat(timespec="seconds"),
                    "expira_em": None,
                    "origem": "legado",
                }
                entradas[indice] = entrada
            if ativo is not None:
                entrada["ativo"] = bool(ativo)
        memoria[chave] = entradas
        self._sincronizar_listas_ativas(memoria)
        self.guardar_memoria(memoria)

    def adicionar_feedback(
        self,
        feedback: str,
        novo_padrao: str = None,
        nova_regra: str = None,
    ):
        """Guarda cada feedback submetido, mesmo quando não gera memória nova."""
        memoria = self.carregar_memoria()
        historico = memoria.get("historico_feedback", [])
        historico.append({
            "data": datetime.now().isoformat(timespec="seconds"),
            "feedback": feedback,
            "novo_padrao": novo_padrao,
            "nova_regra": nova_regra,
        })
        memoria["historico_feedback"] = historico
        self.guardar_memoria(memoria)

    def guardar_sessao(self, sessao: dict):
        """Guarda ou atualiza uma sessão analisada no histórico local."""
        sessao = validate_session(sessao)
        atividade_id = str(sessao.get("atividade_id", "")).strip()
        if not atividade_id:
            raise ValueError("A sessão precisa de um atividade_id.")
        HISTORICO_DIR.mkdir(parents=True, exist_ok=True)
        caminho = HISTORICO_DIR / f"{atividade_id}.json"
        with open(caminho, "w", encoding="utf-8") as ficheiro:
            json.dump(sessao, ficheiro, indent=4, ensure_ascii=False)

    def carregar_historico_sessoes(self) -> list:
        """Carrega todas as sessões guardadas, ignorando ficheiros inválidos."""
        sessoes = []
        if not HISTORICO_DIR.exists():
            return sessoes
        for caminho in HISTORICO_DIR.glob("*.json"):
            try:
                with open(caminho, "r", encoding="utf-8") as ficheiro:
                    sessao = json.load(ficheiro)
                if isinstance(sessao, dict) and sessao.get("atividade_id"):
                    sessoes.append(sessao)
            except (OSError, json.JSONDecodeError) as e:
                print(f"[ERRO HISTÓRICO] Erro ao ler {caminho.name}: {e}")
        return sorted(sessoes, key=lambda item: item.get("data", ""))

    def guardar_sessoes_importadas(self, sessoes: list) -> int:
        """Guarda atividades importadas sem substituir análises já existentes."""
        guardadas = 0
        existentes = {
            str(sessao.get("atividade_id"))
            for sessao in self.carregar_historico_sessoes()
        }
        for sessao in sessoes:
            atividade_id = str(sessao.get("atividade_id", "")).strip()
            if atividade_id and atividade_id not in existentes:
                self.guardar_sessao(sessao)
                existentes.add(atividade_id)
                guardadas += 1
        return guardadas

    def ids_sessoes_existentes(self) -> set[str]:
        """Devolve os identificadores já importados para pré-filtrar resultados."""
        return {
            str(sessao.get("atividade_id")).strip()
            for sessao in self.carregar_historico_sessoes()
            if str(sessao.get("atividade_id", "")).strip()
        }

    def guardar_analise_global(self, analise: dict):
        """Guarda uma análise global e todo o contexto usado para a produzir."""
        analise = validate_global_analysis(analise)
        data = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        ANALISES_GLOBAIS_DIR.mkdir(parents=True, exist_ok=True)
        caminho = ANALISES_GLOBAIS_DIR / f"analise_{data}.json"
        with open(caminho, "w", encoding="utf-8") as ficheiro:
            json.dump(analise, ficheiro, indent=4, ensure_ascii=False)
        return caminho

    def carregar_analises_globais(self) -> list:
        """Carrega análises globais anteriores para consulta e referência."""
        analises = []
        if not ANALISES_GLOBAIS_DIR.exists():
            return analises
        for caminho in sorted(ANALISES_GLOBAIS_DIR.glob("*.json")):
            try:
                with open(caminho, "r", encoding="utf-8") as ficheiro:
                    analise = json.load(ficheiro)
                if isinstance(analise, dict):
                    analises.append(analise)
            except (OSError, json.JSONDecodeError) as e:
                print(f"[ERRO ANÁLISE] Erro ao ler {caminho.name}: {e}")
        return analises

    def listar_analises_globais(self) -> list:
        """Lista análises globais com o nome do ficheiro e os seus dados."""
        resultados = []
        if not ANALISES_GLOBAIS_DIR.exists():
            return resultados
        for caminho in sorted(ANALISES_GLOBAIS_DIR.glob("*.json"), reverse=True):
            try:
                with caminho.open("r", encoding="utf-8") as ficheiro:
                    dados = json.load(ficheiro)
                if isinstance(dados, dict):
                    resultados.append({"ficheiro": caminho.name, "dados": dados})
            except (OSError, json.JSONDecodeError) as error:
                print(f"[ERRO ANÁLISE] Erro ao ler {caminho.name}: {error}")
        return resultados