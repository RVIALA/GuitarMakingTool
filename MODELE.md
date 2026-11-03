# GMT 1.3 — modèle vibroacoustique / vibroacoustic model

## 1. Objectif et unités

GMT calcule une mobilité multipoint de caisse acoustique et son interaction avec six cordes pincées. L’objectif est l’exploration de paramètres de lutherie et leur comparaison à conditions de jeu constantes. Une calibration et une étude de convergence sont nécessaires pour un instrument réel.

Le projet utilise mm, GPa, kg/m³, degrés et pourcentages. Le solveur convertit en SI : m, Pa, kg, s. Axe x transversal ; y du bas de caisse vers le manche ; z devant la table. La caisse plane a une table entre z=0 et son épaisseur, un fond près de z=−profondeur. Le point d’écoute P utilise directement des mètres. La normale d’une face est orientée par son tétraèdre propriétaire.

## 2. Géométrie et assemblage

Les contours internes sont désormais des données de référence : DXF OM de Christophe Grellier, DXF classique d’Étienne Corbet et relevé de plan manouche Maccaferri D. La Dreadnought est relevée sur un aperçu public du plan GenOne, lissée, symétrisée et remise aux cotes publiées ; l’archtop adapte le modèle de contour de Mark French. Ce dernier n’est pas un plan d’archtop de fabricant. Sources, méthodes, dimensions et conditions des contenus sont détaillées dans CONTOURS.md.

Les variantes de pan coupé modifient la géométrie avant la construction des pièces. Les profils Selmer–Maccaferri, vénitien archtop et florentin de type ES-175 sont distincts : relevé de plan, profil paramétrique arrondi et relevé photographique pointu respectivement. Ils sont raccordés au contour choisi ; la profondeur agit sur la gorge intérieure. Voir CONTOURS.md pour les sources et les limites de ces relevés. Le contour n’est pas remis à l’échelle après la découpe. Une simplification commune à toutes les pièces est contrôlée par une tolérance réglable (0,08 mm par défaut), avec une borne de Hausdorff de 1,005 fois cette tolérance. Le tracé affiché reste détaillé.

Un contour SVG est normalisé aux dimensions de caisse choisies. Les ouvertures sont des géométries indépendantes (ronde, ovale, D ou deux ouïes). La table, le fond, le ruban d’éclisses, les barres, le bloc de manche et le chevalet sont des volumes OpenCASCADE. Les barres sont découpées contre le contour intérieur et les ouvertures. Leur hauteur est constante sur trois segments : facteur d’extrémité, hauteur centrale, facteur d’extrémité. Le chevalet flottant est constitué de deux pieds et d’une traverse reliés géométriquement.

Les opérations booléennes fragmentent tous les volumes avant maillage. Les recouvrements sont attribués dans l’ordre table, fond, éclisses, barres, chevalet, air. Au croisement de barres, le volume de recouvrement adopte les axes de la première barre. Ce choix n’est pas une simulation de mi-bois détaillée. Les assemblages sont parfaitement collés, sans éléments de contact.

Le bombé transforme une seule fois chaque nœud partagé :

h(x,y) = H max(0,1−(2x/W)²) max(0,sin(πy/L))^1,2.

La déformation verticale est interpolée entre bombé de table et bombé de fond à travers la caisse. Les jonctions restent conformes. Cette transformation n’est ni un calcul de cintrage ni une loi exacte d’épaisseur normale d’une table sculptée. Les aperçus 3D de l’Atelier sont simplifiés ; la vue Maillage montre la géométrie effectivement calculée.

## 3. Bois orthotrope

Les matériaux ont ρ, E_L, E_R, E_T, G_LR, G_LT, G_RT, ν_LR, ν_LT, ν_RT et un facteur de perte η. Le tenseur de souplesse emploie les déformations de cisaillement d’ingénieur. S_ij=−ν_ij/E_i et S_ji=S_ij assurent la réciprocité. La matrice doit être définie positive. Les constantes initiales sont des valeurs plausibles d’exploration, **pas des valeurs extraites intégralement d’un tableau d’essence ou d’un jeu de cordes précis**.

