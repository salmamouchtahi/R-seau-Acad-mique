import streamlit as st
import networkx as nx
from pyvis.network import Network
import community as community_louvain
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image,TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import tempfile
from reseau_academique import ReseauAcademique
import matplotlib.pyplot as plt
from datetime import datetime
import math
# =========================
# INITIALISATION SESSION
# =========================

if "reseau" not in st.session_state:
    st.session_state.reseau = ReseauAcademique()

reseau = st.session_state.reseau

st.set_page_config(layout="wide")
st.title("Réseau Académique - Analyse de Graphe")


# =========================
# CONSTRUCTION NETWORKX
# =========================

def construire_nx():
    G = nx.Graph()
    for node in reseau.graphe:
        G.add_node(node)
    for n1 in reseau.graphe:
        for n2 in reseau.graphe[n1]:
            if not G.has_edge(n1, n2):
                G.add_edge(n1, n2)
    return G


# =========================
# STATISTIQUES
# =========================

def statistiques(G):
    n = G.number_of_nodes()
    e = G.number_of_edges()
    degres = dict(G.degree())
    deg_moyen = sum(degres.values()) / n if n > 0 else 0
    return n, e, deg_moyen


# =========================
# CENTRALITE SIMPLE
# =========================

def centralite_simple(G):
    if G.number_of_nodes() == 0:
        return {}
    centralites = nx.degree_centrality(G)
    return dict(sorted(centralites.items(), key=lambda x: x[1], reverse=True))


# =========================
# EXPORT PDF
# =========================


