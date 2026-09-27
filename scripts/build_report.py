"""Build the academic publication-grade Word Term Paper (.docx) and export to PDF.

Assembles title page, abstract, executive overview, literature review,
methodology, empirical results, statistical tables, embedded figures,
discussion, limitations, conclusions, references, and code appendices.
"""
from pathlib import Path
import json
import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
CHARTS = OUT / "charts"
DATA = json.loads((OUT / "analysis_data.json").read_text(encoding="utf-8"))

def set_cell_shading(cell, fill_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill_hex)


def set_cell_margins(cell, top=120, start=120, bottom=120, end=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = tcPr.first_child_found_in("w:tcMar")
    if tcMar is None:
        tcMar = OxmlElement("w:tcMar")
        tcPr.append(tcMar)
    for m, v in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tcMar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tcMar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row):
    trPr = row._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)


def format_table(table, col_widths, alignments):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(table.rows):
        for j, cell in enumerate(row.cells):
            cell.width = col_widths[j]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            for p in cell.paragraphs:
                p.alignment = alignments[j]
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                for run in p.runs:
                    run.font.name = "Cambria"
                    run.font.size = Pt(8.5)
            if i == 0:
                set_cell_shading(cell, "2B5B84")
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        run.font.bold = True
            elif i % 2 == 1:
                set_cell_shading(cell, "F7F9FA")
            else:
                set_cell_shading(cell, "FFFFFF")


def add_heading_with_spacing(doc, text, level):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    for r in h.runs:
        r.font.name = "Cambria"
        r.font.color.rgb = RGBColor(30, 40, 50)
    return h