- Table et fond : L suit la longueur, R la largeur et T l’épaisseur. Les deux directions L/R sont transportées par le jacobien du bombé suivant x et y, puis réorthonormalisées. À rotation de fil/débit nulle, toutes deux sont tangentes à la surface.
- Barres : L suit chaque barre, R sa hauteur, T sa largeur.
- Éclisses : L suit la tangente au contour cintré, R suit la hauteur et T l’épaisseur.
- Chevalet : L suit sa largeur x.

Les directions de toutes les pièces suivent d’abord la transformation des nœuds, y compris à travers la hauteur des éclisses et des barres. La rotation de fil agit dans le plan L/R local ; la rotation de débit tourne R/T autour de L. Les repères sont évalués au centre de chaque élément, pas en chaque point d’intégration. La courbure n’introduit aucune contrainte résiduelle. Le tenseur est tourné via une transformation énergétique des déformations, évitant une rotation incorrecte des termes de cisaillement.

## 4. Structure EF et réduction

Le bois est maillé en tétraèdres quadratiques TET10. L’élasticité est tridimensionnelle linéaire :

K_e = ∫ Bᵀ C_global B dV ; M_e = ∫ ρ Nᵀ N dV.

Onze points de quadrature d’ordre quatre intègrent la masse et les éléments affines ; la géométrie courbe est intégrée avec la même règle. Les jacobiens nuls ou changeant de signe sont rejetés. La masse est consistante. Les nœuds géométriquement distincts mais superposés et les composantes déconnectées sont rejetés à la construction.

Trois conditions de maintien : bloc de manche fixé (20 derniers mm), libre, ou éclisses bloquées. En configuration libre, les modes sous 5 Hz sont écartés. Aucun manche, sillet de tête ou main du musicien n’est modélisé mécaniquement. Les cordes ont une extrémité supérieure fixe dans la synthèse.

Kφ_m=ω_m²Mφ_m, avec φ_mᵀMφ_m=1. Les modes affichés sont ceux de la structure sèche. Le facteur de perte modal est pondéré par l’énergie élastique de chaque matériau : η_m=Ση_i φ_mᵀK_iφ_m/ω_m², ζ_m=η_m/2. Le résidu modal est évalué sur les degrés de liberté libres.

La force ponctuelle est distribuée par les fonctions de forme quadratiques d’une face de chevalet. Il existe six points de contact et deux directions par point : z et x. Cela fournit une matrice de mobilité 12×12, incluant les termes croisés. Les courbes affichées sont les douze réponses de point ; le couplage des cordes utilise la matrice complète.

La bande d’extraction des modes secs se règle par fmin/fmax, avec un budget maximal de modes (96 par défaut, plafond 180). Le solveur extrait les modes de la bande dans la limite de ce budget ; le rapport précise si la borne supérieure a été couverte. Les modes inférieurs à 5 Hz sont exclus. La bande de synthèse se règle séparément et ne déclenche aucun nouveau maillage.

Une projection résiduelle de flexibilité complète la base aux douze efforts de port B. Pour les degrés de liberté libres :

S = K⁺ B − Φ Ω⁻² Φᵀ B.

K⁺ est l’inverse contraint, ou l’inverse élastique avec contraintes de masse éliminant les six mouvements rigides lorsque le support est libre. S est réorthogonalisée en masse par rapport aux modes retenus. Une mise à l’échelle en énergie élimine les dépendances numériques ; le problème de Rayleigh–Ritz réduit Kᵣ ψ = λ Mᵣ ψ donne au plus douze vecteurs complémentaires normalisés en masse. Les projections d’effort, de vitesse, d’interface air/bois et de rayonnement utilisent cette base augmentée commune. Le test de flexibilité compare BᵀK⁺B à la somme corrigée.

Les vecteurs résiduels ne sont pas des modes propres résolus. Leur amortissement (10 % du critique par défaut, réglable de 1 à 30 %) lisse une réponse approchée ; ce n’est pas une propriété mesurée du bois. Les résonances et antirésonances manquantes ne sont pas récupérées intégralement. La correction peut aussi représenter des modes écartés sous fmin. Les zones hors de la bande modale effectivement retenue restent identifiées dans la FRF. Vérifier la convergence en maillage et en nombre de modes avant toute conclusion quantitative.

