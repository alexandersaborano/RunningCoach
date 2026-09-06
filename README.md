# Atleta AI Coach

Dashboard Streamlit para análise de sessões, histórico de treino, recuperação e
feedback adaptativo com providers de IA.

## Configuração local

Esta aplicação foi desenhada para utilização local. Copia `.env.example` para
`.env` e preenche os valores. O ficheiro `.env` está excluído do Git.

Os ficheiros da pasta `data/` contêm o perfil, histórico, recuperação, feedback
e análises AI. Permanecem no computador e não devem ser publicados no GitHub.

## Executar localmente

```powershell
pip install -r requirements.txt
streamlit run ui/app.py
```

## Backup dos dados

Executa regularmente:

```powershell
python backup_data.py
```

Por predefinição, o backup é criado em `backups/`, que também está excluída do
Git. Copia essa pasta para um disco privado ou armazenamento cloud privado.
Não guardes chaves API no backup.
