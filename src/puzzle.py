from random import choice
from copy import deepcopy
import timeit 
from frontier import Frontier


class Puzzle:
    goal_state = '012345678'
    
    def __init__(self, state):
        self.state = state

    @classmethod
    def from_stdin(cls):
        state = ''
        exist = [False for _ in range(9)]
        
        for i in range(1, 4):
            print('Enter 3 numbers for row', i, '(sepperate by blank-space): ')
            x = input().split(' ')
             
            if len(x) != 3:
                print('Each row must have 3 numbers')
                exit()

            if not x[0].isnumeric() or not x[1].isnumeric() or not x[2].isnumeric():
                print('Each element must be a number')
                exit()

            x0 = int(x[0])
            x1 = int(x[1])
            x2 = int(x[2])

            if not (0 <= x0 <= 8) or not (0 <= x1 <= 8) or not (0 <= x2 <= 8) \
                or exist[x0] or exist[x1] or exist[x2]:
                print('Numbers must between 0 and 8 and can not duplicate')
                exit()
    
            exist[x0] = exist[x1] = exist[x2] = True
            
            state += str(x0)
            state += str(x1)
            state += str(x2) 

        return cls(state)

    @classmethod
    def random(cls):
        solvable = False
        state = None

        while (not solvable):
            state = ''
            num_pool = [_ for _ in range(9)]
            for _ in range(9):
                num = choice(num_pool)
                state += str(num)
                num_pool.remove(num)
            solvable = Puzzle._solvable(state)
            
        return cls(state)
            
    @staticmethod
    def benchmark():
        f = open('dataset/200 Scrambled Puzzles.txt')

        # average run time and the number of cases you've tested with a specific length
        statistics = dict()  # depth: cases, avg_node_gen_h1, avg_node_gen_h2, avg_runtime
        depth = depth_cases = depth_node_gen_h1 = depth_node_gen_h2 = depth_runtume = 0

        for line in f:
            line = line.rstrip('\n')
            if not line.isdecimal():  # 'Depth x'
                if depth_cases != 0:
                    depth_node_gen_h1 //= depth_cases
                    depth_node_gen_h2 //= depth_cases
                    depth_runtume /= depth_cases

                    statistics[depth] = (depth_cases, depth_node_gen_h1, depth_node_gen_h2, depth_runtume)

                    depth_cases = depth_node_gen_h1 = depth_node_gen_h2 = depth_runtume = 0

                depth = line.split(' ')[1]
                print('Benchmarking on depth', depth, '/ 20')
            else:
                start = timeit.default_timer()
                depth_cases += 1

                puzzle1 = Puzzle(line)
                _, node_gen1, _ = puzzle1.solve(Puzzle._sum_misplaced_heuristic)
                depth_node_gen_h1 += node_gen1
                
                puzzle2 = Puzzle(line)
                _, node_gen2, _ = puzzle2.solve(Puzzle._manhattan_heuristic)
                depth_node_gen_h2 += node_gen2

                end = timeit.default_timer()

                depth_runtume += (end - start)

        depth_node_gen_h1 //= depth_cases
        depth_node_gen_h2 //= depth_cases
        depth_runtume /= depth_cases

        statistics[depth] = (depth_cases, depth_node_gen_h1, depth_node_gen_h2, depth_runtume)

        f.close()

        for d in range(2, 21, 2):
            print('--------------------------')
            print('Depth:', d)
            print('Test cases:', statistics[str(d)][0])
            print('Avg nodes generated of h1:', statistics[str(d)][1])
            print('Avg nodes generated of h2:', statistics[str(d)][2])
            print('Avg runtime:', statistics[str(d)][3])
            print('--------------------------')

    def solve(self, heuristic_func, verbosity=False):
        path, node_gen = self._a_star_search(heuristic_func)
        depth = len(path) - 1 if len(path) > 0 else 0

        if verbosity:
            print('---------------------')
            for state in path :
                Puzzle.pretty_print(state)
            print('Depth:', depth)
            print('Nodes generated:', node_gen)
            print('---------------------')
        
        return path, node_gen, depth

    @staticmethod
    def _solvable(state):
        count = 0
        for i in range(8):
            for j in range(i + 1, 9):
                if state[i] != '0' and state[j] != '0' and state[i] > state[j]:
                    count += 1
        return count % 2 == 0
    
    @staticmethod
    def _sum_misplaced_heuristic(state):
        sum_misplace = 0
        for i in range(9):
            if state[i] != str(i):
                sum_misplace += 1
        return sum_misplace

    @staticmethod
    def _manhattan_heuristic(state):
        sum = 0
        for  i in range(9):
            goal_row, goal_col = i // 3, i % 3
            cur_row, cur_col = int(state[i]) // 3, int(state[i]) % 3
            sum += (abs(cur_row - goal_row) + abs(cur_col - goal_col))
        return sum

    def _a_star_search(self, heuristic_func):
        if self.state == Puzzle.goal_state: 
            return [self.state], 0
        
        # heap of tuple(path_total_cost, path)
        # path_total_cost = path_cost + heuristic
        frontier = Frontier()
        frontier.push((heuristic_func(self.state), [self.state]))
        explored_list = []
        node_gen = 0
        
        while True:
            if frontier.empty():
                break
            
            # pop state with min cost from the frontier
            cur_path_total_cost, cur_path = frontier.pop()
            cur_state = cur_path[-1]
 
            # check lazy delete
            if cur_state in explored_list:
                continue
            
            # test goal condition
            if cur_state == Puzzle.goal_state:                
                return cur_path, node_gen
            
            # add current state to explored list
            explored_list.append(cur_state)
            
            # get all neighbours of current state in asc order
            neighbours = Puzzle._get_neighbours(cur_state)

            for neighbour in neighbours:
                if neighbour not in explored_list:
                    # new path to go to a neighbour
                    path_to_neighbour = cur_path.copy()
                    path_to_neighbour.append(neighbour)
    
                    # calc path_total_cost (include heuristic)
                    path_to_neighbour_total_cost = cur_path_total_cost - heuristic_func(cur_state) \
                                                    + 1 + heuristic_func(neighbour)
                    
                    node_gen += 1
                    
                    # if neighbour already in frontier or not
                    # -> use lazy delete
                    frontier.push((path_to_neighbour_total_cost, path_to_neighbour))

        return None, node_gen
     
    @staticmethod
    def _get_neighbours(state):
        neighbours = []
        d_row = [1, -1, 0, 0]  # format of [Up, Down, Right, Left]
        d_col = [0, 0, 1, -1]
        
        blank_row = blank_col = None
        for i in range (9):
            if state[i] == '0':
                blank_row, blank_col = int(i) // 3, int(i) % 3
                break

        for direction in range(4):
            new_row = blank_row + d_row[direction]
            new_col = blank_col + d_col[direction]

            if (0 <= new_row <= 2) and (0 <= new_col <= 2):
                new = new_row * 3 + new_col 
                blank = blank_row * 3 + blank_col
                
                new_state = deepcopy(state)

                l = list(new_state)
                l[new], l[blank] = l[blank], l[new]
                new_state = ''.join(l)

                neighbours.append(new_state)
                
        return neighbours

    @staticmethod
    def pretty_print(state):
        for i in range(3):
            for j in range(3):
                print(state[i * 3 + j], end=' ')
            print()
        print()