Le maillage est limité à 90 000 nœuds globaux et 180 000 degrés de liberté mécaniques. Le réglage initial est 25 mm / 96 modes mécaniques / dix modes de cavité. Le coût dépend de la géométrie ; voir VERIFICATION.md.

## 5. Air intérieur et ouverture

La cavité est maillée si le fond et les éclisses sont présents et le couplage activé. Elle inclut le conduit de l’ouverture à travers la table. La pression utilise les quatre sommets de chaque tétraèdre (TET4), même si le fichier de maillage commun conserve dix nœuds par cellule.

K_a=∫∇Nᵀ∇N dV ; M_a=∫NᵀN dV.

Les modes de cavité rigide, dont le mode uniforme de fréquence nulle, sont massiquement normalisés avec M_a. Le couplage C entre déplacement mécanique et pression est intégré sur les faces communes avec une quadrature triangulaire à six points et les mêmes coordonnées géométriques. Les faces acoustiques sont planes au niveau de leurs sommets : une forte courbure exige un raffinement.

Une coordonnée de déplacement volumique d’ouverture complète la base réduite. Son inertance extérieure est ρ L_ext/S, L_ext=κ sqrt(S/π). Le conduit physique est déjà dans le volume EF ; son épaisseur n’est pas ajoutée une seconde fois à cette inertance. Le facteur κ est modifiable (1,7 initial). Pour les deux ouïes, l’ouverture équivalente utilise leur aire totale et **une seule coordonnée de débit** : les écoulements indépendants de chaque ouïe ne sont pas résolus.

La résistance combine un terme de rayonnement monopolaire à faible ka et un terme dissipatif réglable. Un amortissement modal acoustique de 2,5 % est appliqué aux modes non uniformes. L’indication « Helmholtz, caisse rigide » est une estimation séparée f_H=c/(2π)sqrt(S/(V(t_top+L_ext))), pas le pic réel du système couplé.

Les équations couplées sont résolues en fréquence après projection. La mobilité est Y(ω)=jω PᵀD_couplé(ω)^−1P. Le modèle possède une compliance de cavité uniforme, une inertance de bouche et des modes de structure réellement calculés. Il ne construit pas la FRF comme une somme de pics prépositionnés suivant le type de guitare.

## 6. Rayonnement extérieur

À ce stade, l’extérieur n’est pas maillé. Chaque face mécanique extérieure fournit son débit modal signé, obtenu par la moyenne surfacique quadratique (poids nuls aux sommets, 1/3 aux milieux d’arêtes). Le champ est approché par des panneaux monopôles :

p(P,ω) ≈ −ρ ω²/(4π) Σ_j [e^(−jkr_j)/r_j] A_j n_j·u_j + terme d’ouverture.

La phase de propagation et le point P sont pris en compte. La surface discrète est représentée par son centre pour le noyau de propagation. La bouche ajoute le débit de sa coordonnée réduite. Cette approximation néglige la diffusion par la caisse, le problème intégral extérieur complet, le champ d’une salle et la directivité fine. Le modèle n’est pas une prédiction calibrée de SPL. P doit rester au moins à 30 mm des centres des panneaux ; cela ne constitue pas un test complet d’appartenance à l’extérieur pour une caisse arbitraire. Placer P clairement devant l’instrument (z=1 m par défaut).

## 7. Cordes pincées et chargement

Les six cordes sont décrites par μ, EI, pertes et accordage. Les trois familles démarrent avec des ordres de grandeur différents, sans recopier des tensions de fabricants. La tension d’accordage est déduite de la fréquence à vide et du diapason L_0 :

T = 4 μ L_0² f_0² − π²EI/L_0².

Un frettage raccourcit la longueur active à L=L_0 2^(−n/12), avec tension conservée. Le pincement statique sous une force F à la distance x_p donne, pour k_n=nπ/L :

q_n(0)=2F sin(k_n x_p) / [L(Tk_n²+EI k_n⁴)].

Un lissage sinc dépend de la largeur de contact ; la dureté et le type doigt/médiator atténuent les harmoniques aiguës. La force bloquée au chevalet de chaque mode est (Tk_n+EI k_n³)q_n. Le mouvement libre amorti est ensuite développé jusqu’à 384 partiels, sous 0,48 fois la fréquence d’échantillonnage et sous 1,1 fois la borne supérieure de synthèse avant fenêtrage. L’amortissement α(f)=σ+σ_h f+2·10^−8 f² est empirique.

