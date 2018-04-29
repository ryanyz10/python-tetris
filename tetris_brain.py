from tetris import TetrisApp
from deap import base, creator, tools, algorithms
import numpy as np
from operator import attrgetter


if __name__ == "__main__":
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    def random_between(lo, hi):
        return np.random.random() * (hi - lo) + lo

    toolbox.register("weight", random_between, -1, 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.weight, n=4)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("mate", tools.cxBlend, alpha=0.4) # TODO change around alpha
    toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma=0.3, indpb=0.05) # TODO change around sigma, indpb
    toolbox.register("select", tools.selTournament, tournsize=5) # TODO change around tournsize

    # Define EA parameters
    n_gen = 10
    pop_size = 25
    prob_xover = 0.5
    prob_mut = 0.15

    pop = toolbox.population(n=pop_size)

    game = TetrisApp(training=True)

    # GA loop
    for g in range(1, n_gen + 1):
        print("On generation " + str(g))

        # simulate for each individual
        for ind in pop:
            print("ind:" + str(ind))
            score = game.run_brain(ind)
            print("score: " + str(score))
            ind.fitness.values = (score,)

        # by this point each ind.gitness.values should be the score

        # Create children
        offspring = map(toolbox.clone, toolbox.select(pop, len(pop)))
        offspring = algorithms.varAnd(offspring, toolbox, prob_xover, prob_mut)
        pop[:] = offspring

        # now print the best trained individual

    best = max(pop, key=attrgetter("fitness"))

    print("best individual found is: " + str(best))
