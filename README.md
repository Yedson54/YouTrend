# YouTrend

### Descriptif des colonnes

- **videoTitle**: titre de la vidéo
- **videoId**: identifiant de la vidéo
- **videoThumbnailUrl**: lien qui renvoie vers la miniature de la vidéo
- **videoDescriptionSnippet**: description (coupée à ~ 200 caractères) de la vidéo. NaN pour les Shorts et pour les vidéos sans description (**videoVerboseDescription** est la même mais n'est pas coupée)
- **videoRelativePublishedTimeText**: date de publication relative (au moment où l'on scrappe)
- **videoLength**: longueur de la video au format (heure:minutes:secondes). NaN pour les Shorts (regarder plutot **videoLengthSeconds**)
- **videoViewCountText**: nombre de vues d'une vidéo. Pour les Shorts, le nombre de vues n'est pas exact (regarder plutot **exactViewNumber**)
- **videoCreatorName**: nom du createur de contenus. Pour les Shorts c'est NaN (#TODO recuperer les noms des createurs pour les Shorts)
- **videoType**: type de la vidéo; s'applique uniquement aux vidéos en tendance. Peut être "Now" (en tendances maintenant) "Recently Trending" (était en tendances), "Music", "Gaming", "Movies"
- **trendingCountry**: code du Pays dans laquelle la vidéo est en tendance
- **exactViewNumber**: nombre de vues exactes
- **numberLikes**: nombre de likes. Si le créateur ne souhaite pas avoir de like, la **numberLikes** prend la valeur _Like_
- **videoDate**: date (mois, jour, année) de publication de la vidéo, avec quelques variations pour les musiques et les videos (_Premiered, Streamed live_ on...)
- **creatorSubscriberNumber**: nombre d'inscriptions à la chaine du créateur de la vidéo
- **videoVerboseDescription**: description de la vidéo. NaN pour les vidéos sans description
- **numberOfComments**: nombre de commentaire sous la vidéo. NaN si il n'est pas possible d'écrire des commentaires
- **isCreatorVerified**: True si le créateur a été vérifié par YouTube
- **videoKeywords**: liste des mots-clés renseignés par le créateur et concernant la vidéo
- **videoLengthSeconds**: longueur de la vidéo en secondes
- **videoIsLiveContent**: True si la vidéo est un live
- **videoCategory**: catégorie de la vidéo, probablement renseignée automatiquement par Youtube?
- **isFamilySafe**: True si la vidéo est adaptée aux familles
- **videoExactPublishDate**: date exacte de la publication de la vidéo, avec les informations sur l'heure, la minute et la seconde de publication
- **creatorUrl**: lien avec l'identifiant unique du créateur de la vidéo