L’impédance dynamique de la corde inclut une solution propagative et une solution évanescente de la corde raide, à conditions de moment nul aux extrémités. La caisse et les cordes sont reliées par :

F = (I + Z_s Y)^−1 F_bloquée ; v=YF ; p=H_pF F.

Ainsi, F est la force chargée réelle du modèle linéaire, et non une force imposée inchangée multipliée ensuite par une simple coloration. Les cordes non excitées peuvent charger la caisse par sympathie. Les mêmes paramètres sont utilisés pour l’aller et le retour de couplage. Les deux polarisations sont considérées identiques dans la corde ; la caisse est anisotrope et distingue leurs chargements. Il n’y a ni torsion, ni roulement sur le chevalet, ni contact non linéaire du doigt ou du médiator.

Le calcul utilise 44 100 échantillons/s. Chaque réponse individuelle est calculée par FFT sur la durée choisie, avec deux secondes supplémentaires de prolongement, indépendamment des instants d’attaque de la phrase. La partie à partir de l’origine du pincement est conservée ; les 10 dernières millisecondes sont fermées par une fenêtre cosinus. Les réponses sont décalées à l’échantillon le plus proche, multipliées par la force relative de chaque attaque et sommées. Une attaque ultérieure ne peut contribuer à un instant antérieur. Le placement est exact, mais les transitoires restent une approximation par FFT finie ; ce découpage n’est pas une preuve de causalité exacte du filtre physique. Les longues décroissances et le prolongement doivent être vérifiés par convergence.

La FRF est interpolée sous forme complexe. L’interpolation linéaire de matrices de mobilité passives conserve leur partie hermitienne positive. La grille de caisse s’étend jusqu’à max(6 kHz, f max de synthèse) ; le fenêtrage annule les fréquences au-delà de la bande choisie. La continuation numérique 1/f hors grille n’est donc pas une source d’aigus dans cette bande. La projection résiduelle complète la base EF lorsqu’elle est activée. La résolution de toutes les résonances très étroites de cordes n’est pas certifiée : une convergence fréquentielle reste nécessaire.

## 8. Édition de FRF et écoute

Chaque mode peut changer virtuellement de fréquence, ζ et participation (±24 dB). Le facteur de participation est appliqué de façon cohérente aux ports, au couplage acoustique et aux débits rayonnants. Ce sont des expériences sur le modèle réduit, sans correspondance géométrique identifiée.

Les signaux physiques sont synthétisés à 44,1 kHz et conservés en float32 SI. La bande choisie (20 Hz–10 kHz par défaut, réglable jusqu’à 20 kHz) s’applique aux trois sorties par un fenêtrage fréquentiel à transitions cosinus à l’intérieur de ses bornes. Jusqu’à 384 partiels de corde sont considérés, limités par la bande et l’échantillonnage. L’écoute n’ajoute plus de passe-bas lié au dernier mode EF. Le gain suit le mode crête, RMS ou fixe. Si nécessaire, un gain global protège la crête à 0,9 FS sans écrêtage. La réduction est affichée pendant la lecture ; elle peut modifier une comparaison en gain fixe. Le gain Web Audio est lissé pendant les réglages sans recréer le signal. La fenêtre de fin de note et le découpage temporel peuvent introduire une fuite spectrale en bord de bande. Les WAV physiques conservent les valeurs calculées ; les WAV PCM16 contiennent l’écoute. Aucun effet de pédale ni micro électrique n’intervient.

## 9. Sources primaires et traçabilité

