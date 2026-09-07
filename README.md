# Atleta AI Coach

Dashboard Streamlit para análise de sessões, histórico de treino, recuperação e
feedback adaptativo com providers de IA.

## Configuração local

Esta aplicação foi desenhada para utilização local. Copia `.env.example` para
`.env` e preenche os valores. O ficheiro `.env` está excluído do Git.

Os ficheiros da pasta `data/` contêm o perfil, histórico, recuperação, feedback
e análises AI. Permanecem no computador e não devem ser publicados no GitHub.

### Zonas de frequência cardíaca

O perfil sincronizado usa `GET /api/v1/athlete/{athlete_id}` do Intervals.icu.
`icu_max_hr`, `icu_lthr` e `icu_resting_hr` são métricas globais em bpm.
As zonas de corrida podem vir de `sportSettings.hr_zones`, acompanhadas por
`hr_zone_names` e `hr_load_type`. A app preserva a origem e o método e não
assume que essas zonas são calculadas por `%HRR`; as zonas Karvonen são
apresentadas separadamente.

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

## Qualidade, manutenção e recuperação

Para instalar e iniciar a aplicação com um único comando:

```powershell
.\run_local.ps1
```

O script cria o ambiente virtual se necessário, instala as dependências,
cria `.env` a partir de `.env.example` quando ainda não existir e inicia o
Streamlit.

Antes de alterações importantes, cria um backup. Para recuperar dados:

1. Abre a página **Configurações**.
2. Confirma a integridade dos ficheiros JSON.
3. Cria um backup dos dados atuais.
4. Seleciona um backup válido e confirma o restauro.
5. Reinicia a aplicação e volta a verificar a integridade.

Se um ficheiro JSON estiver corrompido, não o edites por tentativa. Preserva
primeiro uma cópia da pasta `data/`, verifica um backup anterior e restaura-o
pela interface. Os logs locais são opcionais e não devem conter credenciais.
