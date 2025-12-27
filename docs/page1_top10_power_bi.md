# Page 1 — Top 10 Visuels Essentiels (Power BI)

Executive dashboard Supply Chain avec mesures DAX, champs, légendes et couleurs prêtes à l'emploi. Adapter les noms de colonnes si vos schémas diffèrent.

---

## Filtres Globaux Recommandés
- Année / Période
- Région (`order_region`) / Pays (`customer_country`)
- Transporteur (`carrier`)
- Catégorie produit (`product_category`)
- Mode d'expédition (`shipping_mode`)

## Palette Couleurs (Thème Professionnel)
- Primaire : #1E3A8A (bleu marine)
- Succès : #10B981 (vert)
- Warning : #F59E0B (orange)
- Danger : #EF4444 (rouge)
- Neutre : #6B7280 (gris)
- Accent : #8B5CF6 (violet)

---

## 1) KPI — Ventes Totales
**Mesure DAX**
```DAX
Total Sales := SUM ( 'supply_chain_raw'[sales] )
```
**Légende** : "Chiffre d'affaires cumulé sur la période filtrée."
**Tooltips** : Nombre de commandes, Panier moyen, % du CA total.

## 2) KPI — Nombre de Commandes
**Mesure DAX**
```DAX
Order Count := COUNTROWS ( 'supply_chain_raw' )
```
**Légende** : "Volume total de commandes traitées."
**Tooltips** : Ventes totales, Jours moyens d'expédition.

## 3) KPI — Panier Moyen (AOV)
**Mesure DAX**
```DAX
Avg Order Value := DIVIDE ( [Total Sales], [Order Count] )
```
**Légende** : "Montant moyen par commande."
**Tooltips** : Distribution par catégorie produit.

## 4) KPI — Taux de Livraison à l'Heure
**Mesures DAX**
```DAX
On-Time Deliveries :=
CALCULATE (
    COUNTROWS ( 'supply_chain_raw' ),
    'supply_chain_raw'[days_for_shipping_real] <= 'supply_chain_raw'[days_for_shipment_scheduled]
)

Late Deliveries :=
CALCULATE (
    COUNTROWS ( 'supply_chain_raw' ),
    'supply_chain_raw'[days_for_shipping_real] > 'supply_chain_raw'[days_for_shipment_scheduled]
)

On-Time Rate % := DIVIDE ( [On-Time Deliveries], [On-Time Deliveries] + [Late Deliveries] )
```
**Légende** : "Proportion de livraisons ponctuelles sur la période."
**Couleur** : vert si > 90%, orange 80–90%, rouge < 80%.

## 5) Jauge — Jours d'Expédition Moyens (Réel)
**Mesure DAX**
```DAX
Avg Delivery Days (Actual) := AVERAGE ( 'supply_chain_raw'[days_for_shipping_real] )
```
**Champs** : Valeur = `Avg Delivery Days (Actual)`, Min = 0, Max = 7 (adapter).
**Légende** : "Durée moyenne de livraison (jours)."
**Couleur** : vert < 3.0, orange 3.0–4.0, rouge > 4.0.

## 6) Barres Horizontales — Ventes par Année
**Champs** : Axe Y = `Dates[Year]` (ou `order_date_dateorders` → Année), Axe X = `Total Sales`.
**Légende** : "Évolution annuelle des ventes." 
**Tooltips** : Commandes, AOV, Taux on‑time.
**Tri** : Descendant par ventes.

## 7) Barres — Ventes par Région
**Champs** : Axe X = `order_region`, Axe Y = `Total Sales`.
**Légende** : "Contribution des régions au chiffre d'affaires."
**Couleur** : dégradé accent (violet) sur volume.
**Options** : Small multiples par `shipping_mode` pour comparaison.

## 8) Barres — Top 10 Produits par Ventes
**Champs** : Catégorie = `product_name` (Top N = 10), Valeurs = `Total Sales`.
**Légende** : "Produits générant le plus de ventes."
**Tooltips** : Quantité, Commandes, AOV.
**Tri** : Descendant.

## 9) Secteurs (Pie) — Répartition du CA par Catégorie
**Champs** : Légende = `product_category`, Valeurs = `Total Sales`.
**Légende** : "Parts du chiffre d'affaires par catégorie produit."
**Labels** : % + valeur (format K/M).
**Couleur** : palette accent (violet) déclinée.

## 10) Secteurs (Pie) — Retards par Transporteur
**Champs** : Légende = `carrier`, Valeurs = `Late Deliveries`.
**Légende** : "Poids des retards par transporteur."
**Couleur** : rouge (Danger) pour parts dominantes, neutre pour autres.
**Action** : drill‑through vers page "Transporteurs".

---

## Paramétrage Rapide (Recommandations)
- Format des devises : K/M, séparateur d'espaces insécables.
- Tooltips enrichis : ajouter `Order Count`, `Avg Order Value`, `On-Time Rate %`.
- Slicers synchronisés sur toutes les pages.
- Titres dynamiques : "Période: " & SELECTEDVALUE(Dates[Year]) & ", Région: " & SELECTEDVALUE('supply_chain_raw'[order_region]).

## Bonnes Pratiques Couleurs
- On‑time → vert (#10B981)
- Retards → rouge (#EF4444)
- Risque élevé → orange (#F59E0B)
- Revenus → violet (#8B5CF6)
- Axes/texte 
→ gris neutre (#6B7280)

---

Ce document complète le guide principal et sert de checklist prête à l'emploi pour construire la première page du reporting Power BI.