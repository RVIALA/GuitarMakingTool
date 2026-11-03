# SVG des ouvertures / Opening SVGs

Dans **Atelier → Rosace, ouïes & chevalet**, cliquer **Importer des ouïes SVG**. Les deux exemples contiennent uniquement les découpes. Le SVG de la caisse s’importe avec le bouton SVG du plan, qui reste distinct.

- `deux_ouies_ovales.svg` : deux ouvertures dans un seul fichier ; leur écartement relatif est conservé.
- `ouie_courbe.svg` : une ouverture originale dessinée avec des courbes de Bézier.

L’import conserve les proportions initiales et adapte l’ensemble à la hauteur courante, en limitant sa largeur à 70 % de celle de la caisse. **Les dimensions physiques du fichier ne sont pas reprises automatiquement.** Les champs largeur et hauteur indiquent les dimensions totales en millimètres ; ajuster ces valeurs et la position après import. Pour une seule ouïe, les dimensions concernent cette ouïe ; pour plusieurs, elles incluent leur espacement.

Formats pris en charge : path (M/L/H/V/C/S/Q/T/A/Z, relatifs ou absolus), polygon, polyline fermée, circle, ellipse, rect et transformations de groupes. Dessiner des contours fermés, pas de simples traits : l’épaisseur de trait SVG n’est pas transformée en largeur de découpe. Convertir texte, clones et objets en tracés ; aplatir les découpes et transformations CSS. Les éléments de définition ne sont pas importés.

Limites : 1 Mo, 8 ouvertures, 384 sommets par contour et 2048 au total après approximation. Les contours imbriqués, croisés, superposés ou trop proches ne sont pas acceptés. Une ouverture doit rester à l’intérieur des éclisses et hors du chevalet. Si l’import ne tient pas à la position courante, déplacer ou réduire l’ouverture actuelle puis réimporter. L’échec d’un import conserve le projet précédent.

Les contours et leur nom sont inclus dans la session JSON ; aucun lien au fichier SVG initial n’est nécessaire. Après modification, **Mailler & calculer EF** met à jour les modes, la cavité, les FRF et la synthèse.

## English

Use **Workshop → Soundholes & bridge → Import SVG openings**. Import only the opening outlines, using the separate plan SVG button for the body shape.

Import preserves aspect ratio, fits the current opening height and caps overall width at 70% of body width. **Physical SVG dimensions are not automatically retained.** Set total width/height in millimetres and position after import. For multiple openings, dimensions include spacing.

Paths (M/L/H/V/C/S/Q/T/A/Z), polygons, closed polylines, circles, ellipses, rectangles and group transforms are supported. Convert text/clones to paths and flatten CSS transforms and clipping. Strokes are treated as outline centre lines; stroke thickness does not create an opening.

Limits: 1 MB, eight separate closed openings, 384 vertices per contour and 2048 total after approximation. Nested, intersecting, overlapping and too-close contours are rejected. Openings must fit inside the ribs, clear of the bridge. If import does not fit, adjust current opening size/position and retry; failed imports leave the previous project intact.

JSON sessions retain all outline points. Run the FE solve again after changing openings to update the physical model and sound.
