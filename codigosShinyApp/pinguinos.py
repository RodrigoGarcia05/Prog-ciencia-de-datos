import matplotlib.pyplot as plt
import seaborn as sns
from shinyswatch import theme  
from shared import df
from shiny.express import input, render, ui


ui.page_opts(
    title="Datos sobre pingüinos | Rodri García", theme=theme.flatly
)

# --- TARJETAS SUPERIORES DE MÉTRICAS (KPIs) ---
with ui.layout_columns(col_widths={"sm": 6, "md": 3}):
  ui.value_box(title="Total de pingüinos analizados", value=f"{len(df):,}")
  ui.value_box(title="Especies únicas", value=f"{df['species'].nunique()}")
  ui.value_box(title="Islas de origen", value=f"{df['island'].nunique()}")
  ui.value_box(title="Registros de sexo", value=f"{df['sex'].dropna().nunique()}")


# --- BARRA LATERAL ---
with ui.sidebar():
  ui.input_select(
      "var",
      "Selecciona variable",
      choices=[
          "bill_length_mm",
          "body_mass_g",
          "flipper_length_mm",
          "bill_depth_mm",
      ],
  )
  ui.input_switch("species", "Group by species", value=True)
  ui.input_switch("show_rug", "Show Rug", value=False)
  ui.input_switch("island", "Group by island", value=False)


# --- TARJETA CON LA IMAGEN ---
with ui.card():
  ui.card_header("Datos curiosos de la especie")
  ui.tags.div(
      ui.img(src="pinguinos.jpeg", width="300px"),
      style="text-align: center; padding: 5px;",
  )
# --- TARJETA CON LA GRÁFICA ---
with ui.card():

  @render.plot
  def hist():
    hue = (
        "species" if input.species() else ("island" if input.island() else None)
    )

    plt.figure(facecolor="none")
    ax = plt.gca()
    ax.set_facecolor("none")

    ax.spines["bottom"].set_color("black")
    ax.spines["left"].set_color("black")
    ax.xaxis.label.set_color("black")
    ax.yaxis.label.set_color("black")
    ax.tick_params(axis="x", colors="black")
    ax.tick_params(axis="y", colors="black")

    sns.kdeplot(df, x=input.var(), hue=hue, fill=True, alpha=0.3)

    if input.show_rug():
      sns.rugplot(df, x=input.var(), hue=hue, color="black", alpha=0.5)

    ax.set_xlabel(
        input.var().replace("_", " ").title(), color="black", fontsize=12
    )
    ax.set_ylabel("Densidad", color="black", fontsize=12)
