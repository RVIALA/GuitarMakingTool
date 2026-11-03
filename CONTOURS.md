# GMT 1.2 — contours et pan coupé / outlines and cutaway

## Origine des formes

| Gabarit | Référence | Méthode utilisée | Dimensions de référence L × l |
|---|---|---|---|
| OM | Christophe Grellier, plan OM 2007 | Extraction des splines DXF, fermeture symétrique | 491,96 × 380,64 mm |
| Classique | Étienne Corbet, plan de guitare classique | Extraction des arcs et splines DXF, fermeture symétrique | 483,877 × 354 mm |
| Manouche D / ovale | Plan de style Maccaferri D partagé sur lutherie-guitare.org | Relevé du côté sans découpe sur le plan scanné, lissage et symétrie | 500 × 405 mm dans GMT |
| Dreadnought | Aperçu public, feuille 05, GenOne Luthier Services | Relevé du contour extérieur, lissage et symétrie, mise aux dimensions publiées | 513,8 × 397 mm ; petit lobe 293 mm ; taille 274 mm |
| Archtop | Mark French, *An Improved Body Shape Definition for Acoustic Guitars* (2017) | Adaptation du modèle rationnel publié de contour de grande caisse ; talon aplati et mise à l’échelle | 525,78 × 431,8 mm |

**L’archtop utilise un modèle publié de contour de caisse**, auquel GMT applique son bombé et ses ouïes ; ce n’est pas un plan de fabricant. Cette origine est identifiée dans l’Atelier. Les relevés manouche et Dreadnought ne sont pas des numérisations métrologiques : les incertitudes de tracé, de résolution des aperçus et de déformation des scans subsistent. La variante ovale réutilise le contour extérieur D relevé, avec une ouverture et un diapason distincts.

Les plans complets ne sont pas redistribués. Seules les données géométriques des contours et leurs attributions sont incluses dans `backend/outlines`. Les barrages, épaisseurs, chevalets et matériaux restent ceux du modèle GMT ; un contour issu d’un plan ne transforme donc pas le reste du projet en reproduction de cet instrument.

## Échelle et utilisation

La longueur et la largeur de caisse définissent les dimensions physiques en millimètres. Le contour de référence est remis à cette échelle, en conservant ses proportions relatives dans chaque direction. Les nouveaux projets utilisent les dimensions de référence. Les sessions existantes gardent leurs dimensions. Le bouton **Appliquer les dimensions de référence** rétablit les dimensions du tableau et ajuste les positions des barres, de la bouche et du chevalet. Les sections des pièces et le diapason des cordes restent indépendants.

Le pan coupé propose **aucun**, **Selmer–Maccaferri**, **vénitien archtop arrondi** ou **florentin de type ES-175**, un côté vu de face et une profondeur. La découpe agit réellement sur la table, le fond, les éclisses et la cavité. Les barres sont recoupées au nouveau bord par le constructeur géométrique. Après une modification, mailler et recalculer les FRF. Aucune remise à l’échelle du corps n’a lieu après la découpe.

Les trois profils sont distincts, stockés dans `backend/cutaways.json` :

| Profil | Construction | Profondeur initiale |
|---|---|---:|
| Selmer–Maccaferri | Épaulement réel du plan scanné Maccaferri D, relevé sur le côté découpé puis lissé ; forme caractéristique à retour presque horizontal | 60 mm |
| Vénitien archtop | Courbes paramétriques GMT raccordées, corne arrondie ; référence visuelle Benedetto La Venezia | 90 mm |
| Florentin de type ES-175 | Silhouette du pan coupé relevée sur la photographie de face publique d’une Gibson ES-175D ; lissage séparé de part et d’autre de la pointe | 78 mm |

Les extrémités sont adaptées au talon et à l’épaulement du contour choisi ; le raccord extérieur suit la tangente de la caisse. Le réglage de profondeur agit sur la gorge intérieure, en conservant la position de la corne. Il ne s’agit plus d’une ellipse soustraite. Les photographies ne sont pas rectifiées métrologiquement ; le profil ES-175 est un style adapté à la caisse GMT, pas une reproduction intégrale de cette guitare. Les nouveaux modèles manouches utilisent Selmer–Maccaferri ; l’archtop commence en vénitien. Les profils restent sélectionnables sur tous les gabarits. Une découpe excessive peut toucher la bouche ; le solveur rejette alors la géométrie incompatible.

Les anciennes sessions manouches utilisant le vénitien interne passent au profil Selmer, avec profondeur 60 mm si elles utilisaient l’ancienne valeur initiale de 95 mm. Une profondeur personnalisée est conservée. Les autres styles restent sélectionnés et bénéficient du nouveau tracé. Les contours SVG personnels sont conservés.

L’import SVG reste disponible. Il conserve un pan coupé déjà dessiné et désactive initialement la découpe supplémentaire. Le bouton Contour initial revient au contour de référence de la famille. Les anciennes sessions sans champs de pan coupé sont compatibles ; les anciens contours internes sont remplacés par les nouveaux, tandis que les SVG personnels sont conservés.

L’export SVG est en mm, à échelle 1:1, avec marge et repère de contrôle de **100 mm**. Imprimer sans ajustement automatique, puis contrôler le repère à la règle. Les SVG d’exemple du dossier `examples/outlines` contiennent les tracés seuls. Ce sont des géométries de simulation ; aucune précision de fabrication CNC n’est certifiée.

## Affichage et calcul

L’affichage utilise le contour détaillé. Le maillage utilise une simplification commune à toutes les pièces avec un écart de Hausdorff contrôlé à **1,005 fois la tolérance choisie** (0,08 mm par défaut, soit 0,0804 mm). Cela évite un grand nombre de minuscules arêtes CAO. Le bord n’est pas recalé indépendamment d’une pièce à l’autre. Les éclisses, les interfaces et le volume acoustique restent construits à partir du même polygone.

