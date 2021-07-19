import matplotlib.pyplot as plt

def non_dom_sort(pop, fit_types):
    """This function performs the non-dominated sorting operator of the NSGA-II
    algorithm. It assigns each individual in the population a Pareto front level,
    according to their fitness values.

    Parameters:
        pop (list): the population with all fitness values.
    """
    domination_count = {}
    dominated_set = []
    dominating_individuals = []
    pareto_front_indices = []
    pareto_front_individuals = []
    num_pop = len(pop)
    num_fit_func = len(pop[0])


    for i in range(num_pop):
        domination_count[i] = 0

        for k in range(num_pop):
            if i == k:
                continue
            count_sup = 0
            count_inf = 0
            for j in range(num_fit_func):
                if fit_types[j] == 'min':
                    if pop[i][j] < pop[k][j]:
                        count_sup += 1
                    elif pop[i][j] > pop[k][j]:
                        count_inf += 1
                elif fit_types[j] == 'max':
                    if pop[i][j] > pop[k][j]:
                        count_sup += 1
                    elif pop[i][j] < pop[k][j]:
                        count_inf += 1

            if count_sup < 1 and count_inf >= 1:
                domination_count[i] += 1

            elif count_sup >= 1 and count_inf < 1:
                dominated_set.append(k)
                dominating_individuals.append(i)

    pareto_front_number = 0
    pareto_front_indices.append(0)
    while len(pareto_front_individuals) < num_pop:
        index_count = 0
        for i in range(num_pop):
            if domination_count[i] == 0:
                pareto_front_individuals.append(i)
                domination_count[i] -= 1
                index_count += 1

        indx = index_count + pareto_front_indices[pareto_front_number]
        pareto_front_indices.append(indx)

        a  = pareto_front_indices[pareto_front_number]
        b  = pareto_front_indices[pareto_front_number + 1]

        for k in range(a, b):
            for h in range(len(dominating_individuals)):
                if pareto_front_individuals[k] == dominating_individuals[h]:
                    if domination_count[dominated_set[h]] >= 0:
                        domination_count[dominated_set[h]] = domination_count[dominated_set[h]] - 1

        pareto_front_number += 1
    
    pf = []
    for i in range(len(pareto_front_indices) - 1):
        pf.append(pareto_front_individuals[pareto_front_indices[i]:pareto_front_indices[i+1]])

    return pf

def find_in_front(individual, pf):
    for i, l  in enumerate(pf):
        if individual in l:
            return i

def plot_pf(pop, pf, fit_indices=[0, 1]):
    dot = ['r', 'b', 'k']
    size = [80, 80, 80]
    
    for i, x in enumerate(pop):
        f1, f2 = x[fit_indices[0]], x[fit_indices[1]]
        pf_index =  find_in_front(i, pf)
        if pf_index > 2:
            pf_index = 2
        plt.scatter(f1, f2, s=size[pf_index], c=dot[pf_index], edgecolors='k')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    pop = [[1, 0, 3], [10, 1, 4], [2, 2, 3], [3,3, 2], [0,1, 8], [11,2, 10], [0,1, 11]]
    fit_types = ['max', 'min', 'max']
    pf = non_dom_sort(pop, fit_types)
    print(pf)
    plot_pf(pop, pf, fit_indices=[0,1])