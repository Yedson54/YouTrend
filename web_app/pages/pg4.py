import dash
from dash import dcc, html

dash.register_page(__name__, name='Documentation')

layout = html.Div([html.Br(),
    html.H1(
        "Description du modèle de durée sur les vidéos YouTube en tendance", 
        style={'color': '#6D071A', 'textAlign': 'center'}
    ), 
    dcc.Markdown(
    """
    # 
    # Introduction

    Dans cette etude, nous nous sommes donnés comme objectif de trouver un moyen simple et fiable qui  nous permette d'estimer la date -une probabilité en pratique-  pour laquelle une vidéo partagée sur YouTube serait potentiellement en tendance. 

    ## 1) Présentation du dataset

    Dans ce projet, nous avons utilisé  des modèles parametriques de durée afin d'estimer la probilité qu'une une vidéo YouTube publiée à une certaine date, puisse entrer tendance ultérieurement.
    Nous considérons un ensemble de plusieurs vidéos YouTube obtenues à partir de l'API Youtube que l'on stocke sur un dataframe. Chaque vidéo est représentée  par les différentes caractéristiques suivantes : sa durée, sa date de publication, sa catégorie, ect.
    Cependant pour pouvoir ajuster un modèle de durée sur cette base de données, nous avons fait  des hypothèses supplémentaires  afin que les données soient adaptées à l'ensemble des instances de modèle de durée que nous avons utilisé dans la partie de Building Model
    
    #### Hypothèse 1

    Nous supposons avoir suivi chaque vidéo depuis sa date de publication. Cette hypothèse est réaliste, car en effet dans le futur on pourrait bien sûr suivre n'importe quelle vidéo.
    L'intérêt de cette hypothèse est de limiter les problèmes de censure, et plus particulièrement ici, le problème de censure à gauche.
    Une ligne sera dite censurée à gauche si nous ne connaissons pas sa date de publication, et une ligne sera dite censuré à droite si pendant la période à laquelle on a suivi la vidéo correspondante, on n'a pas observé cette vidéo dans l'ensemble des vidéos en tendance sur toute la période d'étude et on ne sait pas cette vraie date. 
    
    #### Hypothèse 2:

    On prend une date de fin d'étude de sorte à avoir  quelques vidéos censurées à droite dans notre base de données, sinon on ne pourrait pas fitter nos instances de modèle sur notre dataframe. 
    
    ## 2) Présentation de l'approche des modèles de durée

    Les modèles de durée sont une  famille  d'approche  de la  modélisation statistique  et l'une de leur utilisation la plus répendue est la modélisation de la durée passée dans un état . 
    L'exemple typique est la modélisation de la durée de chomage  d'un individu. Il existe principalement trois grandessous familles  de modèle de durèe à savoir les modèles non paramétrique, les modèles semi-paramétriques et les paramétriques avec chacune ses avantages et ses limites. Cependant, indépendamment du type de modélisation utilisé, il n'est pas possible de passer sur les notations et l'hypothèse suivante:
    
    ### Hypothèse: 
    
    Le temps d'apparition de l'évènement, disons le temps auquel la personne trouve un emploi dans l'exemple type, sera modélisé comme une variable aléatoire positive, de fonction de répartition $F$ et souvent notée $T$.


    ## 3) Bulding model and choice

    Le modèle final est sélectioné de la façon suivante:

    * 1)Premièrement, on  fait une validation croisée avec le model Weibull puis on garde le modèle qui  minimise la Log-Vraisemblance. On fait de même pour les modèles LogNormal et LogLogistique.
    * 2)On prend comme modèle final, le meilleur entre tous les modèles.

    ## WEIBULL MODEL

    Ci-dessous, nous avons la paramétrisation de la fonction de hasard et la LogVraisemblance du modèle  pour le modèle de Weibbull.
    
    $$\\lambda(t)=\\alpha{t^{\\alpha-1}}\exp(x^{T}\\beta)$$

    $$l_{n}(x,\\alpha,\\beta)=\\prod_{i=1}^{n} {\\lambda(t_{i},x_{i})}^{\\delta_{i}}(S(t_{i},x_{i})^{1-\\delta_{i}})$$ 

    où $\\delta_{i}=0$  signifie que la donnée correspondante est censurée à droite et 1 sinon. La maximisation de la log-vraisemblance permet de trouver les valeurs optimales pour nos différents paramètres $\\alpha$, $\\beta$
    
    ### Interprétation des des paramètres dans le cas du model de Weibull

    #### Pour $\\alpha$:
    * 1) si $\\alpha >1$ alors il ya une dependance temporelle positive c'est à dire que plus la date de publication est loin , moins une video à la chance d'entré en tendance à date donnée
    * 2) si $\\alpha=1$ alors il n'a aucune dependance temporelle c'est à dire que la probabilité d'entrée en tendance est constante au cours du temps
    * 3) si $\\alpha <0$ alors il ya une dependance négative
    
    ####  Pour $\\beta$:
    Dans les modèles paramétriques les coefficients devants les covariables captures l'effet de la des covariates sur la probabilité de survie
    Pour une variable continue, comme le durée de la vidéo, le paramètre correspond s'interprète comme suit : une hausse d'une unité de $x_{i}$ augmente la probabilité d'entrer en tendance de $(\\exp(\\beta_{i})-1)$
    
    ## 4) Sortie finale et Interprétation 
    
    ### 4.1) L'évolution de la probabilité de survie d'une vidéo publiée sur YouTube
    
    #### Fonction de survie croissante:
    
    Plus la date de publication est ancienne moins la vidéo a une chance d'entrer en tendance à une date donnée.""", mathjax=True),
    html.Img(src=r"assets/plot2moins_s.png", alt='image'),
    dcc.Markdown(
    """
    #### Fonction de survie décroissante:
    Plus la date de publication est ancienne plus la video a une chance d'entrer  en tendance à une date donnée."""),
    html.Img(src=r"assets/plot1moins_s.png"),
    dcc.Markdown(
    """

    #### Fonction de survie multiforme:"""),
    html.Img(src=r"assets/plot3.png"),
    dcc.Markdown(
    """
    ### 4.2) Evolutions globales de la fonction de survie de "l'ensemble" des vidéos YouTube selon le jours de la semaine et les catégories des vidéos
    
    #### Cas simple: évolution distinctive dans le temps
    Interprétation rapide : Pour publier une video dans la categorie Sports, il est préférable de le faire un dimanche plutot qu'un lundi, le lundi est, ici le jour avec la courbe toujours en dessus."""),
    html.Img(src=r"assets/plot_ecart1.png"),
    dcc.Markdown(
    """

    #### Cas plus compliqué

    Pour que votre vidéo soit en tendance à entre sa date de publication et 10 jours après, choisissez de la publier un lundi sinon publier un Dimanche
    Règle générale : selon la date à laquelle vous souhaitez que votre video soit en tendance , toujours choisir la jour pour lequel la courbe de
    survie retournée par cette fonction est en dessous des autres courbes pour les autres jours de la semaine et pour la même catégorie."""),
    html.Img(src=r"assets/plot_ecartx.png"),
    dcc.Markdown(
    """
    ### 5) Mathématiques

    #### Notations et définitions
    On note généralement par $t$ la variable réelle positive qui mesure une durée

    #### Fonction de surive : $S$
    $S(t)= P (T<t)=1-F(t)$.

    $S(t)$ est la probalité pour qu'une vidéo ne soit jamais rentré en tendance pendant $t$ jours depuis sa premiere publication
    
    #### Taux de Hasard : $\\lambda$
    $$\\lambda(t)=\\lim_{{dt \\to 0}} \\frac{P(t<=T<t+df|T>=t)}{dt}$$
    $\\lambda(t)$ est la probabilité qu'une vidéo qui n'a jamais été en tendance, entre en tendance.
    
    #### Fonction de hasard cumulative
    
    $$I(t)= \\int_{0}^{t} \\lambda(u)\\,du$$.

    Par souci de simplication et par souci de se conformer avec ce qui se fait en pratique, nous avons opté de n'utiliser dans la modélisation que les modèles paramétriques. Cependant afin d'avoir une vision globale de la probabilité de survie sur l'ensemble de notre dataset d'étude, nous avons,au début de notre étude , commencé par implémenter le modèle de KAPLAN MEIER, qui est l'un des modèles non-paramétriques les plus utilisés dans la pratique.
    
    #### Relation entre S et $\lambda$:
    On montre et on a:
    $S(t) =\\exp(\\int_{0}^{t} \\lambda(u)\\,du)$

    $\\lambda(t)=\\frac{-S^{'}(t)}{S(t)}$

    Ainsi donc, en connaissant $\\lambda(t)$ pour chaque valeur , on peut retrouver la vraie spécification $F$ et inversement aussi $S(t)$ détermine entièrement $\\lambda(t)$.

    La fome générale des modèles paramétriques s'écrit commme suit :
    $\\lambda(t)={\\lambda}_{0}(t)\\phi(x)$ où le plus souvent on prend $\\phi(x)=\\exp(x^{'}\\beta)$
    $x$ est le vecteur des covariables et $\\beta$ est un paramètre à estimer par maximisation de la vraisemblance du modèle.
    """, mathjax=True
)])