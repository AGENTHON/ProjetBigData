# ProjetBigData

   Dans ce projet nous effectuons la prédiction d’un métier à partir des extraits des CVs. Nous avons en total 28 métiers et 217197 personnes pour lesquelles nous souhaitons prédire le métier qui correspond à leurs profiles.
   
Il s’agit d’un projet de classification des textes multi-classes, et pour lequel nous avons utilisé les techniques de traitement automatique de la langue - NLP.

Pour mieux gérer le stockage de nos données, nous avons utilisé le système de stockage HDFS. Nos données étaient stockées sur une machine Hadoop.
Ensuite, ces données sont transférées sur le cloud pour le traitement final et la production d’un fichier CSV qui sera stocké sur une base de données NoSQL de type MongoDB.

Le traitement des données est fait par un script python qui s’exécute sur une instance EC2.

En termes de données, nous avons :

  -	Le fichier “data.json“ : ce fichier contient l’id de la personne pour laquelle nous souhaitons prédire le poste et des phrases en anglais extraites du CV de la personne en question, et enfin le genre de la personne.

  -	 Le fichier “labes.csv“ : faire la correspondance entre l’id d’un individu et l’id de son poste.

  -	Le fichier “categories_string.csv“ : donne pour chaque id le label du poste correspondant.
