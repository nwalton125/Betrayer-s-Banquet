import random

#I'm far from sure this is correct. I did put in a test at the bottom to make sure the total score is correct, and it is! That's a good sign, but there could be other bugs.

class Player:
    def __init__(self, strategy_name, seat = 0, score = 0, history = []):
        self.seat = seat
        self.score = score #Based on the type of food you get. Players get n points for eating at the nth seat of the table. Lower scores are better.
        self.strategy = getattr(self, strategy_name)
        self.history = history #History of defections and cooperations for both the player and their opponents, not keeping track of opponent identities.

    def track_hist(self, new_item):
        self.history.append(new_item)

    #Finds the proportion of the player's history which is "C".
    def recent_c_prop(self):
        if self.history == []:
            return 1 #Basically, if nothing has occurred yet, we assume the player is benevolent.
        else:
            last_10 = self.history[-10:]
            return len(list(filter(lambda x: x == "C", last_10))) / 10

    def all_d(self, opp):
        return "D"

    def all_c(self, opp):
        return "C"

    def alternator(self, opp):
        if len(self.history)%2 == 0:
            return "C"
        else:
            return "D"

    #Tit For Tat, though it's weirder here than in iterated Prisoner's Dilemma, since you're not necessarily playing the same opponent repeatedly.
    def tft(self, opp):
        if len(self.history) == 0:
            return "C"
        return self.history[-1][1]

    #Tit For Two Tats.
    def tftt(self, opp):
        if len(self.history) < 2:
            return "C"
        elif self.history[-1][1] == "D" and self.history[-2][1] == "D":
            return "D"
        else:
            return "C"

    #Cooperates before anyone has defected against it, then never again.
    def grudger(self, opp):
        for i in self.history:
            if i[1] == "D":
                return "D"
        return "C"

    #Randomly cooperates or defects.
    def rando(self, opp):
        if random.random() < .5:
            return "C"
        else:
            return "D"

    #The commenseur cooperates with probability equal to the proportion of "C"'s in the opponent's history.
    def commenseur(self, opp):
        if random.random() < opp.recent_c_prop():
            return "C"
        else:
            return "D"

    def move(self, opp = None):
        return self.strategy(opp)

class Position:
    #'players' is a list of player objects ordered by seating.
    def __init__(self, players):
        if len(players) % 2 != 0:
            raise ValueError("Number of players must be even.")
        self.sides = [players[:len(players)//2], players[len(players)//2:]]
        self.length = len(self.sides[0])
        for i in range(self.length):
            self.sides[0][i].seat = i
            self.sides[1][i].seat = i

    def iterate(self):
        #First, the players eat...
        for i in range(self.length):
            self.sides[0][i].score += i
            self.sides[1][i].score += i

        #Then, they play...
        new_places1 = []
        new_places2 = []
        for i in range(self.length):
            outcome = (self.sides[0][i].move(self.sides[1][i]), self.sides[1][i].move(self.sides[0][i]))
            if outcome == ("C", "C"):
                new_places1.append((i-3,i))
                self.sides[0][i].track_hist(("C", "C"))
                new_places2.append((i-3,i))
                self.sides[1][i].track_hist(("C", "C"))
            elif outcome == ("C", "D"):
                new_places1.append((i+10,i))
                self.sides[0][i].track_hist(("C", "D"))
                new_places2.append((i-10,i))
                self.sides[1][i].track_hist(("D", "C"))
            elif outcome == ("D", "C"):
                new_places1.append((i-10,i))
                self.sides[0][i].track_hist(("D", "C"))
                new_places2.append((i+10,i))
                self.sides[1][i].track_hist(("C", "D"))
            else:
                new_places1.append((i+5,i))
                self.sides[0][i].track_hist(("D", "D"))
                new_places2.append((i+5,i))
                self.sides[1][i].track_hist(("D", "D"))

        #And rearrange.
        new_places1, new_places2 = sorted(new_places1), sorted(new_places2) #Note that if there is a tie (i.e. people previously at seats 3 and 16 would both sit at seat 13), the player who previously sat higher takes the higher seat (in this case, the player at seat 3 before would take 13 now, and previous 16 would take 14).
        new_side1 = [self.sides[0][new_places1[i][1]] for i in range(self.length)]
        new_side2 = [self.sides[1][new_places2[i][1]] for i in range(self.length)]
        self.sides[0], self.sides[1] = new_side1, new_side2

    def simulate(self, its):
        for _ in range(its):
            self.iterate()

    #Gives total points in the game so far for each strategy played.
    def strat_report(self):
        pts_dict = {}
        for i in range(self.length):
            for j in [0,1]:
                s = self.sides[j][i].strategy.__name__
                if s not in pts_dict:
                    pts_dict[s] = 0
                pts_dict[s] += self.sides[j][i].score
        return pts_dict


#Strategies.

#Function for combining two dictionaries with numbers as entries, combining elements that are in both rather than overwriting.
def add_dicts(d1, d2):
    new_d = {}
    for k1 in d1:
        new_d[k1] = d1[k1]
    for k2 in d2:
        if k2 in d1:
            new_d[k2] += d2[k2]
        else:
            new_d[k2] = d2[k2]
    return new_d

simuls = 100
strats = ["all_d", "all_c", "tft", "tftt", "grudger", "rando", "commenseur"]
strat_freq = 10 #The number of players who play any given strategy at the table (identical for each strategy).
its_per_simul = 100

def triang(n):
    return n*(n+1)//2

#To check our work at the end -- this should be the total number of points scored among strategies by the end.
total_pts_checksum = simuls * its_per_simul * triang(strat_freq*len(strats)//2 - 1)*2


aggregated_results = {}
for _ in range(simuls):
    players = []
    for _ in range(strat_freq):
        for strat in strats:
            p = Player(strat)
            players.append(p)
    random.shuffle(players)
    pos = Position(players)
    pos.simulate(its_per_simul)
    aggregated_results = add_dicts(aggregated_results, pos.strat_report())
print(aggregated_results)
print(sum([aggregated_results[k] for k in aggregated_results]) == total_pts_checksum)