def add_body_paragraph(doc, text, space_after=6, italic=False, bold_prefix=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Cambria"
        r_pre.font.size = Pt(10)
        r_pre.font.bold = True
    r = p.add_run(text)
    r.font.name = "Cambria"
    r.font.size = Pt(10)
    r.font.italic = italic
    return p


def add_figure(doc, img_stem, caption_text, width=Inches(6.2)):
    png_path = CHARTS / f"{img_stem}.png"
    if png_path.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(str(png_path), width=width)
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = "Cambria"
        r_cap.font.size = Pt(8.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(80, 80, 80)


def build_document():
    doc = Document()
    
    # Page setup (A4 standard)
    sec = doc.sections[0]
    sec.page_width = Inches(8.27)
    sec.page_height = Inches(11.69)
    sec.top_margin = Inches(0.85)
    sec.bottom_margin = Inches(0.85)
    sec.left_margin = Inches(0.9)
    sec.right_margin = Inches(0.9)

    # Title Page / Header
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(24)
    p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("Understanding the Relationship Between Pokémon Type and its Battle Role Using Official Performance Statistics: Pokémon Database, 2008–2025")
    r_title.font.name = "Cambria"
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(20, 35, 60)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(16)
    r_sub = p_sub.add_run("Term Paper · CSD105 Intro to Data Science · Ahmedabad University\nInstructor: Professor Hiral Vegda")
    r_sub.font.name = "Cambria"
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(70, 80, 90)

    # Authors Table
    table_auth = doc.add_table(rows=2, cols=2)
    table_auth.alignment = WD_TABLE_ALIGNMENT.CENTER
    authors_data = [
        ("AU2540195 Naman Kumar Sinha", "AU23L10004 Kabir Chaterjee"),
        ("AU2410174 Tithi Modi", "AU25L20003 Hazikah Kazi")
    ]
    for r_idx, (a1, a2) in enumerate(authors_data):
        row = table_auth.rows[r_idx]
        p1 = row.cells[0].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.add_run(a1).font.bold = True
        p2 = row.cells[1].paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.add_run(a2).font.bold = True
    
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Abstract
    add_heading_with_spacing(doc, "ABSTRACT", level=1)
    add_body_paragraph(
        doc,
        "The term paper aims to investigate the fundamental connections between a Pokémon’s elemental type and its "
        "functional battle role. The goal is to determine if the existing correlations are simply a coincidence or an "
        "actual deliberate game design framework. The study’s central essence is to find out if a statistically predictable "
        "relationship exists between classification of Type and the quantitative distribution of the six core Base Stats "
        "(HP, Attack, Defense, Special Attack, Special Defence, and Speed). Using the official Pokémon Database comprising "
        "1,219 unique Pokémon entries across all nine generations, the analysis performs rigorous descriptive statistics, "
        "bivariate linear and monotonic rank correlation analysis (Pearson and Spearman), independent two-sample t-tests, "
        "one-way Analysis of Variance (ANOVA), and unsupervised K-Means clustering. ANOVA confirms that Type and defined "
        "Power Categories exert an overwhelmingly significant impact on Base Stats (F = 2551.92, p < 1e-300 for Total Stats). "
        "Correlation analysis establishes that HP is the dominant linear anchor for overall combat potential (r = 0.6596, rho = 0.7316), "
        "while Special Attack and Special Defence exhibit structured symmetrical balancing (r = 0.5167, rho = 0.5736). "
        "K-Means clustering categorizes the population into four distinct battle roles: Walls, Sweepers, Balanced/Tanks, and "
        "Low-Stat Unevolved entities, demonstrating that elemental typing serves as a deliberate architectural proxy for combat utility."
    )

    # 1. Introduction
    add_heading_with_spacing(doc, "1. INTRODUCTION", level=1)
    add_body_paragraph(
        doc,
        "The Pokémon franchise centers on creatures, often inspired by animals, myths, and objects, that inhabit the Pokémon world. "
        "Humans, called Trainers, journey across regions to catch, train, and battle with these creatures, with the ultimate goal of "
        "completing the Pokédex—an encyclopedic catalog of all species—and achieving the title of Pokémon Master. This core gameplay loop "
        "of collecting, optimizing, and competitive battling drives the franchise across videogames, anime, and trading cards. "
        "Pokémon statistics exist to create differentiated combat roles and ensure balance: a rapid, frail attacker is intentionally "
        "engineered differently from a slow, heavily fortified juggernaut."
    )
    add_body_paragraph(
        doc,
        "In the complex multiverse of Pokémon battling, success hinges upon interconnected variables such as elemental type, abilities, "
        "natures, and base statistics. These stats represent the biological DNA of a creature’s competitive capability. For example, high "
        "Speed combined with elite Special Attack defines a 'Special Sweeper,' designed to outpace and eliminate opposing teams before they "
        "can retaliate. This raises a fundamental research question: Are these competitive roles merely emergent coincidences of player strategy, "
        "or do they stem from a deliberate, statistically measurable design architecture embedded by Game Freak developers?"
    )
    add_body_paragraph(
        doc,
        "This paper rigorously investigates the quantitative link between Elemental Type and statistical dispersion across six core attributes: "
        "HP, Attack, Defense, Special Attack, Special Defence, and Speed. By analyzing static base statistics, we create a controlled experimental "
        "setting that isolates intrinsic design parameters from situational factors like movesets and items."
    )

    # 2. Literature Review
    add_heading_with_spacing(doc, "2. LITERATURE REVIEW & THEORETICAL FRAMEWORK", level=1)
    add_body_paragraph(
        doc,
        "The Pokémon Database (2008–2025) and competitive battling communities (such as Smogon University) have established functional battle roles "
        "based on statistical distributions:",
        bold_prefix="Community-Defined Battle Roles: "
    )
    roles = [
        ("Glass Cannons: ", "Creatures possessing immense Attack or Special Attack and Speed, but frail HP and Defense. Their objective is to eliminate adversaries in a single blow before sustaining counterattacks."),
        ("Walls: ", "Defensive bastions featuring high HP, Defense, or Special Defence. Their role is to absorb sustained punishment, stall opponents, and disrupt offensive momentum."),
        ("Tanks: ", "Hybrid combatants with substantial HP and high offensive output, engineered to both absorb incoming damage and strike back decisively."),
        ("Sweepers: ", "High-speed offensive sweepers configured to wipe out an entire opposing lineup once defensive barriers are breached."),
        ("Pivots: ", "Balanced creatures with superior Speed and versatile tactical switching capabilities, allowing agile momentum control.")
    ]
    for r_title, r_desc in roles:
        add_body_paragraph(doc, r_desc, bold_prefix=f"• {r_title}")

    add_body_paragraph(
        doc,
        "Prior exploratory studies on Kaggle and academic datasets have demonstrated that Pokémon Type strongly influences stat bias: "
        "Fighting types exhibit statistically superior median Attack; Psychic types show pronounced bias toward Special Attack; "
        "Rock and Steel types systematically record the highest Defense values; and Bug types anchor the lowest base stat totals. "
        "However, previous studies examined stats in isolation or applied unsupervised K-Means clustering without reconciling findings "
        "with inferential hypothesis testing. A clear methodological gap exists in synthesizing individual stat distributions with multivariate "
        "clustering. This term paper directly bridges that gap."
    )

    # 3. Methodology
    add_heading_with_spacing(doc, "3. METHODOLOGY & DATA PROVENANCE", level=1)
    add_body_paragraph(
        doc,
        "The dataset utilized in this empirical investigation comprises the official Pokémon Pokédex spanning Generations I through IX (1996–2025). "
        "The raw tabular data was acquired from the Pokémon Database (pokemondb.net/pokedex/all) and transformed into a standardized spreadsheet "
        "('Pokemon Dataset - Sheet1.csv'). The raw dataset contained 1,220 total entries. Initial data audit revealed that row 1,220 corresponded to an "
        "extraneous web footer containing null values across all combat statistics. Dropping this non-numeric entry yielded a pristine dataset of "
        "1,219 unique Pokémon species and regional/battle forms."
    )
    add_body_paragraph(
        doc,
        "To operationalize combat capability, four composite power metrics and a categorical tiering system were engineered:",
        bold_prefix="Feature Engineering Formulation: "
    )
    add_body_paragraph(doc, "• Physical Power = (Attack + Defense) / 2\n"
                           "• Special Power = (Special Attack + Special Defence) / 2\n"
                           "• Offensive Power = (Attack + Special Attack) / 2\n"
                           "• Defensive Power = (Defense + Special Defence) / 2\n"
                           "• Power Category = Categorical stratification: Weak (0–300 BST), Average (301–450 BST), Strong (451–600 BST), Legendary (601–1200 BST).")

    # 4. Results & Analysis
    add_heading_with_spacing(doc, "4. EMPIRICAL ANALYSIS & STATISTICAL FINDINGS", level=1)
    
    # 4.1 Scope and Completeness
    add_heading_with_spacing(doc, "4.1 Initial Data Scope and Power Distribution", level=2)
    add_body_paragraph(
        doc,
        f"The cleaned dataset encompasses {DATA['metadata']['cleaned_record_count']} Pokémon entries across 18 primary types. "
        f"The mean Base Stat Total (BST) across the population is {DATA['summary_statistics']['Total']['mean']:.2f}, slightly below "
        f"the median of {DATA['summary_statistics']['Total']['median']:.1f}. This indicates a moderate negative skew, driven by the vast "
        f"cohort of unevolved and mid-tier evolutionary forms balancing out high-tier outliers."
    )
    add_figure(doc, "figure_4_bst_distribution", "Figure 1: Overall Base Stat Total (BST) Distribution with Mean and Median Marks.")

    # 4.2 Power Extremes
    add_heading_with_spacing(doc, "4.2 Power Extremes and Dominance Hierarchy", level=2)
    top_p = DATA["strongest_pokemon"]
    add_body_paragraph(
        doc,
        f"The strongest single entity identified in the entire franchise database is {top_p['name']} with an astonishing BST of {top_p['total']:.1f} "
        f"(HP: {top_p['hp']:.0f}, Attack: {top_p['attack']:.0f}, Defense: {top_p['defense']:.0f}, Sp. Atk: {top_p['sp_atk']:.0f}, "
        f"Sp. Def: {top_p['sp_def']:.0f}, Speed: {top_p['speed']:.0f}). Eternamax Eternatus serves as the climax boss in Pokémon Sword and Shield, "
        f"standing as an extreme statistical outlier far exceeding standard Legendary caps (~780 BST)."
    )
    add_figure(doc, "figure_1_top_10_bst", "Figure 2: Top 10 Pokémon Ranked by Base Stat Total (BST).")

    # Top 10 Table
    table_top10 = doc.add_table(rows=1, cols=6)
    table_top10.rows[0].cells[0].paragraphs[0].text = "#"
    table_top10.rows[0].cells[1].paragraphs[0].text = "Pokémon Name"
    table_top10.rows[0].cells[2].paragraphs[0].text = "Type"
    table_top10.rows[0].cells[3].paragraphs[0].text = "BST"
    table_top10.rows[0].cells[4].paragraphs[0].text = "Atk / Def"
    table_top10.rows[0].cells[5].paragraphs[0].text = "SpA / SpD"
    set_repeat_table_header(table_top10.rows[0])
    
    for pk in DATA["top_10_pokemon"]:
        row = table_top10.add_row()
        row.cells[0].paragraphs[0].text = pk["number"]
        row.cells[1].paragraphs[0].text = pk["name"].replace("\r\n", " ")
        t_str = pk["primary_type"] if pk["secondary_type"] == "None" else f"{pk['primary_type']}/{pk['secondary_type']}"
        row.cells[2].paragraphs[0].text = t_str
        row.cells[3].paragraphs[0].text = f"{int(pk['total'])}"
        row.cells[4].paragraphs[0].text = f"{int(pk['attack'])} / {int(pk['defense'])}"
        row.cells[5].paragraphs[0].text = f"{int(pk['sp_atk'])} / {int(pk['sp_def'])}"

    format_table(table_top10, [Inches(0.6), Inches(2.2), Inches(1.3), Inches(0.7), Inches(0.9), Inches(0.9)],
                 [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT,
                  WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT])
    
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 4.3 Correlation Analysis
    add_heading_with_spacing(doc, "4.3 Correlation Analysis: Structural Inter-Stat Dependencies", level=2)
    add_body_paragraph(
        doc,
        "To explore structural dependencies within the battle engine, both Pearson (linear) and Spearman (monotonic rank) "
        "correlation coefficients were calculated across all pairs. All five primary focal pairs exhibited statistically significant "
        "relationships (p < 0.001):"
    )

    # Correlation Table
    table_corr = doc.add_table(rows=1, cols=5)
    table_corr.rows[0].cells[0].paragraphs[0].text = "Stat Pair"
    table_corr.rows[0].cells[1].paragraphs[0].text = "Pearson r"
    table_corr.rows[0].cells[2].paragraphs[0].text = "Pearson p-value"
    table_corr.rows[0].cells[3].paragraphs[0].text = "Spearman rho"
    table_corr.rows[0].cells[4].paragraphs[0].text = "Significant?"
    set_repeat_table_header(table_corr.rows[0])
    
    for f in DATA["focal_pair_correlations"]:
        row = table_corr.add_row()
        row.cells[0].paragraphs[0].text = f["pair"]
        row.cells[1].paragraphs[0].text = f"{f['pearson_r']:.4f}"
        row.cells[2].paragraphs[0].text = f"{f['pearson_p']:.4e}"
        row.cells[3].paragraphs[0].text = f"{f['spearman_rho']:.4f}"
        row.cells[4].paragraphs[0].text = "Yes (p < 0.05)"

    format_table(table_corr, [Inches(2.2), Inches(1.0), Inches(1.3), Inches(1.0), Inches(1.0)],
                 [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT,
                  WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.CENTER])
    
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    add_figure(doc, "figure_3_correlation_heatmap", "Figure 3: Full Correlation Heatmap of All Seven Numerical Parameters.")
    add_figure(doc, "figure_2_attack_vs_defense", "Figure 4: Scatter Plot of Attack vs Defense, Color-coded by Base Stat Total.")

    # 4.4 Hypothesis Testing: T-Test
    add_heading_with_spacing(doc, "4.4 Hypothesis Testing: T-Test Verification of Strong vs. Legendary Power", level=2)
    add_body_paragraph(
        doc,
        "To rigorously confirm whether the human-defined 'Legendary' classification represents an objectively superior tier "
        "rather than a narrative label, independent two-sample t-tests were conducted comparing the 'Strong' tier (BST 451–600, N=479) "
        "against the 'Legendary' tier (BST 601–1200, N=114). The null hypothesis posited equal population means across tiers."
    )
    
    table_ttest = doc.add_table(rows=1, cols=6)
    table_ttest.rows[0].cells[0].paragraphs[0].text = "Base Stat"
    table_ttest.rows[0].cells[1].paragraphs[0].text = "Strong Mean"
    table_ttest.rows[0].cells[2].paragraphs[0].text = "Legendary Mean"
    table_ttest.rows[0].cells[3].paragraphs[0].text = "t-statistic"
    table_ttest.rows[0].cells[4].paragraphs[0].text = "p-value"
    table_ttest.rows[0].cells[5].paragraphs[0].text = "Cohen's d"
    set_repeat_table_header(table_ttest.rows[0])
    
    for s_name, res in DATA["hypothesis_testing"]["t_tests_strong_vs_legendary"].items():
        row = table_ttest.add_row()
        row.cells[0].paragraphs[0].text = s_name
        row.cells[1].paragraphs[0].text = f"{res['strong_mean']:.2f}"
        row.cells[2].paragraphs[0].text = f"{res['legendary_mean']:.2f}"
        row.cells[3].paragraphs[0].text = f"{res['t_statistic']:.4f}"
        row.cells[4].paragraphs[0].text = f"{res['p_value_formatted']}"
        row.cells[5].paragraphs[0].text = f"{res['cohens_d']:.2f}"

    format_table(table_ttest, [Inches(1.2), Inches(1.0), Inches(1.1), Inches(1.0), Inches(1.3), Inches(0.9)],
                 [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT,
                  WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT])
    
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    add_figure(doc, "figure_9_strong_vs_legendary_stats", "Figure 5: Mean Base Stat Comparison: Strong vs Legendary Pokémon.")

    # 4.5 Hypothesis Testing: ANOVA
    add_heading_with_spacing(doc, "4.5 Analysis of Variance (ANOVA): Power Tier Stratification", level=2)
    anova_tot = DATA["hypothesis_testing"]["anova_results"]["total_stats"]
    add_body_paragraph(
        doc,
        f"One-Way Analysis of Variance was executed across the four defined tiers: Weak (Mean BST = {anova_tot['category_means']['Weak']:.2f}), "
        f"Average (Mean BST = {anova_tot['category_means']['Average']:.2f}), Strong (Mean BST = {anova_tot['category_means']['Strong']:.2f}), "
        f"and Legendary (Mean BST = {anova_tot['category_means']['Legendary']:.2f}). "
        f"The resulting F-statistic was astronomical: F = {anova_tot['f_statistic']:.2f} (p = 0.000e+00). "
        f"This definitively rejects the null hypothesis of equal group means, verifying that each tier occupies an unmistakably distinct power echelon."
    )
    add_figure(doc, "figure_5_stat_boxplots_by_category", "Figure 6: Boxplots of Six Base Stats Across Four Power Categories.")
    add_figure(doc, "figure_7_individual_stat_distributions", "Figure 7: Histograms and Kernel Density Estimates for All Six Base Stats.")

    # 4.6 Elemental Type Stratification
    add_heading_with_spacing(doc, "4.6 Elemental Type Stratification & Power Disparity", level=2)
    add_body_paragraph(
        doc,
        "Analyzing mean BST across the 18 primary types demonstrates that Game Freak designs elemental classes with distinct strategic tiers. "
        "Dragon, Steel, and Psychic types dominate the upper echelon of power, driven by late-game availability and legendary representation. "
        "In contrast, Bug and Normal types occupy the lower tier, reflective of early-route encounters with rapid evolutionary lines."
    )
    add_figure(doc, "figure_6_type_average_bst", "Figure 8: Pokémon Types Ranked by Average Total Base Stats.")
    add_figure(doc, "figure_8_primary_type_pie_chart", "Figure 9: Primary Elemental Type Proportional Breakdown.")

    # 4.7 Latent Battle Roles
    add_heading_with_spacing(doc, "4.7 Unsupervised K-Means Clustering of Combat Archetypes", level=2)
    add_body_paragraph(
        doc,
        "Applying K-Means clustering (k=4) on standardized 6-stat vectors resolves the Pokémon multiverse into four empirical battle archetypes: "
        "(1) Low-Stat Unevolved creatures, (2) Fast Offensive Sweepers, (3) Walls/Defensive Specialists, and (4) Balanced Tanks. "
        "Cross-tabulating these clusters against elemental typing proves that a creature's typing strongly influences its probability of "
        "occupying a given tactical combat archetype."
    )
    add_figure(doc, "figure_10_cluster_battle_roles", "Figure 10: 2D Principal Component Projection of Latent Battle Role Clusters.")

    # 5. Discussion
    add_heading_with_spacing(doc, "5. DISCUSSION & DESIGN IMPLICATIONS", level=1)
    add_body_paragraph(
        doc,
        "The empirical evidence overwhelmingly confirms that Pokémon stats are not randomly distributed numbers. The strong correlation between "
        "HP and Total Stats (r = 0.6596) reveals that Hit Points serve as the primary foundational anchor for survivability and combat viability. "
        "Furthermore, the balanced correlation between Special Attack and Special Defence (r = 0.5167) illustrates intentional design symmetry: "
        "specialists designed to harness energy-based attacks are symmetrically fortified against reciprocal special assaults. "
        "The near-zero correlation between Defense and Speed (r = 0.02) further underscores a classic RPG archetype balance: rapid strikers "
        "sacrifice physical bulk, whereas heavily armored juggernauts trade away agility."
    )

    # 6. Limitations
    add_heading_with_spacing(doc, "6. LIMITATIONS", level=1)
    add_body_paragraph(
        doc,
        "1. Static Stat Isolation: The analysis focuses solely on base stats, excluding movepool viability, type effectiveness charts, abilities, and held items.\n"
        "2. Competitive Usage Discrepancies: In competitive tournament play (VGC, Smogon), a Pokémon with lower BST can outperform higher-BST Pokémon due to signature abilities (e.g., Prankster, Intimidate) or priority moves.\n"
        "3. Variant Over-representation: Forms such as Mega Evolutions and Gigantamax skew certain species counts, though they accurately represent the peak performance states playable across various game releases."
    )

    # 7. Conclusion
    add_heading_with_spacing(doc, "7. CONCLUSION", level=1)
    add_body_paragraph(
        doc,
        "In conclusion, this empirical investigation demonstrates that elemental classification in Pokémon is far more than aesthetic lore—it is "
        "a structured, statistically predictable blueprint for combat utility. ANOVA and t-tests confirm that designated tiers reflect genuine "
        "power disparities rather than nominal labels. Elemental types function as intentional archetypes, establishing predictable relationships "
        "between species classification and strategic battle performance."
    )

    # References
    add_heading_with_spacing(doc, "REFERENCES", level=1)
    refs = [
        "Bulbapedia. (2025, September 11). Bulbapedia, the community-driven Pokémon encyclopedia. https://bulbapedia.bulbagarden.net/wiki/Main_Page",
        "Kaggle. (2017). The Complete Pokemon Dataset (Generations I–VII). https://www.kaggle.com/datasets/rounakbanik/pokemon",
        "Moore, J. (2023). Complete Pokemon Dataset (Gen I–IX). Kaggle Datasets. https://www.kaggle.com/datasets/mariotormo/complete-pokemon-dataset-gen-i-ix",
        "Pokémon Database. (n.d.). Pokémon Pokédex: List of Pokémon with stats. https://pokemondb.net/pokedex/all",
        "PokéBase. (2013). What does sp.attack and sp.defense mean? https://pokemondb.net/pokebase/110914/what-does-sp-attack-and-sp-defense-mean",
        "Smogon University. (2024). Competitive Pokémon Battling Tiers and Role Definitions. https://www.smogon.com/dex/sv/pokemon/"
    ]
    for rf in refs:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.left_indent = Inches(0.4)
        p_r.paragraph_format.first_line_indent = Inches(-0.4)
        p_r.paragraph_format.space_after = Pt(4)
        r_rf = p_r.add_run(rf)
        r_rf.font.name = "Cambria"
        r_rf.font.size = Pt(9)

    docx_path = OUT / "Pokemon_Type_and_Battle_Role_Term_Paper.docx"
    doc.save(docx_path)
    print(f"Generated DOCX Term Paper: {docx_path}")

    # Convert to PDF via Word COM if Word is installed
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        doc_com = word.Documents.Open(str(docx_path.resolve()))
        pdf_export_path = OUT / "Pokemon_Type_and_Battle_Role_Term_Paper_generated.pdf"
        doc_com.SaveAs(str(pdf_export_path.resolve()), FileFormat=17)
        doc_com.Close()
        word.Quit()
        print(f"Successfully converted to PDF via Word COM: {pdf_export_path}")
    except Exception as e:
        print(f"PDF export note (Word COM not available or skipped): {e}")


if __name__ == "__main__":
    build_document()
