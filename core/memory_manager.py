import json
from datetime import datetime
from pathlib import Path
from config.settings import (
    ANALISES_GLOBAIS_DIR,
    FICHEIRO_MEMORIA,
    FICHEIRO_RECUPERACAO,
    HISTORICO_DIR,
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
                "historico_feedback": []
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
                return memoria
        except Exception as e:
            print(f"[ERRO MEMÓRIA] Erro ao carregar memória: {e}")
            return {
                "padroes_atleta": [],
                "regras_estilo": [],
                "historico_feedback": []
            }

    def guardar_memoria(self, dados: dict):
        """Guarda o dicionário de memória no ficheiro JSON."""
        self.caminho_ficheiro.parent.mkdir(parents=True, exist_ok=True)
        with open(self.caminho_ficheiro, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

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
        FICHEIRO_RECUPERACAO.parent.mkdir(parents=True, exist_ok=True)
        with open(FICHEIRO_RECUPERACAO, "w", encoding="utf-8") as ficheiro:
            json.dump(dados, ficheiro, indent=4, ensure_ascii=False)

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

    def guardar_analise_global(self, analise: dict):
        """Guarda uma análise global e todo o contexto usado para a produzir."""
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