def exporter_pdf(reseau):

    file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    styles["Title"].fontSize = 22
    styles["Heading2"].fontSize = 16
    styles["Normal"].fontSize = 11

    elements = []

    # =========================
    # PAGE DE GARDE
    # =========================
    elements.append(Spacer(1, 60))
    elements.append(Paragraph("Analyse Structurelle d’un Réseau Académique", styles["Title"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Module : Structures de Données Avancées", styles["Normal"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 40))

    # =========================
    # STATISTIQUES GENERALES
    # =========================
    elements.append(Paragraph("Statistiques Générales", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    n = len(reseau.graphe)
    degres = reseau.degres_tous()
    total_aretes = sum(degres.values()) // 2
    deg_moyen = round(sum(degres.values()) / n, 2) if n > 0 else 0
    densite = round((2 * total_aretes) / (n * (n - 1)), 3) if n > 1 else 0

    data_stats = [
        ["Indicateur", "Valeur"],
        ["Nombre de chercheurs", n],
        ["Nombre de collaborations", total_aretes],
        ["Degré moyen", deg_moyen],
        ["Densité du graphe", densite],
    ]

    table_stats = Table(data_stats, colWidths=[350, 100])
    table_stats.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#dbe9f4")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))

    elements.append(table_stats)
    elements.append(Spacer(1, 30))

    # =========================
    # VISUALISATION DU GRAPHE 
    # =========================
    elements.append(Paragraph("Visualisation du graphe", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    chercheurs = list(reseau.graphe.keys())
    angle_step = 2 * math.pi / n if n > 0 else 0

    positions = {}
    for i, chercheur in enumerate(chercheurs):
        angle = i * angle_step
        x = math.cos(angle)
        y = math.sin(angle)
        positions[chercheur] = (x, y)

    plt.figure(figsize=(8, 8))

    # Dessiner arêtes
    for c1 in reseau.graphe:
        for c2 in reseau.graphe[c1]:
            if chercheurs.index(c1) < chercheurs.index(c2):
                x_values = [positions[c1][0], positions[c2][0]]
                y_values = [positions[c1][1], positions[c2][1]]
                plt.plot(x_values, y_values, alpha=0.4)

    # Dessiner sommets
    for chercheur in chercheurs:
        x, y = positions[chercheur]
        taille = 800 + 400 * reseau.degre(chercheur)
        plt.scatter(x, y, s=taille)
        plt.text(x, y, chercheur,
                 ha='center', va='center',
                 fontsize=9, weight='bold', color='white')

    plt.axis("off")

    tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    plt.savefig(tmp_img, bbox_inches="tight", dpi=300)
    plt.close()

    elements.append(Image(tmp_img, width=400, height=400))
    elements.append(Spacer(1, 30))

    # =========================
    # DEGRES DETAILLES
    # =========================
    elements.append(Paragraph("Degré de chaque chercheur", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    data_degres = [["Chercheur", "Degré"]]
    for chercheur, deg in sorted(degres.items(), key=lambda x: x[1], reverse=True):
        data_degres.append([chercheur, deg])

    table_degres = Table(data_degres, colWidths=[300, 100])
    table_degres.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e6f2ff")),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
    ]))

    elements.append(table_degres)
    elements.append(Spacer(1, 30))

    # =========================
    # COMPOSANTES CONNEXES
    # =========================
    elements.append(Paragraph("Composantes connexes", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    composantes = reseau.composantes_connexes()

    elements.append(
        Paragraph(f"Nombre total de composantes : {len(composantes)}", styles["Normal"])
    )
    elements.append(Spacer(1, 10))

    for i, comp in enumerate(composantes, start=1):
        elements.append(
            Paragraph(f"<b>Composante {i} :</b> {', '.join(sorted(comp))}",
                      styles["Normal"])
        )
        elements.append(Spacer(1, 5))

    elements.append(Spacer(1, 30))

    # =========================
    # CHERCHEURS ISOLES
    # =========================
    elements.append(Paragraph("Analyse des chercheurs isolés", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    isoles = [c for c, d in degres.items() if d == 0]

    if isoles:
        elements.append(
            Paragraph(f"Chercheurs isolés ({len(isoles)}) : {', '.join(isoles)}",
                      styles["Normal"])
        )
    else:
        elements.append(
            Paragraph("Aucun chercheur isolé.", styles["Normal"])
        )

    elements.append(Spacer(1, 30))

    # =========================
    # LISTE COMPLETE DES COLLABORATIONS
    # =========================
    elements.append(Paragraph("Liste complète des collaborations", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    for chercheur in chercheurs:
        voisins = sorted(reseau.graphe[chercheur])
        texte = f"<b>{chercheur}</b> → {', '.join(voisins) if voisins else 'Aucune collaboration'}"
        elements.append(Paragraph(texte, styles["Normal"]))
        elements.append(Spacer(1, 4))

    elements.append(Spacer(1, 30))

    # =========================
    # SUGGESTIONS
    # =========================
    elements.append(Paragraph("Suggestions de collaboration", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    for chercheur in chercheurs:
        suggestions = reseau.suggestion_collaborations(chercheur)
        texte = f"<b>{chercheur}</b> → {', '.join(suggestions) if suggestions else 'Aucune suggestion'}"
        elements.append(Paragraph(texte, styles["Normal"]))
        elements.append(Spacer(1, 4))

    # =========================
    # CONSTRUCTION PDF
    # =========================
    doc.build(elements)

    return file_path



# =========================
# VISUALISATION STABLE
# =========================

def afficher_pyvis(G):

    net = Network(
        height="600px",
        width="100%",
        bgcolor="#111111",
        font_color="white",
        directed=False
    )

    net.set_options("""
    var options = {
      "physics": { "enabled": false },
      "interaction": { "zoomView": false }
    }
    """)

    if len(G.nodes) > 0:
        partition = community_louvain.best_partition(G)
    else:
        partition = {}

    couleurs = [
        "#e63946", "#457b9d", "#2a9d8f",
        "#f4a261", "#9d4edd", "#ffb703",
        "#06d6a0", "#ef476f"
    ]

    centralites = centralite_simple(G)

    for node in G.nodes():
        community_id = partition.get(node, 0)
        color = couleurs[community_id % len(couleurs)]
        size = 20 + centralites.get(node, 0) * 40

        net.add_node(
            node,
            label=node,
            color=color,
            size=size
        )

    for edge in G.edges():
        net.add_edge(edge[0], edge[1])

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.save_graph(tmp_file.name)
    return tmp_file.name


# =========================
# SIDEBAR
# =========================

st.sidebar.header("Gestion du Réseau")

# Ajouter chercheur
st.sidebar.subheader("Ajouter un chercheur")
nom = st.sidebar.text_input("Nom du chercheur")

if st.sidebar.button("Ajouter chercheur"):
    if nom:
        try:
            reseau.ajouter_chercheur(nom)
            st.rerun()
        except Exception as e:
            st.sidebar.error(str(e))

# Supprimer chercheur
st.sidebar.subheader("Supprimer un chercheur")
if reseau.graphe:
    chercheur_suppr = st.sidebar.selectbox(
        "Choisir chercheur",
        list(reseau.graphe.keys())
    )
    if st.sidebar.button("Supprimer chercheur"):
        reseau.supprimer_chercheur(chercheur_suppr)
        st.rerun()

# Ajouter collaboration
st.sidebar.subheader("Ajouter collaboration")
chercheurs = list(reseau.graphe.keys())

if len(chercheurs) >= 2:
    c1 = st.sidebar.selectbox("Chercheur 1", chercheurs, key="a1")
    c2 = st.sidebar.selectbox("Chercheur 2", chercheurs, key="a2")

    if st.sidebar.button("Ajouter collaboration"):
        reseau.ajouter_collaboration(c1, c2)
        st.rerun()

# Supprimer collaboration
st.sidebar.subheader("Supprimer collaboration")

if len(chercheurs) >= 2:
    s1 = st.sidebar.selectbox("Chercheur A", chercheurs, key="s1")
    s2 = st.sidebar.selectbox("Chercheur B", chercheurs, key="s2")

    if st.sidebar.button("Supprimer collaboration"):
        reseau.supprimer_collaboration(s1, s2)
        st.rerun()


# =========================
# AFFICHAGE GRAPHE
# =========================

G = construire_nx()

if len(G.nodes) > 0:
    html_path = afficher_pyvis(G)
    with open(html_path, 'r', encoding='utf-8') as f:
        st.components.v1.html(f.read(), height=650)


# =========================
# STATISTIQUES
# =========================

st.subheader("Statistiques")

n, e, deg_moyen = statistiques(G)

col1, col2, col3 = st.columns(3)
col1.metric("Sommets", n)
col2.metric("Arêtes", e)
col3.metric("Degré Moyen", round(deg_moyen, 2))


# =========================
# CENTRALITE
# =========================

st.subheader("Centralité de degré")

centralites = centralite_simple(G)

for chercheur, valeur in centralites.items():
    st.write(f"{chercheur} → {round(valeur, 3)}")

if centralites:
    plus_central = max(centralites, key=centralites.get)
    st.success(f"Chercheur le plus central : {plus_central}")


# =========================
# COMPOSANTES
# =========================

if st.button("Afficher composantes connexes"):
    composantes = list(nx.connected_components(G))
    st.write(composantes)


# =========================
# SUGGESTIONS
# =========================

st.subheader("Suggestions de collaboration")

chercheur = st.text_input("Nom du chercheur")

if st.button("Obtenir suggestions"):
    try:
        st.write(reseau.suggestion_collaborations(chercheur))
    except Exception as e:
        st.error(str(e))


# =========================
# EXPORT
# =========================

if st.button("Exporter PDF"):
    pdf_path = exporter_pdf(reseau) 
    with open(pdf_path, "rb") as f:
        st.download_button(
            "Télécharger le rapport",
            f,
            file_name="rapport_reseau.pdf"
        )
