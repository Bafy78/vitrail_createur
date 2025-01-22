# R506 : Chef d’Oeuvre

## Générateur de “Vitraux”

## **Description :** 

Ce projet est un programme Python permettant, à partir d’une image d’entrée, de générer un genre de vitrail.  
Il y a dans le fichier zip [des exemples](#5.-les-exemples-:) d’images d’entrées, avec leur résultat correspondant. (Les images d’entrée ne m’appartiennent pas toutes \!)  
Lorsqu’on lance le script *vitrail.py*, le cadre du vitrail va être créé, et va être rempli de polygones, créés aléatoirement avec l’algorithme de Voronoi ([https://en.wikipedia.org/wiki/Voronoi\_diagram](https://en.wikipedia.org/wiki/Voronoi_diagram)). Tout l’espace va être pris par ces polygones.   
Chaque polygone aura ensuite une couleur attribuée, qui correspond à la couleur moyenne dans la zone de l’image correspondante à la position du polygone. C’est une sorte de redimensionnement mais avec des “pixels” de taille et forme différentes.  
Ensuite, des effets sont ajoutés, pour rendre le résultat plus joli et intéressant, comme des ombres portées entre les polygones, un effet de “respiration” et de rotation, et un changement de teinte global cyclique.  
Le résultat est sous la forme d’un svg, non interactif, mais donc observable depuis n’importe quel navigateur, intégrable dans des pages web,...

## **Détails :**

#### **1\. Techniques informatiques employées**

* **Langage** : Le projet est développé en Python  
* **Bibliothèques utilisées** :  
  * *drawsvg* : Pour la génération d'éléments SVG et leur animation (transformations, couleurs).  
  * *Pillow* : Pour traiter l'image source et extraire les couleurs.  
  * *shapely* : Pour manipuler les polygones et gérer les calculs géométriques complexes.  
  * *scipy.spatial.Voronoi* : Pour générer le diagramme de Voronoi, structurant l’espace en polygones.  
  * *colorsys*, pour faire de la conversion hsl \<-\> rgb  
  * Des bibliothèques auxiliaires comme *numpy, math, ou random*

---

#### **2\. Techniques propres au multimédia ou à l'animation**

* **Couleurs dynamiques** :  
  * Chaque polygone du vitrail est coloré en fonction de la couleur moyenne de la région correspondante (via la position) de l’image source.  
  * Une animation de variation cyclique de la teinte de tous les polygones est ajoutée pour un effet visuel captivant.

* **Respiration des polygones** :  
  * Certains polygones (probabilité contrôlée) sont animés pour grandir et rétrécir subtilement. Seulement certains polygones ont cette animation, dans un souci de performance.

* **Rotation dynamique** :  
  * En complément de l’animation de respiration, les polygones affectés ont une rotation légère appliquée lors du “détachement”, simulant un effet vivant et organique : on a l’impression qu’un coin du polygone a du mal à se détacher, et qu’on doit donc forcer.

* **Calques optimisés** :  
  * Les éléments statiques et animés sont séparés en deux calques pour améliorer les performances et permettre une meilleure gestion du rendu graphique. Les éléments animés passent au-dessus de ceux statiques, lorsqu’ils se déplacent.

* **Effets d’ombre portée** :  
  * Chaque polygone a une ombre projetée pour donner un effet de profondeur réaliste.

* **Structure géométrique** :  
  * Le cadre est arrondi sur le haut, avec des polygones parfaitement ajustés à l’intérieur grâce à une construction Voronoi optimisée. Il ressemble (probablement) à un cadre de vitrail

---

#### **3\. Limitations de la réalisation**

* **Performances graphiques** :  
  * Les fichiers SVG produits peuvent être lourds avec un grand nombre de polygones et d’animations simultanées.  
  * Le rendu peut être lent sur des machines ou des navigateurs moins puissants.

* **Entrées acceptées** :  
  * Une seule image source peut être utilisée comme base pour le vitrail.  
  * Les dimensions de l’image et du canvas sont fixes, bien que modulables dans le code. L’image d’entrée est redimensionnée pour rentrer dans le cadre, mais peut ne pas convenir si elle est bien plus large que haute par exemple.

* **Personnalisation limitée** :  
  * Des variables globales au début du script permettent de faire varier le nombre de polygones (pour simuler une plus haute résolution), la taille du canevas et du cadre, ainsi que l’amplitude et la probabilité (combien de polygones) de l’animation de respiration et de rotation.  
  * Le reste n’est pas vraiment paramétrable avec le code actuel.

* **Rendu du résultat :**  
  * Le résultat semble moins beau lorsqu’on utilise une image de plus haute résolution : soit on a peu de polygones et on ne distingue pas de détails, soit on augmente le nombre de polygones, mais l’effet n’est pas très joli. L’image d’entrée qui semble produire le meilleur effet est le pixel art.

* **Modification de l’image d’entrée à postériori :**  
  * L’image d’entrée “n’existe plus” après qu’on ait associé ses couleurs aux polygones. Il n’est donc pas possible de par exemple faire tourner l’image d’entrée après coup sans bouger le cadre ou les polygones, avec la façon dont c’est implémenté actuellement.  
  * Il n’est pas possible de mettre une image animée (style GIF) comme image d’entrée.

---

#### **4\. Tentatives d’améliorations ratées :** 

* J’ai tenté de pondérer la création de polygones en fonction d’un filtre *Emboss* et/ou d’un filtre d’*Edge Detection* appliqué sur l’image d’entrée, pour avoir plus de polygones aux endroits où ça avait un impact et moins aux endroits où les pixels d’entrée étaient semblables. Malheureusement, peut-être que mon implémentation n’était pas très bonne, mais le résultat n’était pas vraiment intéressant, ça n’apportait pas grand chose et était moins joli “artistiquement”.  
* J’ai voulu faire en sorte que lorsque les polygones passent au-dessus d’autres (via l’animation de “respiration”), ils soient un peu transparents pour qu’on voit quand même en partie la couleur du pixel derrière. Malheureusement je ne pense pas que ce soit possible avec les technologies que j’ai utilisé :   
  le SVG ne permet pas de manipuler dynamiquement la géométrie d’un polygone pour séparer automatiquement la zone qui chevauche un autre polygone (transparente) de celle qui ne chevauche rien (opaque). Les modes de fusion (*mix-blend-mode*) ou les masques agissent globalement sur tout le polygone ou tout le calque, mais ne peuvent pas cibler uniquement la zone d’intersection (et donc le polygone est transparent “avec le fond” également). Pour obtenir cet effet précis, il faudrait recalculer en continu les intersections entre polygones pendant l’animation, ce qui nécessite un script externe ou une technologie comme JavaScript, Canvas ou WebGL.

---

#### **5\. Les exemples :**  {#5.-les-exemples-:}

* ***skeleton*** : “petit” pixel art, rend bien avec 2000 polygones  
* ***elvish\_archer*** : un peu plus grand, nécessite plus de polygones (j’ai choisi 2500\)  
* ***orcish\_warlord*** : plus détaillé, 3000 polygones  
* ***pouler*** : image de plus haute résolution mais moins détaillée, rend très bien avec 2000 polygones  
* **The\_Elder** : image bien plus grande et détaillée : nécessite beaucoup de polygones pour voir les détails (5000) mais l’effet vitrail est bien moins attrayant

Crédits pour les images : 

* ***skeleton***, ***elvish\_archer***, et ***orcish\_warlord*** viennent du jeu Open-Source [Battle For Wesnoth](https://www.wesnoth.org/)  
* ***pouler*** est le logo de [mon serveur Minecraft](https://discord.gg/FqGKSqPBbk) (à partir d’une image de poulet [Minecraft](https://www.minecraft.net/en-us))  
* ***The\_Elder*** est une image du jeu [Path of Exile](https://www.pathofexile.com/)