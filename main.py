import math
import os
from collections import ChainMap

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


def distance3D(x1, y1, z1, x2, y2, z2):
    d = 0.0
    d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
    return d


if __name__ == "__main__":
    # General description
    st.title("Scanner")
    st.text("Versión: 0.1.1")

    # Upload file
    uploaded_file = st.file_uploader("Sube el archivo csv", type=["csv"])

    if uploaded_file is not None:  # File > 0 bytes

        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
        st.write(file_details)
        df = pd.read_csv(uploaded_file)

        st.subheader("El archivo que subiste, primeras lineas")
        st.dataframe(df.head())

        result = df.groupby("DIA", as_index=False).agg({"X": ["mean"], "Y": ["mean"], "Z": ["mean"]})
        result.columns = ["_".join(col).strip() if col[1] else col[0] for col in result.columns.values]
        result.set_index("DIA", inplace=True)
        promedios = result
        graph3ddata = result
        result = result.diff()
        result.reset_index(inplace=True)
        result.iloc[0] = [1, 0, 0, 0]
        result.set_index("DIA", inplace=True)

        st.subheader("Variación")
        st.line_chart(result)

        st.subheader("Gráfico 3D")

        graph3ddata = graph3ddata - graph3ddata.iloc[0]

        x = graph3ddata["X_mean"]
        y = graph3ddata["Y_mean"]
        z = graph3ddata["Z_mean"]

        # Create an object for graph layout
        fig = go.Figure(
            data=go.Scatter3d(
                x=x,
                y=y,
                z=z,
                marker=dict(
                    size=4,
                    color=z,
                    colorscale="Viridis",
                ),
                line=dict(color="darkblue", width=2),
            )
        )

        fig.update_layout(
            width=800,
            height=700,
            autosize=False,
            scene=dict(xaxis_title="Eje X", yaxis_title="Eje Y", zaxis_title="Eje Z"),
            # margin=dict(r=20, b=10, l=10, t=10),
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Alpha, Beta")

        result2 = result
        result2["alpha"] = result2["X_mean"] / result["Y_mean"]
        result2["alpha"] = result2["alpha"].apply(lambda x: math.atan(x))
        result2["beta"] = result2["X_mean"] ** 2 + result["Z_mean"] ** 2
        result2["beta"] = result2["beta"].apply(lambda x: math.sqrt(x))
        result2["beta"] = result2["X_mean"] / result["beta"]
        result2["beta"] = result2["beta"].apply(lambda x: math.atan(x))
        result2["Azimut"] = result2["alpha"].apply(lambda x: x * 180 / math.pi)
        result2["Dip"] = result2["beta"].apply(lambda x: x * 180 / math.pi)
        result2.iloc[0] = [0, 0, 0, 0, 0, 0, 0]
        result2["X_mean_delta"] = result2["X_mean"]
        result2["Y_mean_delta"] = result2["Y_mean"]
        result2["Z_mean_delta"] = result2["Z_mean"]
        result2["X_mean"] = promedios["X_mean"]
        result2["Y_mean"] = promedios["Y_mean"]
        result2["Z_mean"] = promedios["Z_mean"]
        result2 = result2.reindex(columns=["X_mean", "Y_mean", "Z_mean", "X_mean_delta", "Y_mean_delta", "Z_mean_delta", "Azimut", "Dip"])

        st.dataframe(result2)
        csv = convert_df(result2)
        st.download_button(
            label="Descargar",
            data=csv,
            file_name="datos.csv",
            mime="text/csv",
        )