Les dimensions et les origines sont visibles dans l’Atelier. Les données restent disponibles hors connexion ; aucun téléchargement n’est nécessaire à chaque lancement. Les dépendances Python sont inchangées depuis 1.0.

## Sources et conditions des contenus

- **Christophe Grellier**, plan OM, DXF publié par l’auteur : https://www.grellier.fr/en/downloads ; fichier https://www.grellier.fr/static/data/plans/OM_acoustic_guitar/OM_acoustic_guitar.dxf . La page de l’auteur lie la licence **CC BY-NC-SA 2.0 FR** : https://creativecommons.org/licenses/by-nc-sa/2.0/fr/ . Le fichier `backend/outlines/om.json` est une adaptation : extraction du contour, symétrisation, rééchantillonnage et normalisation. Cette donnée de contour conserve cette licence, y compris sa restriction d’utilisation commerciale ; la licence GPL du code ne la remplace pas.
- **Étienne Corbet**, plan classique : https://lutherie-guitare.org/wiki/Chapitre_6_:_Plans ; DXF https://lutherie-guitare.org/mediawiki/images/6/61/Guitare-classique-EC-a0.dxf . Données de contour extraites et symétrisées, attribution conservée. Le site met le plan à disposition sans préciser de licence ouverte dans la page consultée ; aucune licence CC particulière n’est revendiquée pour le plan original.
- **Plan manouche de style Maccaferri**, partagé par lutherie-guitare.org depuis luthier-amateur.org : https://lutherie-guitare.org/mediawiki/images/9/9a/Manouche_macca1.pdf . Auteur original non identifié dans le document consulté. Relevé géométrique partiel, redressé, lissé et symétrisé ; aucune redistribution du plan complet ni revendication de licence du document original.
- **GenOne Luthier Services**, plan Dreadnought et cotes publiées : https://genone-luthier-supply.com/products/dreadnought-guitar-plans . Contour relevé depuis l’aperçu public de la feuille 05 : https://genone-luthier-supply.com/cdn/shop/products/05_dreadnoughtplan_5_2000x.png . Le côté sans découpe est relevé, lissé et symétrisé, puis mis aux dimensions publiées. L’aperçu et le plan complet ne sont pas redistribués ; les droits du document original restent à son auteur. Aucun achat ni accès au fichier payant n’a été effectué.
- **Benedetto**, La Venezia, référence de pan vénitien archtop : https://www.benedettoguitars.com/product/la-venezia/ . Le profil GMT est paramétrique, inspiré de cette référence visuelle, sans traçage CAO revendiqué.
- **Gibson**, ES-175D de 1960, référence de pan florentin : https://www.gibson.com/products/gibson-certified-vintage-1960-gibson-es-175d-natural . Relevé partiel de silhouette sur la photographie publique de face, adapté ; la photographie n’est pas redistribuée.
- **Mark French**, Savart Journal (2017) : https://www.savartjournal.org/articles/26/article.pdf ; dépôt auteur https://arxiv.org/abs/1802.00439 . Modèle mathématique de contour adapté, remis à l’échelle et modifié au talon. Il ne s’agit pas d’un plan d’archtop issu d’un fabricant.

Le code GMT et ses variantes paramétriques restent sous GPL-3.0-or-later. Les conditions des contenus de référence sont distinctes. Les noms de fabricants et de luthiers désignent des références, sans affiliation ni approbation.

## English

OM and classical outlines are extracted from the Grellier and Corbet DXFs. The gypsy shape is digitised from a scanned Maccaferri-style D-hole plan and mirrored; the oval-hole preset reuses that outer outline. Dreadnought is digitised from GenOne’s public sheet-05 preview, smoothed, mirrored and scaled to the published dimensions. Digitisation from a preview is not metrological CAD extraction. Archtop adapts Mark French’s published rational body-shape model, **not an archtop maker’s plan**.

New projects start at reference dimensions; existing sessions keep their dimensions. All outlines scale to the body dimensions in mm. “Apply reference dimensions” restores the table’s size and rescales component positions. Separate Selmer–Maccaferri, rounded archtop Venetian and ES-175-style Florentine profiles change the actual top, back, ribs and cavity; solve again for new FRFs. Side is defined in front view. No body rescaling follows the cut. SVG import preserves an existing cutaway and initially disables additional cutting. SVG export is 1:1 in mm with a 100 mm calibration mark.

The detailed display and common CAD polygon use a configurable CAD simplification tolerance (0.08 mm by default), checked to within 1.005 times that tolerance in the Hausdorff metric. This bounds outline simplification, not manufacturing accuracy. Source DXFs, scans and their complete plans are not redistributed. The Grellier-derived OM outline data retain **CC BY-NC-SA 2.0 FR**, including its non-commercial condition. The code’s GPL license does not override content-specific conditions. Corbet and the scanned gypsy plan have the attribution/provenance described above; no unverified open license is claimed for their originals.

The Selmer cutaway is digitised from the actual cut side of the cited Maccaferri plan. The Venetian is GMT’s tangent-connected parametric profile, visually informed by Benedetto La Venezia. The Florentine is digitised from the public Gibson ES-175D front photograph, smoothing each side of the pointed horn separately. Endpoints are adapted to the chosen body; these are reference-based simulation profiles, not certified manufacturing outlines. New gypsy projects use Selmer at 60 mm; archtop uses Venetian at 90 mm. Older internal gypsy Venetian sessions migrate to Selmer, preserving custom depth and personal SVGs.
