# EDT_Scrapper
Projet pour récupérer les emplois du temps depuis l'application de Zuchetti

Chaque fichier correspond à une étape du processus :
  - Récupération des données à l'aide de selenium
  - Traitement des données a l'aide de la bibliothèque Python Beautiful Soup
  - Utilisation de l'API google pour ajouter toutes les données à agenda google

Il est trés difficile de scrpper les données de façon fiable et explitable car l'application de Zuchetti sépare
complétement la mise ne page des informations et les informations elle même. Cela impliquait de compter les pixels
et le moindre changement de taille de fenêtre ou autre entrainait des erreurs.