- Gmsh 4.15.2, documentation officielle : https://gmsh.info/doc/texinfo/gmsh.html — booléens conformes et éléments d’ordre deux.
- USDA Forest Products Laboratory, Wood Handbook, chapitre 5, *Mechanical Properties of Wood* : https://research.fs.usda.gov/treesearch/62244 — orthotropie, directions et réciprocité. Les valeurs initiales GMT restent illustratives.
- Martin, OM-28, documentation officielle : https://www.martinguitar.com/10Y25OM28.html — référence de famille/diapason, pas un plan de caisse copié.
- John Le Voi, Selmer-style guitars : https://www.johnlevoiguitars.co.uk/selmer.htm — variantes de diapason 670/640 mm.
- D’Addario, EJ16 12–53 : https://www.daddario.com/products/ej16-phosphor-bronze-acoustic-guitar-strings-light-12-53 — référence de famille de cordes acier. Les μ et EI GMT ne sont pas une identification de ce jeu.
- Savarez, Argentine : https://www.savarez.com/argentine-boule-1540x — référence de famille de cordes manouches, sans attribution de nos constantes.
- Jim Woodhouse, Euphonics : https://euphonics.org/4-2-2-coupling-of-a-helmholtz-resonator-and-a-body-mode/ ; https://euphonics.org/5-1-1-coupling-a-string-to-the-instrument-body/ ; https://euphonics.org/4-3-sound-radiation/ — principes de couplage et rayonnement.
- Revue de modèles acoustiques de guitare : https://doi.org/10.3390/acoustics4010012 ; exemple de comparaison modèle/mesure : https://pubmed.ncbi.nlm.nih.gov/34241441/ . GMT n’est pas leur implémentation ni une reproduction de leurs résultats.

L’implémentation, les paramètres illustratifs et les tests reproductibles sont inclus. PickupTool Lab fournit la continuité du geste de pincement et de l’interface d’écoute ; aucune chaîne électrique ou de pédales n’est conservée.

## English technical scope

The code implements conformal volumetric orthotropic TET10 elasticity, a TET4 pressure cavity with the uniform mode retained, modal fluid–structure coupling and a twelve-port bridge mobility. The soundhole’s physical neck is meshed; only its exterior end correction is added as a lumped inertance. All six plucked strings load the full mobility matrix through their stiff-string driving-point impedances. Initial displacement follows the static point-force solution, with empirical contact smoothing and damping.

Exterior pressure is a signed monopole-panel plus aperture-flow approximation with propagation phase, not an exterior BEM solution or calibrated SPL. Arching is a geometric warp, joints are perfectly bonded, brace profiles use three constant-height segments, crossing volumes take the first brace’s material frame, and no prestress, neck mechanics or string torsion is solved. Both f holes share one reduced aperture-flow coordinate. Body responses are limited by the retained modal basis; refine the mesh and increase structural/acoustic modes before quantitative interpretation. The supplied numerical checks and analytical benchmarks validate implementation components; they do not experimentally validate a real guitar.


## 10. Affichage des modes, barrages et contacts

Les barrages et le bloc de manche sont des volumes TET10 fragmentés avec les autres pièces ; leurs interfaces partagent les mêmes nœuds. La visualisation inclut désormais les surfaces bois/air internes, qui n’étaient pas dessinées dans la version 1.1. Un tableau indique les nombres de tétraèdres et les volumes par pièce. La vue intérieure et les masques table/fond/éclisses/barrages servent à les inspecter. Les assemblages restent parfaitement collés et les barres ont toujours trois segments de hauteur.

Les faces à six nœuds sont interpolées avec leurs fonctions quadratiques, tant pour la position que pour le déplacement. Le niveau 2/3/4 règle la subdivision d’affichage ; il ne raffine pas le calcul EF. Les franges montrent l’enveloppe |u| ou une composante X/Y/Z signée, normalisée pour chaque mode. Les palettes et les niveaux continu/8/16/32 changent le rendu. L’amplitude d’animation reste visuelle et ne représente pas une excitation en newtons.

Le contour partagé des éclisses utilise une tolérance plus fine (0,08 mm par défaut au lieu de 0,20 mm). La caisse reste construite par volumes à section polygonale et transformation de bombé ; ce n’est pas une simulation du cintrage ou d’une épaisseur sculptée exacte.

Les six positions de corde sont interpolées sur la surface du chevalet, chacune dans les directions Z (normale) et X (transversale). Les FRF affichées sont les réponses propres au point Yᵢᵢ et p(P)/Fᵢ. L’option caisse + air montre le corps couplé à sa cavité sans charge des cordes ; l’option avec cordes utilise :

Y_chargée = Y (I + Z_cordes Y)⁻¹ ; H_chargée = H (I + Z_cordes Y)⁻¹.

