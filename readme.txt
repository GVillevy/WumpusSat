# Before starting the project, please activate the python environment with the command:

```sh
source venv/bin/activate
then execute the script with :
python wumpus.py

# How the AI works
    - When the game is started, the rules of the game are generated as a logical clause
    - For each box that is scanned, a clause is added to our SAT form based on the observation
    - To find the most optimal movement to not die, for each box around our
    player, we put a monster clause on this same box, then we try to find a solution to our SAT formula with
    this new clause. If it is satisfactory, it means that there is a chance of having the presence of a monster (or hole)
    on this box. If it’s UNSAT, that means there’s no chance of a monster or a hole in this box,
    So we can move there.
    - It could happen that after a while, our AI is stuck because it doesn’t take enough risk (for example, it stays stuck between several hole boxes). 
    To counter this, from a certain time (steps = 800), our player will take risks. 
    To detect if a box near a smell box is less likely to be a monster or hole box, then we look at the observations made around this same box, 
    if we have only one box of smell (or wind), we take the risk of moving it in our table of possible moves. 
    Theoretically, our player can die only after step 800.
