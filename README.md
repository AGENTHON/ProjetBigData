# ProjetBigData

Objectif :
----------
Dans ce projet nous effectuons la prédiction d’un métier à partir des extraits des CVs. Nous avons en total 28 métiers et 217197 personnes pour lesquelles nous souhaitons prédire le métier qui correspond à leurs profiles.
   
Il s’agit d’un projet de **classification des textes multi-classes**, et pour lequel nous avons utilisé les techniques de **traitement automatique de la langue - NLP**.

Données & Stockage :
--------------------
En termes de données, nous avons :

  -	Le fichier [**“data.json“**](https://github.com/AGENTHON/ProjetBigData/blob/main/processing/data.json) : ce fichier contient l’id de la personne pour laquelle nous souhaitons prédire le poste et des phrases en anglais extraites du CV de la personne en question, et enfin le genre de la personne.

  -	 Le fichier [**“label.csv“**](https://github.com/AGENTHON/ProjetBigData/blob/main/processing/label.csv) : faire la correspondance entre l’id d’un individu et l’id de son poste.
  
  -	Le fichier [**“categories_string.csv“**](https://github.com/AGENTHON/ProjetBigData/blob/main/processing/categories_string.csv) : donne pour chaque id le label du poste correspondant.

Pour mieux gérer le stockage de nos données, nous avons utilisé le système de stockage **HDFS**. Nos données étaient stockées sur une machine **Hadoop**.
Ensuite, ces données sont transférées sur le **cloud** pour le traitement final et la production d’un fichier CSV qui sera stocké sur une base de données **NoSQL** de type **MongoDB**.


Transfert de données Local <--> HDFS:
-------------------------------------
Dans un premier temps, les données sont envoyées sur une machine virtuelle Hadoop. Cette tâche est assuré par le script [**“data_transfer_hadoop.bat“**](https://github.com/AGENTHON/ProjetBigData/blob/main/Script%20Hdfs/data_transfer_hadoop.bat) qui transfère les fichiers des données et les scripts de traitement HDFS vers la VM Hadoop. Les scripts de traitement HDFS sont dans le répertoire [**“transfer_hadoop_fs“**](https://github.com/AGENTHON/ProjetBigData/tree/main/Script%20Hdfs/transfer_hadoop_fs), ils ont pour rôle l’envoie des fichiers de données de la VM Hadoop vers HDFS.

Ensuite, les 3 scripts qui sont dans le répertoire [**“hdfs_to_local“**](https://github.com/AGENTHON/ProjetBigData/tree/main/Script%20Hdfs/hdfs_to_local) sont exécutés pour récupérer les fichiers des données du HDFS vers la VM Hadoop. Enfin, ces données sont transférées de la VM Hadoop vers la machine Windows locale à l’aide du script [**“data_transfer_local.bat“**](https://github.com/AGENTHON/ProjetBigData/blob/main/Script%20Hdfs/data_transfer_local.bat)


Transfert de données Local <--> AWS :
-----
Le script [**“initEc2Instance.py“**](https://github.com/AGENTHON/ProjetBigData/blob/main/aws/initEc2Instance.py) permet de :
	
   - Créer une instance EC2
	
   - Se connecter à l’instance
	
   - Installer python3 et les différentes librairies nécessaires pour l’exécution de notre script de traitment [**“trainingTFIDF.py“**](https://github.com/AGENTHON/ProjetBigData/blob/main/trainingTFIDF.py)
	
   - Envoyer les fichiers des données et les scripts de traitement sur l’instance
   
   - Récupérer le fichier des résultats [**“predict.csv“**](https://github.com/AGENTHON/ProjetBigData/blob/main/result/predict.csv) sur la machine locale.

Le script [**“predict_to_mongodb.sh“**](https://github.com/AGENTHON/ProjetBigData/blob/main/predict_to_mongodb.sh) permet d'importer les données de prédiction depuis le fichier [**“predict.csv“**](https://github.com/AGENTHON/ProjetBigData/blob/main/processing/predict.csv) vers la base MongoDB

Traitement :
------------
Le traitement des données est fait par le script [**“trainingTFIDF.py“**](https://github.com/AGENTHON/ProjetBigData/blob/main/trainingTFIDF.py) qui s’exécute sur une instance EC2.
Avant de commencer l’entrainement de notre modèle, ce script fait le prétraitement des extraits des CVs. Ce prétraitement consiste à transformer toutes les lettres en minuscules et à supprimer la ponctuation et les mots non essentiels à la prédiction. Ensuite transformer les mots, jugés comme nécessaires à la classification, pour ne garder que la forme neutre canonique.

Après la phase de prétraitement, le script sépare les données en des données de test et des données d’entrainement. Ensuite, Les textes sont transformés à des vecteurs en limitant la taille à 10000 vecteurs.

Finalement, le script entraine l’algorithme **SVM** pour classer nos données, des tests et des mesures sont ensuite effectués pour mesurer l’efficacité de notre algorithme.

Les différentes fonctions utilisées dans le script [**“trainingTFIDF.py“**](https://github.com/AGENTHON/ProjetBigData/blob/main/trainingTFIDF.py) sont définies dans le script [**“utils.py“**](https://github.com/AGENTHON/ProjetBigData/blob/main/utils.py).
