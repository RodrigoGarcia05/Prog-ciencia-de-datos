import matplotlib.pyplot as plt
import seaborn as sns
from shinyswatch import theme
from shared import df
from shiny import reactive
from shiny.express import input, render, ui

# --- Limpieza rápida de datos (espacios extra como "Empleado " o "Paparazzi ") ---
for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = df[col].str.strip()

AZUL = "#2C3E50"      # color principal del tema flatly
AZUL_CLARO = "#3498DB"
COLORES_GENERO = {"Hombre": AZUL, "Mujer": AZUL_CLARO}

# Indicadores clave (se calculan una sola vez)
gasto_h = df.loc[df["Género"] == "Hombre", "Total Gastado"].mean()
gasto_m = df.loc[df["Género"] == "Mujer", "Total Gastado"].mean()
pct_canje = (df["Canje Cupón"] == "Si").mean() * 100


def estilo_ejes(ax):
    """Aplica el mismo estilo limpio a todas las gráficas."""
    ax.set_facecolor("none")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(colors="black")


ui.page_opts(
    title=ui.div(
        ui.img(src="chevere logo.png", height="100px"),
        ui.span("ANALISIS | CHEVERE CERVEZA Y MUSICA", style="font-weight: 600; font-size: 16px;"),
        style="display: flex; align-items: center; gap: 12px;"
    ),
    theme=theme.flatly,
    fillable=True
)

# 1. Pestaña: Resumen General
with ui.nav_panel("Resumen General"):
    with ui.layout_sidebar():
        with ui.sidebar():
            ui.input_select(
                "var",
                "Selecciona variable",
                choices=["Edad", "Ingresos", "Máximo Gastar", "Total Gastado",
                         "Preferencia", "Ocasiones", "Frecuencia Visita", "Bar Favorito"],
            )
            # Un solo selector en lugar de dos switches que se contradicen
            ui.input_radio_buttons(
                "agrupar", "Agrupar por",
                choices=["Ninguno", "Género", "Preferencia"],
                selected="Ninguno",
            )
            ui.p("Encuesta realizada en línea, 01 al 31 de mayo de 2020.", class_="text-muted small")

        with ui.layout_columns(fill=False):
            ui.value_box(title="Personas encuestadas", value=f"{len(df):,}")
            ui.value_box(title="Canjearon su cupón", value=f"{pct_canje:.0f}%")
            ui.value_box(title="Gasto promedio (canje)", value=f"${df['Total Gastado'].mean():,.0f}")

        with ui.card():
            ui.card_header("Distribución de la Variable")

            @render.plot
            def hist():
                var_sel = input.var()
                hue = None if input.agrupar() == "Ninguno" else input.agrupar()
                if hue == var_sel:   # evitar agrupar una variable consigo misma
                    hue = None

                fig, ax = plt.subplots(figsize=(7, 3.5), facecolor="none")
                estilo_ejes(ax)

                if df[var_sel].dtype.kind in "if":
                    sns.histplot(data=df, x=var_sel, hue=hue, kde=True, alpha=0.5,
                                 color=AZUL, palette="Blues_d" if hue else None, ax=ax)
                else:
                    orden = df[var_sel].value_counts().index   # de mayor a menor
                    sns.countplot(data=df, x=var_sel, hue=hue or var_sel, order=orden,
                                  palette="Blues_d", legend=bool(hue), ax=ax)

                ax.set_xlabel(var_sel, color="black", fontsize=10)
                ax.set_ylabel("Frecuencia", color="black", fontsize=10)
                fig.tight_layout()
                return fig

