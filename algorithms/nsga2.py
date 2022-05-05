
from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.operator import BitFlipMutation, SPXCrossover, BinaryTournamentSelection
from jmetal.util.termination_criterion import StoppingByEvaluations
from jmetal.util.solution import print_function_values_to_file, print_variables_to_file
from jmetal.lab.visualization.plotting import Plot
from jmetal.util.solution import get_non_dominated_solutions


from partitioningProblem import *
from loadData import *
if __name__ == '__main__':

    problem = RegionalIntegrationProblem(gdp, gdpCompo, dfExports, G)

    algorithm = NSGAII(
        problem=problem,
        population_size=1000,
        offspring_population_size=1000,
        mutation=BitFlipMutation(1.0 / len(borderingCountryNames)),
        crossover=SPXCrossover(0.8),
        selection=BinaryTournamentSelection(),
        termination_criterion=StoppingByEvaluations(max_evaluations=1000000)
    )

    algorithm.run()
    front = algorithm.get_result()

    # Save results to file
    print_function_values_to_file(front, 'FUN.' + algorithm.label)
    print_variables_to_file(front, 'VAR.'+ algorithm.label)

    print(f'Algorithm: ${algorithm.get_name()}')
    print(f'Problem: ${problem.get_name()}')
    print(f'Computing time: ${algorithm.total_computing_time}')

    plot_front = Plot(title='Pareto front approximation', axis_labels=['Mean Regional Integration', 'Mean(Max Diff GDP Composition)'])
    plot_front.plot(front, label='NSGAII (100*100) (Mean MeanMaxDiff)')