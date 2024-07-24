Avant de lancer le projet, veuillez activer l'environnement python avec la commande :
source venv/bin/activate
puis éxécuter le code avec :
python wumpus.py

Fonctionnement de l'IA :
    - Au lancement de la partie, on génère les règles du jeu sous forme de clause logique
    - À chaque case parcourue, on ajoute une clause dans notre formule SAT en fonction de l'observation
    - Pour trouver le mouvement le plus optimal à faire pour ne pas mourir, pour chaque case autour de notre
    joueur, on pose une clause de monstre sur cette même case, puis on essaye de trouver une solution à notre formule SAT avec
    cette nouvelle clause. Si c'est satisfiable, cela veut dire qu'il y a une chance d'avoir la présence d'un monstre (ou d'un trou)
    sur cette case. Si c'est UNSAT, cela veut dire qu'il n'y a aucune chance d'avoir un monstre ou un trou sur cette case,
    on peut donc s'y déplacer.
    - Il se pourrait qu'au bout d'un moment, notre IA se retrouve bloqué, car elle ne prend pas assez de risque ( par exemple, elle
    reste bloquée entre plusieurs cases d'odeur). Pour contrer cela, à partir d'un certain temps (steps = 600), notre joueur prendra
    des risques. Pour détecter si une case à proximité d'une case d'odeur à moins de chance d'être une case de monstre ou de trou,
    alors on regarde les observations faites autour de cette même case, si on a qu'une seule case d'odeur (ou de vent), 
    on prend le risque de s'y déplacer en l'ajoutant dans notre tableau de possibleMoves.
    Théoriquement, notre joueur peut mourir uniquement après le step 800.

Problématiques rencontrées :
    - À chaque itération, lorsque j'ajoute une clause de monstre aux cases à proximités, je dois les supprimer juste après.
    Je n'ai pas trouvé de solution dans la documentation pour supprimer la dernière clause ajoutée, alors je supprime mon
    solver puis je le recrée après avec la fonction testSolver.
    - J'ai également rencontré des problèmes pour utiliser le pysat classique du TD1 lors de mes addClauses, alors j'ai utilisé
    la librairie pysat avec le solver Glucose3. Ça fonctionne avec cela, j'ai donc gardé celui-ci.