# 2. Pestaña: Preferencias y Género
with ui.nav_panel("Preferencias y género"):
    with ui.layout_sidebar():
        with ui.sidebar():
            ui.h4("Filtros de preferencias")
            ui.input_select(
                "filtro_estado",
                "Estado Civil",
                choices=["Todos"] + sorted(df["Estado civil"].dropna().unique())
            )
            ui.input_select(
                "filtro_ocupacion",
                "Ocupación",
                choices=["Todos"] + sorted(df["Ocupación"].dropna().unique())
            )
            ui.input_select(
                "factor", "Factor a comparar",
                choices=["Preferencia", "Ocasiones", "Frecuencia Visita", "Bar Favorito"],
            )

        # Filtro compartido por la gráfica y la tabla (se calcula una sola vez)
        @reactive.calc
        def filtrar_pref():
            dff = df.copy()
            if input.filtro_estado() != "Todos":
                dff = dff[dff["Estado civil"] == input.filtro_estado()]
            if input.filtro_ocupacion() != "Todos":
                dff = dff[dff["Ocupación"] == input.filtro_ocupacion()]
            return dff

        with ui.card():
            ui.card_header("Comparativa por Género (% dentro de cada género)")

            @render.plot
            def plot_pref():
                dff = filtrar_pref()
                factor = input.factor()

                # Porcentaje dentro de cada género: hay más mujeres (152) que hombres (121),
                # así que comparar conteos crudos sería engañoso.
                tabla = (dff.groupby("Género")[factor]
                            .value_counts(normalize=True)
                            .mul(100).rename("Porcentaje").reset_index())

                fig, ax = plt.subplots(figsize=(7, 3.5), facecolor="none")
                estilo_ejes(ax)
                sns.barplot(data=tabla, x=factor, y="Porcentaje", hue="Género",
                            palette=COLORES_GENERO, ax=ax)
                for cont in ax.containers:
                    ax.bar_label(cont, fmt="%.0f%%", fontsize=8)
                ax.set_xlabel(factor, color="black", fontsize=10)
                ax.set_ylabel("% de clientes", color="black", fontsize=10)
                fig.tight_layout()
                return fig

        with ui.card():
            ui.card_header("Tabla resumen")

            @render.data_frame
            def tabla_pref():
                dff = filtrar_pref()
                factor = input.factor()
                tabla = (dff.groupby(factor)["Género"].value_counts()
                            .unstack(fill_value=0).reset_index())
                return render.DataGrid(tabla)

# 3. Pestaña: Análisis de Gasto
with ui.nav_panel("Análisis de gasto"):
    with ui.layout_sidebar():
        with ui.sidebar():
            ui.h4("Filtros de gasto")
            ui.input_select(
                "filtro_frecuencia",
                "Frecuencia de visita",
                choices=["Todos"] + sorted(df["Frecuencia Visita"].dropna().unique())
            )
            # "Total Gastado" solo existe para quienes canjearon el cupón (113 personas);
            # "Máximo Gastar" lo respondieron los 273 encuestados.
            ui.input_radio_buttons(
                "var_gasto", "Medida de gasto",
                choices={"Total Gastado": "Gasto real (con cupón)",
                         "Máximo Gastar": "Gasto máximo declarado"},
            )

        with ui.layout_columns(fill=False):
            ui.value_box(title="Gasto promedio hombres", value=f"${gasto_h:,.0f}")
            ui.value_box(title="Gasto promedio mujeres", value=f"${gasto_m:,.0f}")

        with ui.card():
            ui.card_header("¿Quién gasta más: Hombres o mujeres?")

            @render.plot
            def plot_gasto():
                dff = df.copy()
                if input.filtro_frecuencia() != "Todos":
                    dff = dff[dff["Frecuencia Visita"] == input.filtro_frecuencia()]
                var = input.var_gasto()
                dff = dff.dropna(subset=[var])

                fig, ax = plt.subplots(figsize=(7, 3.5), facecolor="none")
                estilo_ejes(ax)
                sns.boxplot(data=dff, x="Género", y=var, hue="Género",
                            palette=COLORES_GENERO, legend=False, ax=ax)

                # Marcar el promedio de cada grupo sobre la caja
                medias = dff.groupby("Género")[var].mean()
                for i, genero in enumerate([t.get_text() for t in ax.get_xticklabels()]):
                    if genero in medias:
                        ax.scatter(i, medias[genero], color="orange", zorder=3, s=40)
                        ax.annotate(f"Prom. ${medias[genero]:,.0f}", (i, medias[genero]),
                                    xytext=(10, 5), textcoords="offset points", fontsize=8)

                ax.set_xlabel("Género", color="black", fontsize=10)
                ax.set_ylabel(f"{var} ($)", color="black", fontsize=10)
                fig.tight_layout()
                return fig

        with ui.card():
            ui.card_header("Conclusión")
            ui.markdown(
                f"""
- Los hombres gastan más: en promedio ${gasto_h:,.0f} contra ${gasto_m:,.0f} de las mujeres
  (entre quienes canjearon su cupón). También declaran un gasto máximo mayor.
- Mujeres: valoran sobre todo la música y el lugar; el menú casi no les importa.
- Hombres: valoran el lugar y la música, pero el menú pesa mucho más que en las mujeres.
- Solo el {(df.loc[df['Género'] == 'Mujer', 'Canje Cupón'] == 'Si').mean() * 100:.0f}% de las mujeres canjeó el cupón
  (hombres: {(df.loc[df['Género'] == 'Hombre', 'Canje Cupón'] == 'Si').mean() * 100:.0f}%): hay una oportunidad de atraerlas con promociones ligadas a música y eventos.
"""
            )
