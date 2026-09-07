"""Tabela interativa com ações consistentes de filtro e exportação."""

from io import BytesIO
import json

import pandas as pd
import streamlit as st


def tabela_com_acoes(
    data: pd.DataFrame,
    *,
    key: str,
    file_stem: str,
    title: str | None = None,
) -> pd.DataFrame:
    """Renderiza uma tabela filtrável/ordenável e devolve as linhas visíveis."""
    if data.empty:
        st.info("Não existem dados para apresentar.")
        return data
    if title:
        st.subheader(title)

    working = data.copy()
    actions = st.columns([2, 1, 1, 2])
    with actions[0]:
        query = st.text_input("Filtrar tabela", key=f"{key}_query")
    with actions[1]:
        sort_column = st.selectbox(
            "Ordenar por",
            list(working.columns),
            key=f"{key}_sort",
        )
    with actions[2]:
        descending = st.checkbox("Descendente", key=f"{key}_descending")
    with actions[3]:
        columns = st.multiselect(
            "Colunas",
            list(working.columns),
            default=list(working.columns),
            key=f"{key}_columns",
        )

    if query:
        mask = working.astype(str).apply(
            lambda column: column.str.contains(query, case=False, na=False, regex=False)
        ).any(axis=1)
        working = working.loc[mask]
    if sort_column in working.columns:
        working = working.sort_values(sort_column, ascending=not descending, kind="stable")
    visible_columns = columns or list(working.columns)
    visible = working.loc[:, [column for column in visible_columns if column in working.columns]]
    st.dataframe(visible, width="stretch", hide_index=True)

    csv_bytes = visible.to_csv(index=False).encode("utf-8-sig")
    excel = BytesIO()
    visible.to_excel(excel, index=False, engine="openpyxl")
    downloads = st.columns(3)
    downloads[0].download_button(
        "⬇️ CSV",
        csv_bytes,
        f"{file_stem}.csv",
        "text/csv",
        key=f"{key}_csv",
    )
    downloads[1].download_button(
        "⬇️ Excel",
        excel.getvalue(),
        f"{file_stem}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"{key}_excel",
    )
    downloads[2].download_button(
        "⬇️ JSON",
        json.dumps(
            visible.where(pd.notna(visible), None).to_dict(orient="records"),
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8"),
        f"{file_stem}.json",
        "application/json",
        key=f"{key}_json",
    )
    return visible
