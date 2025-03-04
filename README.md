# CAMEO MTCE: Maintien et fonctionnement du module d'alarme Python ITX-TAG Ganging

## Contexte
Le module d'alarme est conçu pour surveiller les horaires de Gang des canaux ITX via la page web du Ganging Web UI (accédée avec ChromeDriver) et pour modifier la couleur d'un PIP (Picture-in-Picture) dans un multiviewer TAG via son API en fonction des canaux présents dans la page web. Le code est compilé en un fichier exécutable (.exe) avec PyInstaller et roule sur une VM Windows dédiée, mais le code source reste accessible également.

Le script est déployé sur une VM nommée **MTLPREPVUMUTY101 (10.172.233.29)**. L'exécutable est présentement dans `C:\ITX_Gang_Tag_Multi_PIP`, avec un raccourci sur le bureau.

### Dépendances nécessaires :
- **List.xml** comportant les informations nécessaires à l'exécution.
- **chromedriver.exe** avec la même version que Google Chrome dans `chromedriver_64` (même répertoire que l'exécutable).
  - Alternativement, en supprimant le path dans le code d'origine, la bonne version de ChromeDriver peut aussi être placée dans `C:\Users\<username>\.cache\selenium\<chrome_version_number>`.
- **Google Chrome** avec une version compatible avec `chromedriver.exe`.

Les différentes versions de Chrome et ChromeDriver sont disponibles via le fichier JSON dans le dossier racine du programme.

Le script `keepIT Gangsta config.py` sur le bureau permet de configurer les PIP associés aux points de contrôle.

---

## Résumé du Flux Principal
1. Le programme démarre en initialisant les dictionnaires et les pages Chrome.
2. Il entre ensuite dans une boucle infinie où il scanne les canaux dans chaque point de contrôle.
3. Si un canal est détecté ou retiré d'un point de contrôle, il envoie une requête PUT pour mettre à jour la couleur du canal dans l'API.
4. Il surveille également les canaux jumeaux et modifie la couleur en conséquence.
5. En cas d'erreur, le programme se termine en journalisant l'erreur.

---

## Résumé des classes, fonctions et boucles
Ces structures de données sont essentielles au bon fonctionnement du module.

### **Classe `ChannelHashMap`**
- Gère les états d'alarme pour chaque canal en fonction des points de contrôle.
- Utilise un dictionnaire pour stocker les états (True ou False) de chaque canal pour chaque point de contrôle.

### **Fonctions principales**
- `terminate_chromedriver()`: Termine les instances de ChromeDriver encore en cours d'exécution pour éviter les conflits.
- `init_chrome_drivers(channel)`: Ouvre une page web via ChromeDriver pour surveiller les canaux d'un point de contrôle spécifique.
- `get_channel_list(driver)`: Récupère la liste des canaux actifs dans le point de contrôle associé à un ChromeDriver.
- `get_tag_api(url)`: Récupère les configurations actuelles d'un PIP via l'API.
- `put_tag_api(json_data, color)`: Modifie la couleur de bordure du PIP en fonction de l'état de l'alarme détectée.

### **Boucle principale**
- Le script fonctionne en boucle, vérifiant régulièrement les états des canaux.
- Lorsqu'un canal apparaît ou disparaît d'un point de contrôle, il modifie la couleur du PIP associé via l'API.
- Si un canal est présent dans plusieurs points de contrôle, une alarme de couleur **Yellow** est déclenchée.

### **Journalisation**
- Toutes les actions significatives, erreurs et états sont enregistrés dans un fichier log avec horodatage.
- Cela permet un suivi et un débogage efficace.

---

## Surveillance et anticipation des problèmes futurs
### **Surveillance des processus ChromeDriver**
- Assurez-vous que les instances de `chromedriver.exe` sont bien terminées après chaque exécution.
- Des processus ChromeDriver en excès peuvent entraîner des conflits ou des fuites de mémoire.

### **Surveillance des fichiers logs**
- Vérifiez régulièrement les logs pour identifier les anomalies ou erreurs récurrentes.
- Une surabondance de logs peut indiquer un problème sous-jacent.

### **Mises à jour de ChromeDriver**
- Le module dépend de ChromeDriver pour accéder aux pages web.
- Assurez-vous que la version de ChromeDriver est compatible avec la version de Chrome installée.
- Une page web est accessible pour obtenir toutes les versions de ChromeDriver compatibles.

### **Vérification de l'accès réseau**
- Ce module interagit avec l'API TAG et ITX Main.
- Assurez-vous que l'accès réseau vers ces ressources est toujours opérationnel.

---

## Bonnes pratiques pour le maintien
### **Surveillance des ressources**
- Vérifiez régulièrement l'utilisation de la mémoire et du CPU par l'exécutable.
- Une utilisation excessive peut indiquer des processus ChromeDriver non fermés correctement.

### **Gestion des erreurs**
- Surveillez les erreurs fréquentes dans les logs, surtout celles qui provoquent un crash.
- Le script est résistant aux erreurs mineures d'obtention du contenu de la page web.

### **Planification des vérifications**
- Planifiez des vérifications régulières de l'état des services et des dépendances externes.

### **Gestion des mots de passe**
- Les mots de passe sont récupérés depuis des variables d'environnement.
- Assurez-vous qu'ils sont mis à jour si des modifications ont lieu.

### **Archivage des logs**
- Une rotation des logs est effectuée via `Scheduled Tasks` et un fichier `.bat`.
- Une rétention de 30 jours est appliquée.

### **Redémarrage hebdomadaire**
- Bien que le programme puisse tourner plusieurs semaines, un redémarrage est recommandé pour éviter les déconnexions.

---

## Recommandation
Une surveillance proactive et des mises à jour régulières des composants externes sont essentielles pour garantir un fonctionnement stable et sans interruptions.