La synthèse utilise également les transferts entre ports de la matrice complète 12 × 12, et pas seulement les six diagonales affichées. Les courbes chargées emploient l’accordage et les doigtés courants des six cordes. Les positions sont repérées sur le dessin du chevalet et dans la vue du maillage.

## 11. Spectrogramme et sélection

L’onglet Spectrogramme dispose de sa propre bande de visualisation, indépendante des bandes modale et de synthèse. FFT 1024 à 16384, fenêtres Hann/Hamming/Blackman/rectangulaire, axe fréquentiel linéaire/logarithmique, palettes et dynamique sont réglables. La normalisation de fenêtre corrige le gain cohérent pour afficher une amplitude en dB re 1 N, m/s ou Pa, ou des couleurs référencées à la crête de la prise. Ce n’est pas une densité spectrale par Hz.

Un rectangle délimite temps et fréquence. L’écoute et l’export de sélection emploient cette portion temporelle avec un filtre fréquentiel à transitions cosinus et des fondus courts aux extrémités ; la prise physique intégrale reste disponible. Un curseur, une vue temporelle, une barre de déplacement, pause/reprise et volume complètent la navigation. FFT, fenêtre et axes de l’analyse ne relancent pas la synthèse. Les principaux réglages sont conservés dans la session JSON.

Référence de méthode pour les vecteurs résiduels : Ansys, Theory Reference, §14.8.5 : https://ansyshelp.ansys.com/public/Views/Secured/corp/v261/en/ans_thry/thy_tool9.html . GMT implémente sa propre projection sur les matrices EF ; aucune bibliothèque ou routine Ansys n’est utilisée. Impédance de corde : Jim Woodhouse, Euphonics §5.4.6 : https://euphonics.org/5-4-6-frequency-responses-for-string-synthesis/ .

### English — 1.2 additions

Modal extraction has its own frequency interval and mode budget; synthesis uses a separate band (default 20 Hz–10 kHz at 44.1 kHz). Playback no longer low-passes at the last FE mode. Static residual-flexibility vectors driven at all twelve bridge loads augment the elastic basis through a mass-normalised Ritz projection, including cavity and radiation projections. Their editable 10% default critical damping is an approximation setting. They do not resolve the omitted resonances or establish high-frequency mesh/radiation convergence.

Internal brace faces are displayed, with actual part element counts. Quadratic six-node surface interpolation supplies mode envelopes/signed components and continuous or banded palettes. Six bridge contacts have separate driving-point FRFs, optionally including all six current string impedances. The Spectrogram tab controls time/frequency axes, FFT/window/palette/levels and selected time-frequency playback/export, with independent display settings and pause/seek.

En maintien libre, la flexibilité statique élastique utilise une résolution contrainte qui retire les six mouvements rigides. Le contrôle 1.2 a trouvé un écart de récupération de compliance aux ports d’environ 0,21 %, contre moins de 10⁻⁷ relatif pour les cas maintenus testés. Cet indicateur est exporté dans `projection.staticError` ; il ne mesure ni la convergence du maillage ni la précision dynamique au-delà des modes.


## 12. Résolution et cache 1.3 / Solve and cache

Le système réduit s’écrit D = D₀ − A C_f Aᵀ : D₀ est diagonal (structure sèche et bouche), A regroupe les couplages de structure et d’ouverture. L’identité de Woodbury ramène la résolution dense à C_f⁻¹ − AᵀD₀⁻¹A, de dimension égale au nombre de modes de cavité. C’est une transformation algébrique du même système, vérifiée contre sa résolution dense. Elle ne supprime aucun mode ou couplage retenu. Le cas sans air utilise directement les dénominateurs diagonaux.

Les réponses et banques de notes sont protégées par un verrou par modèle. Une banque dépend des paramètres physiques, du contact observé, des cordes actives et de l’échantillonnage. Les matrices d’assemblage et bases intermédiaires sont libérées après export des modes ; les déformées nécessaires à l’affichage restent disponibles.

English: exact Woodbury reduction accelerates the same coupled FE system. Local wood directions follow the geometry warp before orthonormalisation. Per-note templates fix event ordering, with a 10 ms ending window. Finite-FFT transient and narrow-resonance convergence limitations remain; see AUDIT.md.
